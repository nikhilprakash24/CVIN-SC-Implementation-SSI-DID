// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title CVINVehicleAccount (ERC-4337 Account Abstraction — research implementation)
 * @notice A smart-contract account representing a connected-vehicle identity.
 *         Deploying this account IS the act of creating the vehicle identity:
 *         the contract address is the vehicle's stable on-chain identifier,
 *         while the signing key (owner) can be rotated or recovered without
 *         the identity/address ever changing — the headline identity property
 *         of ERC-4337 evaluated in this thesis.
 *
 * @dev SELF-CONTAINED MINIMAL ERC-4337 SETUP — SIMPLIFICATIONS vs the
 *      canonical v0.7 stack (npm account-abstraction/contracts), documented for
 *      the thesis security/gas analysis:
 *
 *      1. PackedUserOperation matches the v0.7 struct shape (sender, nonce,
 *         initCode, callData, accountGasLimits, preVerificationGas, gasFees,
 *         paymasterAndData, signature) but the gas-limit fields are carried
 *         only so the userOpHash matches the v0.7 hashing scheme — they are
 *         NOT enforced by the minimal entry point (no gas accounting).
 *      2. IAccount keeps the canonical validateUserOp(userOp, userOpHash,
 *         missingAccountFunds) signature, but the minimal entry point always
 *         passes missingAccountFunds = 0 (no deposit/prefund system). The
 *         prefund-payment branch is still implemented for shape-fidelity.
 *      3. Signature validation follows SimpleAccount v0.7: the owner signs
 *         the EIP-191 ("\x19Ethereum Signed Message:\n32") envelope of the
 *         userOpHash; validation returns 0 on success and 1
 *         (SIG_VALIDATION_FAILED) on failure instead of reverting, exactly
 *         like the canonical account. Time-range packing of validationData
 *         (validAfter/validUntil) is omitted.
 *      4. No initCode-based counterfactual deployment via an AccountFactory;
 *         the account is deployed directly (identity creation is measured as
 *         the constructor cost).
 *      5. No paymaster, no signature aggregation, no EIP-1271.
 *
 *      Identity features on top of the raw account:
 *      - setAttribute(bytes32,bytes): ERC-725Y-flavoured attribute store for
 *        vehicle metadata (VIN, make/model, firmware hash, ...), gated to
 *        owner-or-entryPoint, with an event for off-chain indexing.
 *      - transferOwnership: signing-key rotation (identity address unchanged).
 *      - setGuardian / recoverOwner: social-recovery mechanism — a designated
 *        guardian (e.g. manufacturer or fleet operator) can install a new
 *        signing key if the vehicle's key is lost or compromised. This is the
 *        recovery capability unique to contract accounts among the standards
 *        compared in the thesis.
 */

/// @dev ERC-4337 v0.7 `PackedUserOperation`: v0.7-shaped packed user operation (see simplification note 1 above).
///      Gas fields are hashed by CVINMinimalEntryPoint.getUserOpHash but not enforced.
struct PackedUserOperation {
    address sender;
    uint256 nonce;
    bytes initCode;
    bytes callData;
    bytes32 accountGasLimits; // packed verificationGasLimit | callGasLimit
    uint256 preVerificationGas;
    bytes32 gasFees; // packed maxPriorityFeePerGas | maxFeePerGas
    bytes paymasterAndData;
    bytes signature;
}

/// @title IAccount
/// @notice ERC-4337 account validation interface.
/// @dev Minimal ERC-4337 account interface (v0.7 shape).
/// @custom:standard ERC-4337 https://eips.ethereum.org/EIPS/eip-4337
interface IAccount {
    /// @notice Validates a user operation for the calling EntryPoint.
    /// @param userOp The packed user operation.
    /// @param userOpHash Hash of the op as computed by the EntryPoint.
    /// @param missingAccountFunds Prefund the account must pay to the EntryPoint.
    /// @return validationData 0 = valid, 1 = signature failure (time-range packing optional).
    function validateUserOp(
        PackedUserOperation calldata userOp,
        bytes32 userOpHash,
        uint256 missingAccountFunds
    ) external returns (uint256 validationData);
}

/**
 * @title CVINVehicleAccount
 * @author CVIN research project
 * @notice ERC-4337 smart-contract account representing a connected-vehicle identity;
 *         the address is the identifier, the owner key can be rotated or recovered.
 * @dev See the file header above for the full list of simplifications vs the canonical
 *      v0.7 stack (npm account-abstraction/contracts) and the CVIN identity features.
 *      Self-contained (no OpenZeppelin imports, though the project pins OZ 5.0.2).
 *      Signature check follows the SimpleAccount v0.7 pattern (EIP-191 over userOpHash).
 *      Omitted: validAfter/validUntil packing, factory/CREATE2 counterfactual deployment,
 *      paymaster, aggregation, ERC-1271.
 * @custom:standard ERC-4337 (Account Abstraction, v0.7 shapes) https://eips.ethereum.org/EIPS/eip-4337
 * @custom:standard EIP-191 (signed data) https://eips.ethereum.org/EIPS/eip-191
 * @custom:security A single guardian can take over the account immediately via {recoverOwner}:
 *                  no timelock, threshold or owner veto.
 * @custom:security No EIP-2 low-s check and no v normalisation in {_validateSignature}; harmless here
 *                  because replay protection is the EntryPoint nonce.
 * @custom:see docs/smart-contracts/04-account-claim-identity-erc725-735-4337-combined.md (section 4a)
 * @custom:see sandbox/options/erc-4337/adapter.js
 */
