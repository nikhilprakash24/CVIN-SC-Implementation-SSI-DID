// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title CVINVehicleERC725XY
 * @dev Full ERC-725 (X + Y) smart-account vehicle identity for the CVIN thesis.
 *
 *      ERC-725 combines two sub-standards into one owner-controlled smart
 *      account that acts as a self-sovereign, blockchain-native identity:
 *
 *        - ERC-725X (generic executor): execute(operationType, target, value,
 *          data) performs low-level CALL / CREATE / CREATE2 / STATICCALL /
 *          DELEGATECALL on behalf of the account, gated to the {owner}. This is
 *          what makes the identity a *proxy account* able to act on-chain.
 *
 *        - ERC-725Y (generic key/value data store): setData/getData and their
 *          batch variants map bytes32 data keys to arbitrary bytes values, the
 *          canonical way an ERC-725 identity carries verifiable attributes
 *          (here: the vehicle VIN, make, model and year).
 *
 *      Access model: a single {owner} (the vehicle's controlling key) may write
 *      data and execute operations. transferOwnership rotates that controlling
 *      key WITHOUT changing the identity (the account address is the stable
 *      DID/identifier), which is the ERC-725 notion of key rotation.
 *
 * ============================================================================
 * REPRESENTATIVE IMPLEMENTATION -- why self-contained (not erc725/smart-contracts)
 * ============================================================================
 * This is a clean, self-contained implementation of ERC-725X + ERC-725Y per
 * EIP-725, faithful to the reference contracts in the erc725/smart-contracts
 * npm package: identical public interface (execute / executeBatch, setData /
 * getData / setDataBatch / getDataBatch, owner / transferOwnership /
 * renounceOwnership), identical ERC-165 interface IDs (ERC725X = 0x7545acac,
 * ERC725Y = 0x629aa694) and identical event shapes (Executed, ContractCreated,
 * DataChanged, OwnershipTransferred) with the five canonical operation types.
 *
 * We do NOT inherit the erc725/smart-contracts reference contracts directly:
 * the vendored package (v7.0.0) pins OpenZeppelin Contracts ^4.9.3 and its
 * ERC725XCore calls the 3-argument `Address.verifyCallResult(bool,bytes,string)`
 * helper, which was REMOVED in OpenZeppelin 5.0 (this project uses OZ 5.0.2 --
 * only the 2-argument `verifyCallResult(bool,bytes)` remains). Inheriting it
 * would force a mixed OZ4/OZ5 compilation graph into an otherwise OZ-5 project.
 * Every other standard in this thesis (ERC-721/1155/4337/LSP8/...) is likewise
 * a self-contained representative implementation, so this contract follows the
 * same convention: spec-faithful behaviour and interface, no version conflict.
 *
 * Full EIP-725 semantics implemented here (nothing stubbed): all five operation
 * types perform the real low-level opcode and bubble up the callee's revert
 * data; ERC-725Y stores real bytes and emits DataChanged on every write.
 * ============================================================================
 */
contract CVINVehicleERC725XY {
    // ============ ERC-165 / ERC-725 interface IDs (match the erc725 reference) ============
    bytes4 internal constant _INTERFACEID_ERC165 = 0x01ffc9a7;
    bytes4 internal constant _INTERFACEID_ERC725X = 0x7545acac;
    bytes4 internal constant _INTERFACEID_ERC725Y = 0x629aa694;

    // ============ ERC-725X operation types ============
    uint256 public constant OPERATION_CALL = 0;
    uint256 public constant OPERATION_CREATE = 1;
    uint256 public constant OPERATION_CREATE2 = 2;
    uint256 public constant OPERATION_STATICCALL = 3;
    uint256 public constant OPERATION_DELEGATECALL = 4;

    // ============ Well-known CVIN vehicle attribute data keys ============
    /// @dev keccak256("cvin:vin")
    bytes32 public constant VIN_KEY = keccak256("cvin:vin");
    /// @dev keccak256("cvin:make")
    bytes32 public constant MAKE_KEY = keccak256("cvin:make");
    /// @dev keccak256("cvin:model")
    bytes32 public constant MODEL_KEY = keccak256("cvin:model");
    /// @dev keccak256("cvin:year")
    bytes32 public constant YEAR_KEY = keccak256("cvin:year");

    // ============ State ============
    address private _owner;

    /// @dev ERC-725Y store: bytes32 data key => bytes data value
    mapping(bytes32 => bytes) internal _store;

    // ============ Events (EIP-725 canonical shapes) ============
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    event Executed(
        uint256 indexed operationType,
        address indexed target,
        uint256 value,
        bytes4 indexed selector
    );

    event ContractCreated(
        uint256 indexed operationType,
        address indexed contractAddress,
        uint256 value,
        bytes32 indexed salt
    );

    event DataChanged(bytes32 indexed dataKey, bytes dataValue);

    // ============ Modifiers ============
    modifier onlyOwner() {
        require(msg.sender == _owner, "ERC725: caller is not the owner");
        _;
    }

    // ============ Constructor ============
    /**
     * @param initialOwner The controlling key (owner) of this vehicle identity account.
     */
    constructor(address initialOwner) payable {
        require(initialOwner != address(0), "ERC725: owner is the zero address");
        _owner = initialOwner;
        emit OwnershipTransferred(address(0), initialOwner);
    }

    /// @dev Allow the smart account to custody native tokens (proxy-account funding).
    receive() external payable {}

    // ============ Ownership (key rotation) ============
    function owner() public view returns (address) {
        return _owner;
    }

    /**
     * @notice Rotate the controlling key of this vehicle identity to `newOwner`.
     * @dev The account address (the identity) is unchanged; only the controller rotates.
     */
    function transferOwnership(address newOwner) public onlyOwner {
        require(newOwner != address(0), "ERC725: new owner is the zero address");
        emit OwnershipTransferred(_owner, newOwner);
        _owner = newOwner;
    }

    function renounceOwnership() public onlyOwner {
        emit OwnershipTransferred(_owner, address(0));
        _owner = address(0);
    }

    // ============ ERC-725Y: generic key/value data store ============
    function getData(bytes32 dataKey) public view returns (bytes memory dataValue) {
        return _store[dataKey];
    }

    function getDataBatch(bytes32[] memory dataKeys)
        public
        view
        returns (bytes[] memory dataValues)
    {
        dataValues = new bytes[](dataKeys.length);
        for (uint256 i = 0; i < dataKeys.length; ) {
            dataValues[i] = _store[dataKeys[i]];
            unchecked {
                ++i;
            }
        }
        return dataValues;
    }

    function setData(bytes32 dataKey, bytes memory dataValue) public payable onlyOwner {
        _setData(dataKey, dataValue);
    }

    function setDataBatch(bytes32[] memory dataKeys, bytes[] memory dataValues)
        public
        payable
        onlyOwner
    {
        require(dataKeys.length == dataValues.length, "ERC725Y: keys/values length mismatch");
        require(dataKeys.length != 0, "ERC725Y: empty arrays");
        for (uint256 i = 0; i < dataKeys.length; ) {
            _setData(dataKeys[i], dataValues[i]);
            unchecked {
                ++i;
            }
        }
    }

    function _setData(bytes32 dataKey, bytes memory dataValue) internal {
        _store[dataKey] = dataValue;
        emit DataChanged(dataKey, dataValue);
    }

    // ============ CVIN convenience: birth attributes ============
    /**
     * @notice Owner-gated convenience setter writing the vehicle's birth
     *         attributes (VIN, make, model, year) into the ERC-725Y store in a
     *         single transaction. Strings are stored as their UTF-8 bytes; the
     *         year is stored abi-encoded as a uint256.
     */
    function setVehicleBirthAttributes(
        string calldata vin,
        string calldata make,
        string calldata model,
        uint256 year
    ) external onlyOwner {
        _setData(VIN_KEY, bytes(vin));
        _setData(MAKE_KEY, bytes(make));
        _setData(MODEL_KEY, bytes(model));
        _setData(YEAR_KEY, abi.encode(year));
    }

    /// @notice Convenience view returning the stored VIN decoded as a string.
    function getVehicleVIN() external view returns (string memory) {
        return string(_store[VIN_KEY]);
    }

    // ============ ERC-725X: generic executor ============
    /**
     * @notice Execute a generic operation from this account (owner-gated).
     * @param operationType 0=CALL, 1=CREATE, 2=CREATE2, 3=STATICCALL, 4=DELEGATECALL
     * @param target       Address to interact with (must be address(0) for CREATE/CREATE2).
     * @param value        Native tokens (wei) to forward (must be 0 for STATICCALL/DELEGATECALL).
     * @param data         Calldata for the call, or creation bytecode (+salt for CREATE2).
     * @return result      Return data of the call, or the created contract address (packed).
     */
    function execute(
        uint256 operationType,
        address target,
        uint256 value,
        bytes memory data
    ) public payable onlyOwner returns (bytes memory) {
        return _execute(operationType, target, value, data);
    }

    /**
     * @notice Batch version of {execute}. All arrays must have equal, non-zero length.
     */
    function executeBatch(
        uint256[] memory operationsType,
        address[] memory targets,
        uint256[] memory values,
        bytes[] memory datas
    ) public payable onlyOwner returns (bytes[] memory) {
        require(
            operationsType.length == targets.length &&
                targets.length == values.length &&
                values.length == datas.length,
            "ERC725X: batch parameters length mismatch"
        );
        require(operationsType.length != 0, "ERC725X: empty batch");

        bytes[] memory results = new bytes[](operationsType.length);
        for (uint256 i = 0; i < operationsType.length; ) {
            results[i] = _execute(operationsType[i], targets[i], values[i], datas[i]);
            unchecked {
                ++i;
            }
        }
        return results;
    }

    function _execute(
        uint256 operationType,
        address target,
        uint256 value,
        bytes memory data
    ) internal returns (bytes memory) {
        if (operationType == OPERATION_CALL) {
            return _executeCall(target, value, data);
        }
        if (operationType == OPERATION_CREATE) {
            require(target == address(0), "ERC725X: CREATE requires empty recipient");
            return _deployCreate(value, data);
        }
        if (operationType == OPERATION_CREATE2) {
            require(target == address(0), "ERC725X: CREATE2 requires empty recipient");
            return _deployCreate2(value, data);
        }
        if (operationType == OPERATION_STATICCALL) {
            require(value == 0, "ERC725X: msg.value disallowed in STATICCALL");
            return _executeStaticCall(target, data);
        }
        if (operationType == OPERATION_DELEGATECALL) {
            require(value == 0, "ERC725X: msg.value disallowed in DELEGATECALL");
            return _executeDelegateCall(target, data);
        }
        revert("ERC725X: unknown operation type");
    }

    function _executeCall(
        address target,
        uint256 value,
        bytes memory data
    ) internal returns (bytes memory) {
        require(address(this).balance >= value, "ERC725X: insufficient balance for call");
        emit Executed(OPERATION_CALL, target, value, _selectorOf(data));
        (bool success, bytes memory returnData) = target.call{value: value}(data);
        return _verifyCallResult(success, returnData);
    }

    function _executeStaticCall(address target, bytes memory data)
        internal
        returns (bytes memory)
    {
        emit Executed(OPERATION_STATICCALL, target, 0, _selectorOf(data));
        (bool success, bytes memory returnData) = target.staticcall(data);
        return _verifyCallResult(success, returnData);
    }

    function _executeDelegateCall(address target, bytes memory data)
        internal
        returns (bytes memory)
    {
        emit Executed(OPERATION_DELEGATECALL, target, 0, _selectorOf(data));
        // solhint-disable-next-line avoid-low-level-calls
        (bool success, bytes memory returnData) = target.delegatecall(data);
        return _verifyCallResult(success, returnData);
    }

    function _deployCreate(uint256 value, bytes memory creationCode)
        internal
        returns (bytes memory)
    {
        require(address(this).balance >= value, "ERC725X: insufficient balance for create");
        require(creationCode.length != 0, "ERC725X: no contract bytecode provided");
        address contractAddress;
        // solhint-disable-next-line no-inline-assembly
        assembly {
            contractAddress := create(value, add(creationCode, 0x20), mload(creationCode))
        }
        require(contractAddress != address(0), "ERC725X: CREATE deployment failed");
        emit ContractCreated(OPERATION_CREATE, contractAddress, value, bytes32(0));
        return abi.encodePacked(contractAddress);
    }

    /**
     * @dev CREATE2 with the erc725 reference convention: the last 32 bytes of `data` are
     *      the salt, the preceding bytes are the contract creation bytecode.
     */
    function _deployCreate2(uint256 value, bytes memory data)
        internal
        returns (bytes memory)
    {
        require(address(this).balance >= value, "ERC725X: insufficient balance for create2");
        require(data.length > 32, "ERC725X: CREATE2 needs bytecode + salt");
        bytes32 salt;
        address contractAddress;
        // solhint-disable-next-line no-inline-assembly
        assembly {
            let len := mload(data)
            salt := mload(add(add(data, 0x20), sub(len, 32)))
            // temporarily shrink the byte array length to exclude the trailing salt
            mstore(data, sub(len, 32))
            contractAddress := create2(value, add(data, 0x20), mload(data), salt)
            // restore the original length
            mstore(data, len)
        }
        require(contractAddress != address(0), "ERC725X: CREATE2 deployment failed");
        emit ContractCreated(OPERATION_CREATE2, contractAddress, value, salt);
        return abi.encodePacked(contractAddress);
    }

    /// @dev Bubble up the callee's revert reason on failure; return data on success.
    function _verifyCallResult(bool success, bytes memory returnData)
        internal
        pure
        returns (bytes memory)
    {
        if (success) {
            return returnData;
        }
        if (returnData.length != 0) {
            // solhint-disable-next-line no-inline-assembly
            assembly {
                revert(add(returnData, 0x20), mload(returnData))
            }
        }
        revert("ERC725X: low-level call failed");
    }

    /// @dev First 4 bytes (function selector) of `data`, or 0x00000000 if shorter.
    function _selectorOf(bytes memory data) internal pure returns (bytes4 selector) {
        if (data.length >= 4) {
            // solhint-disable-next-line no-inline-assembly
            assembly {
                selector := mload(add(data, 0x20))
            }
        }
    }

    // ============ ERC-165 ============
    function supportsInterface(bytes4 interfaceId) public pure returns (bool) {
        return
            interfaceId == _INTERFACEID_ERC165 ||
            interfaceId == _INTERFACEID_ERC725X ||
            interfaceId == _INTERFACEID_ERC725Y;
    }
}
