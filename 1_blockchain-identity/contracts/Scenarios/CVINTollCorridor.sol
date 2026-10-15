// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/utils/cryptography/EIP712.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/IERC20Permit.sol";

interface IDIDRegistry1056 {
    function identityOwner(address identity) external view returns (address);
    function validDelegate(address identity, bytes32 delegateType, address delegate) external view returns (bool);
}

/**
 * @title CVINTollCorridor
 * @notice Scenario X1 ("endorsed passage, paid write"). One contract that composes
 *         the primitives the thesis measures separately:
 *
 *   READ  (gate)  An official authority's trusted issuer signs an EIP-712
 *                 Endorsement for a vehicle DID (did:ethr address) and a vehicle
 *                 class. `credentialHash` binds it to the off-chain W3C VC the
 *                 roadside unit verified. `checkTicket` is the on-chain read.
 *   WRITE (toll)  The vehicle signs an EIP-712 TollTicket with its DID owner key
 *                 or with any live ERC-1056 `veriKey` delegate (a rotating
 *                 pseudonym, register #38). The gantry relays it; the fee for the
 *                 endorsed class is debited from a stablecoin escrow that the
 *                 vehicle funded with an EIP-2612 permit (no ETH needed by the car).
 *
 * Revocation is per endorsement digest (a one-bit status list). Replay is
 * blocked per (identity, nonce). Events carry the DID address and digests only;
 * no VIN or plate ever reaches the chain.
 *
 * Research scaffolding: no upgradeability, single authority, no dispute window.
 */