contract CVINVehicleAccount is IAccount {
    // ============ Constants ============

    /// @dev Canonical ERC-4337 return value for a failed signature check.
    uint256 internal constant SIG_VALIDATION_FAILED = 1;
    /// @dev Canonical ERC-4337 return value for a successful signature check.
    uint256 internal constant SIG_VALIDATION_SUCCESS = 0;

    // ============ State ============

    /// @notice Current signing key controlling this vehicle identity.
    address public owner;

    /// @notice Trusted entry point allowed to relay validated user operations.
    address public immutable entryPoint;

    /// @notice Social-recovery guardian (e.g. manufacturer / fleet operator).
    address public guardian;

    /// @dev Vehicle metadata store (ERC-725Y-flavoured key/value).
    mapping(bytes32 => bytes) private _attributes;

    // ============ Events ============

    /// @notice Emitted once at construction (identity creation).
    /// @param account This account's address.
    /// @param owner Initial signing key.
    /// @param entryPoint Trusted EntryPoint.
    event VehicleAccountCreated(address indexed account, address indexed owner, address indexed entryPoint);
    /// @notice Emitted on signing-key rotation via {transferOwnership}.
    /// @param previousOwner Previous key.
    /// @param newOwner New key.
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
    /// @notice Emitted when the guardian is set or cleared.
    /// @param previousGuardian Previous guardian.
    /// @param newGuardian New guardian (zero = cleared).
    event GuardianChanged(address indexed previousGuardian, address indexed newGuardian);
    /// @notice Emitted when the guardian installs a new owner via {recoverOwner}.
    /// @param guardian The guardian that performed recovery.
    /// @param previousOwner Replaced key.
    /// @param newOwner Installed key.
    event OwnerRecovered(address indexed guardian, address indexed previousOwner, address indexed newOwner);
    /// @notice Emitted on every attribute write.
    /// @param key Attribute key.
    /// @param value New value.
    event AttributeChanged(bytes32 indexed key, bytes value);
    /// @notice Emitted after a successful {execute} call.
    /// @param target Called address.
    /// @param value Wei forwarded.
    /// @param data Calldata.
    event Executed(address indexed target, uint256 value, bytes data);

    // ============ Modifiers ============

    /**
     * @dev Gates state-changing identity functions to: the owner key (direct
     *      call), the entry point (validated 4337 path), or the account
     *      itself (self-call via execute(), the canonical way a UserOperation
     *      reaches an account's admin functions).
     */
    modifier onlyOwnerOrEntryPoint() {
        require(
            msg.sender == owner || msg.sender == entryPoint || msg.sender == address(this),
            "CVINVehicleAccount: not owner or entryPoint"
        );
        _;
    }

    // ============ Constructor (identity creation) ============

    /// @notice Creates the vehicle identity (deployment = identity creation; no factory).
    /// @dev Both arguments must be non-zero. Emits {VehicleAccountCreated}.
    /// @param _entryPoint Trusted EntryPoint (immutable).
    /// @param _owner Initial signing key.
    constructor(address _entryPoint, address _owner) {
        require(_entryPoint != address(0), "CVINVehicleAccount: zero entryPoint");
        require(_owner != address(0), "CVINVehicleAccount: zero owner");
        entryPoint = _entryPoint;
        owner = _owner;
        emit VehicleAccountCreated(address(this), _owner, _entryPoint);
    }

    /// @notice Accepts native tokens (e.g. to fund EntryPoint prefunds).
    receive() external payable {}

    // ============ ERC-4337 validation ============

    /**
     * @notice Validate a user operation's signature (called by the entry point).
     * @dev The owner signs the EIP-191 envelope of userOpHash. Returns 0 on
     *      success, 1 on signature failure (does not revert), per ERC-4337.
     *      EntryPoint only. Pays `missingAccountFunds` to the caller when > 0
     *      (failure ignored); CVINMinimalEntryPoint always passes 0.
     * @param userOp The packed user operation (only `signature` is read).
     * @param userOpHash Hash the owner signed (EIP-191 envelope applied here).
     * @param missingAccountFunds Prefund owed to the EntryPoint.
     * @return validationData SIG_VALIDATION_SUCCESS (0) or SIG_VALIDATION_FAILED (1).
     */
    function validateUserOp(
        PackedUserOperation calldata userOp,
        bytes32 userOpHash,
        uint256 missingAccountFunds
    ) external override returns (uint256 validationData) {
        require(msg.sender == entryPoint, "CVINVehicleAccount: not entryPoint");

        validationData = _validateSignature(userOp.signature, userOpHash);

        // Shape-fidelity prefund branch (minimal entry point always passes 0).
        if (missingAccountFunds > 0) {
            (bool ok, ) = payable(msg.sender).call{value: missingAccountFunds}("");
            (ok); // ignore failure, per canonical account behaviour
        }
    }

    /// @dev Recovers the EIP-191 signer of `userOpHash` and compares it with {owner}.
    ///      Returns failure (not revert) for a non-65-byte signature or a zero/mismatched signer.
    ///      No low-s check, no v normalisation.
    /// @param signature 65-byte r||s||v signature.
    /// @param userOpHash The user operation hash.
    /// @return SIG_VALIDATION_SUCCESS or SIG_VALIDATION_FAILED.
    function _validateSignature(
        bytes calldata signature,
        bytes32 userOpHash
    ) internal view returns (uint256) {
        if (signature.length != 65) {
            return SIG_VALIDATION_FAILED;
        }
        // EIP-191 personal-sign envelope over the userOpHash (SimpleAccount pattern).
        bytes32 digest = keccak256(
            abi.encodePacked("\x19Ethereum Signed Message:\n32", userOpHash)
        );
        (bytes32 r, bytes32 s, uint8 v) = _splitSignature(signature);
        address recovered = ecrecover(digest, v, r, s);
        if (recovered == address(0) || recovered != owner) {
            return SIG_VALIDATION_FAILED;
        }
        return SIG_VALIDATION_SUCCESS;
    }

    /// @dev Splits a 65-byte signature into r, s, v (calldata slices).
    /// @param signature The signature.
    /// @return r First 32 bytes.
    /// @return s Second 32 bytes.
    /// @return v Final byte.
    function _splitSignature(
        bytes calldata signature
    ) internal pure returns (bytes32 r, bytes32 s, uint8 v) {
        r = bytes32(signature[0:32]);
        s = bytes32(signature[32:64]);
        v = uint8(signature[64]);
    }

    // ============ Execution ============

    /**
     * @notice Execute an arbitrary call from this vehicle identity.
     * @dev Callable by the owner key directly, or by the entry point after
     *      validateUserOp succeeded (the 4337 path), or by the account itself.
     *      Bubbles up the callee revert. Emits {Executed}. SimpleAccount pattern.
     * @param target Address to call.
     * @param value Wei to forward.
     * @param data Calldata.
     * @return result Callee return data.
     */
    function execute(
        address target,
        uint256 value,
        bytes calldata data
    ) external onlyOwnerOrEntryPoint returns (bytes memory result) {
        (bool success, bytes memory ret) = target.call{value: value}(data);
        if (!success) {
            // bubble up revert reason
            assembly {
                revert(add(ret, 32), mload(ret))
            }
        }
        emit Executed(target, value, data);
        return ret;
    }

    // ============ Key rotation ============

    /**
     * @notice Rotate the signing key. The vehicle identity (this address)
     *         is unchanged — only the controlling key moves.
     * @dev CVIN extension. Owner / EntryPoint / self. Non-zero. Emits {OwnershipTransferred}.
     * @param newOwner The new signing key.
     */
    function transferOwnership(address newOwner) external onlyOwnerOrEntryPoint {
        require(newOwner != address(0), "CVINVehicleAccount: zero owner");
        address previous = owner;
        owner = newOwner;
        emit OwnershipTransferred(previous, newOwner);
    }

    // ============ Social recovery ============

    /// @notice Designate (or clear, with address(0)) the recovery guardian.
    /// @dev CVIN extension (social recovery). Owner / EntryPoint / self. Emits {GuardianChanged}.
    /// @param newGuardian The guardian, or address(0) to clear.
    function setGuardian(address newGuardian) external onlyOwnerOrEntryPoint {
        address previous = guardian;
        guardian = newGuardian;
        emit GuardianChanged(previous, newGuardian);
    }

    /**
     * @notice Guardian-driven recovery: installs a new signing key when the
     *         vehicle's key is lost or compromised.
     * @dev CVIN extension. Guardian only; takes effect immediately (no timelock/veto).
     *      Non-zero. Emits {OwnerRecovered}.
     * @param newOwner The new signing key.
     */
    function recoverOwner(address newOwner) external {
        require(msg.sender == guardian, "CVINVehicleAccount: not guardian");
        require(newOwner != address(0), "CVINVehicleAccount: zero owner");
        address previous = owner;
        owner = newOwner;
        emit OwnerRecovered(msg.sender, previous, newOwner);
    }

    // ============ Vehicle attribute store ============

    /// @notice Set a vehicle metadata attribute (VIN, make, firmware hash, ...).
    /// @dev CVIN extension (ERC-725Y-flavoured). Owner / EntryPoint / self. Emits {AttributeChanged}.
    /// @param key Attribute key (the sandbox adapter uses keccak256 of a name).
    /// @param value Attribute value.
    function setAttribute(bytes32 key, bytes calldata value) external onlyOwnerOrEntryPoint {
        _attributes[key] = value;
        emit AttributeChanged(key, value);
    }

    /// @notice Read a vehicle metadata attribute.
    /// @dev CVIN extension.
    /// @param key Attribute key.
    /// @return The stored value (empty if unset).
    function getAttribute(bytes32 key) external view returns (bytes memory) {
        return _attributes[key];
    }
}