contract CVINTollCorridor is EIP712 {
    using SafeERC20 for IERC20;

    struct Endorsement {
        address subject;          // vehicle DID (did:ethr:<subject>)
        uint8 vehicleClass;       // e.g. 0 emergency, 1 car, 2 EV, 3 truck
        uint64 validUntil;        // unix seconds
        bytes32 credentialHash;   // digest of the off-chain W3C VC
    }

    struct TollTicket {
        address identity;         // same DID as the endorsement subject
        address gantry;           // the RSU that may submit this ticket
        uint64 nonce;             // one-time, per identity
        uint128 maxFee;           // vehicle-side price cap
        uint64 deadline;          // ticket expiry
        bytes32 endorsementHash;  // EIP-712 digest of the endorsement presented
    }

    bytes32 public constant ENDORSEMENT_TYPEHASH =
        keccak256("Endorsement(address subject,uint8 vehicleClass,uint64 validUntil,bytes32 credentialHash)");
    bytes32 public constant TICKET_TYPEHASH =
        keccak256("TollTicket(address identity,address gantry,uint64 nonce,uint128 maxFee,uint64 deadline,bytes32 endorsementHash)");
    bytes32 public constant VERIKEY = "veriKey";

    // Reason codes returned by checkTicket (0 = OK).
    uint8 public constant OK = 0;
    uint8 public constant E_GANTRY = 1;
    uint8 public constant E_EXPIRED_TICKET = 2;
    uint8 public constant E_NONCE_USED = 3;
    uint8 public constant E_ENDORSEMENT_MISMATCH = 4;
    uint8 public constant E_UNTRUSTED_ISSUER = 5;
    uint8 public constant E_ENDORSEMENT_EXPIRED = 6;
    uint8 public constant E_ENDORSEMENT_REVOKED = 7;
    uint8 public constant E_SUBJECT_MISMATCH = 8;
    uint8 public constant E_UNKNOWN_CLASS = 9;
    uint8 public constant E_BAD_VEHICLE_SIGNER = 10;
    uint8 public constant E_FEE_ABOVE_MAX = 11;
    uint8 public constant E_INSUFFICIENT_ESCROW = 12;

    address public immutable authority;
    IERC20 public immutable token;
    IDIDRegistry1056 public immutable registry;

    mapping(address => bool) public trustedIssuer;
    mapping(address => bool) public isGantry;
    mapping(uint8 => uint128) public feeOf;
    mapping(uint8 => bool) public classEnabled;
    mapping(bytes32 => bool) public endorsementRevoked;
    mapping(address => uint256) public escrowOf;
    mapping(address => mapping(uint64 => bool)) public nonceUsed;
    uint256 public treasury;

    event IssuerSet(address indexed issuer, bool trusted);
    event GantrySet(address indexed gantry, bool enabled);
    event FeeSet(uint8 indexed vehicleClass, uint128 fee);
    event EndorsementRevoked(bytes32 indexed endorsementHash);
    event Deposited(address indexed identity, address indexed payer, uint256 amount);
    event Withdrawn(address indexed identity, address indexed to, uint256 amount);
    event TollPaid(address indexed identity, address indexed gantry, uint8 vehicleClass, uint256 fee, bytes32 ticketHash);
    event TreasurySwept(address indexed to, uint256 amount);

    error NotAuthority();
    error NotIdentityOwner();
    error TicketRejected(uint8 code);

    modifier onlyAuthority() {
        if (msg.sender != authority) revert NotAuthority();
        _;
    }

    constructor(address token_, address registry_) EIP712("CVINTollCorridor", "1") {
        authority = msg.sender;
        token = IERC20(token_);
        registry = IDIDRegistry1056(registry_);
    }

    // ---------------------------------------------------------------- admin

    function setIssuer(address issuer, bool trusted) external onlyAuthority {
        trustedIssuer[issuer] = trusted;
        emit IssuerSet(issuer, trusted);
    }

    function setGantry(address gantry, bool enabled) external onlyAuthority {
        isGantry[gantry] = enabled;
        emit GantrySet(gantry, enabled);
    }

    function setFee(uint8 vehicleClass, uint128 fee) external onlyAuthority {
        feeOf[vehicleClass] = fee;
        classEnabled[vehicleClass] = true;
        emit FeeSet(vehicleClass, fee);
    }

    /// @notice Authority or the endorsement's own issuer may revoke it.
    function revokeEndorsement(Endorsement calldata e, bytes calldata issuerSig) external {
        bytes32 eh = hashEndorsement(e);
        if (msg.sender != authority) {
            if (ECDSA.recover(eh, issuerSig) != msg.sender || !trustedIssuer[msg.sender]) revert NotAuthority();
        }
        endorsementRevoked[eh] = true;
        emit EndorsementRevoked(eh);
    }

    function sweep(address to) external onlyAuthority {
        uint256 amount = treasury;
        treasury = 0;
        token.safeTransfer(to, amount);
        emit TreasurySwept(to, amount);
    }

    // --------------------------------------------------------------- escrow

    function deposit(address identity, uint256 amount) external {
        token.safeTransferFrom(msg.sender, address(this), amount);
        escrowOf[identity] += amount;
        emit Deposited(identity, msg.sender, amount);
    }

    /// @notice Gasless top-up: anyone (e.g. the gantry) relays the payer's EIP-2612 permit.
    function depositWithPermit(
        address payer, address identity, uint256 amount, uint256 deadline, uint8 v, bytes32 r, bytes32 s
    ) external {
        // A front-run permit leaves the allowance in place, so tolerate a failure here.
        try IERC20Permit(address(token)).permit(payer, address(this), amount, deadline, v, r, s) {} catch {}
        token.safeTransferFrom(payer, address(this), amount);
        escrowOf[identity] += amount;
        emit Deposited(identity, payer, amount);
    }

    function withdraw(address identity, uint256 amount, address to) external {
        if (msg.sender != registry.identityOwner(identity)) revert NotIdentityOwner();
        escrowOf[identity] -= amount;
        token.safeTransfer(to, amount);
        emit Withdrawn(identity, to, amount);
    }

    // -------------------------------------------------------------- hashing

    function hashEndorsement(Endorsement calldata e) public view returns (bytes32) {
        return _hashTypedDataV4(keccak256(abi.encode(
            ENDORSEMENT_TYPEHASH, e.subject, e.vehicleClass, e.validUntil, e.credentialHash)));
    }

    function hashTicket(TollTicket calldata t) public view returns (bytes32) {
        return _hashTypedDataV4(keccak256(abi.encode(
            TICKET_TYPEHASH, t.identity, t.gantry, t.nonce, t.maxFee, t.deadline, t.endorsementHash)));
    }

    function domainSeparator() external view returns (bytes32) {
        return _domainSeparatorV4();
    }

    // ------------------------------------------------------------ read path

    /// @notice The gate's on-chain read: would this ticket settle if `gantry` submitted it now?
    function checkTicket(
        Endorsement calldata e, bytes calldata issuerSig, TollTicket calldata t, bytes calldata vehicleSig, address gantry
    ) public view returns (uint8 code, uint256 fee, bytes32 ticketHash) {
        ticketHash = hashTicket(t);
        if (!isGantry[gantry] || t.gantry != gantry) return (E_GANTRY, 0, ticketHash);
        if (block.timestamp > t.deadline) return (E_EXPIRED_TICKET, 0, ticketHash);
        if (nonceUsed[t.identity][t.nonce]) return (E_NONCE_USED, 0, ticketHash);

        bytes32 eh = hashEndorsement(e);
        if (t.endorsementHash != eh) return (E_ENDORSEMENT_MISMATCH, 0, ticketHash);
        (address issuer, ECDSA.RecoverError ierr,) = ECDSA.tryRecover(eh, issuerSig);
        if (ierr != ECDSA.RecoverError.NoError || !trustedIssuer[issuer]) return (E_UNTRUSTED_ISSUER, 0, ticketHash);
        if (block.timestamp > e.validUntil) return (E_ENDORSEMENT_EXPIRED, 0, ticketHash);
        if (endorsementRevoked[eh]) return (E_ENDORSEMENT_REVOKED, 0, ticketHash);
        if (e.subject != t.identity) return (E_SUBJECT_MISMATCH, 0, ticketHash);
        if (!classEnabled[e.vehicleClass]) return (E_UNKNOWN_CLASS, 0, ticketHash);

        (address signer, ECDSA.RecoverError verr,) = ECDSA.tryRecover(ticketHash, vehicleSig);
        if (verr != ECDSA.RecoverError.NoError) return (E_BAD_VEHICLE_SIGNER, 0, ticketHash);
        if (signer != registry.identityOwner(t.identity) && !registry.validDelegate(t.identity, VERIKEY, signer)) {
            return (E_BAD_VEHICLE_SIGNER, 0, ticketHash);
        }

        fee = feeOf[e.vehicleClass];
        if (fee > t.maxFee) return (E_FEE_ABOVE_MAX, fee, ticketHash);
        if (escrowOf[t.identity] < fee) return (E_INSUFFICIENT_ESCROW, fee, ticketHash);
        return (OK, fee, ticketHash);
    }

    // ----------------------------------------------------------- write path

    function payToll(
        Endorsement calldata e, bytes calldata issuerSig, TollTicket calldata t, bytes calldata vehicleSig
    ) external returns (uint256 fee) {
        return _settle(e, issuerSig, t, vehicleSig);
    }

    /// @notice All-or-nothing batch: a gantry pre-screens with checkTicket, then settles.
    function settleBatch(
        Endorsement[] calldata es, bytes[] calldata issuerSigs, TollTicket[] calldata ts, bytes[] calldata vehicleSigs
    ) external returns (uint256 total) {
        uint256 n = ts.length;
        require(es.length == n && issuerSigs.length == n && vehicleSigs.length == n, "length mismatch");
        for (uint256 i = 0; i < n; ++i) {
            total += _settle(es[i], issuerSigs[i], ts[i], vehicleSigs[i]);
        }
    }

    function _settle(
        Endorsement calldata e, bytes calldata issuerSig, TollTicket calldata t, bytes calldata vehicleSig
    ) internal returns (uint256 fee) {
        uint8 code;
        bytes32 th;
        (code, fee, th) = checkTicket(e, issuerSig, t, vehicleSig, msg.sender);
        if (code != OK) revert TicketRejected(code);
        nonceUsed[t.identity][t.nonce] = true;
        escrowOf[t.identity] -= fee;
        treasury += fee;
        emit TollPaid(t.identity, msg.sender, e.vehicleClass, fee, th);
    }
}
