// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./ERC1155/IERC1155.sol";
import "./ERC1155/IERC1155Receiver.sol";
import "./ERC1155/extensions/IERC1155MetadataURI.sol";
import "./ERC1155/dependencies/Strings.sol";
import "./ERC1155/dependencies/Address.sol";
import "./ERC1155/dependencies/Context.sol";
import "./ERC1155/dependencies/ERC165.sol";

contract SFT is Context, ERC165, IERC1155, IERC1155MetadataURI {
    using Address for address;

    struct Secret {
        uint256 id;
        address creator;
        uint256 supply; // number of NFTs
        string metadata; // ipfs link
        uint256 metahash; // sha256 of secretId, creator, supply, and metadata
    }

    string private _uri;
    uint256 private _nbSecrets; // number of secrets
    mapping(uint256 => uint256) private _metahashsToIds; // metahash -> secretId
    mapping(uint256 => Secret) private _secrets; // secretId -> secret
    mapping(uint256 => mapping(uint256 => address)) private _holders; // secretId -> boxId -> owner
    mapping(uint256 => mapping(uint256 => bool)) private _revealed; // secretId -> boxId -> revealed
    mapping(uint256 => mapping(address => uint256)) private _balances; // secretId -> owner -> balance
    mapping(address => mapping(address => bool)) private _operatorApprovals; // owner -> operator -> approved

    event SecretMinted(
        uint256 indexed secretId,
        address indexed creator,
        uint256 amount,
        uint256 metahash
    );

    event SecretOpened(
        uint256 indexed secretId,
        address indexed from,
        uint256 boxId,
        uint256 metahash
    );

    constructor() {}

    function uri(uint256 id) public view override returns (string memory) {
        uint256 id_ = getAnyId(id);
        return _secrets[id_].metadata;
    }

    function supportsInterface(
        bytes4 interfaceId
    ) public view override(ERC165, IERC165) returns (bool) {
        return
            interfaceId == type(IERC1155).interfaceId ||
            interfaceId == type(IERC1155MetadataURI).interfaceId ||
            super.supportsInterface(interfaceId);
    }

    function getAnyId(uint256 id) public view returns (uint256) {
        uint256 id_ = _metahashsToIds[id];
        return id_ == 0 ? id : id_;
    }

    function balanceOf(
        address account,
        uint256 id
    ) public view override returns (uint256) {
        uint256 id_ = getAnyId(id);
        return _balances[id_][account];
    }

    function balanceOfBatch(
        address[] calldata accounts,
        uint256[] calldata ids
    ) public view override returns (uint256[] memory) {
        require(
            accounts.length == ids.length,
            "ERC1155: accounts and ids length mismatch"
        );
        uint256[] memory batchBalances = new uint256[](accounts.length);
        for (uint256 i = 0; i < accounts.length; i++) {
            batchBalances[i] = _balances[getAnyId(ids[i])][accounts[i]];
        }
        return batchBalances;
    }

    function setApprovalForAll(
        address operator,
        bool approved
    ) public override {
        _setApprovalForAll(_msgSender(), operator, approved);
    }

    function _setApprovalForAll(
        address owner,
        address operator,
        bool approved
    ) internal {
        require(owner != operator, "ERC1155: setting approval status for self");
        _operatorApprovals[owner][operator] = approved;
        emit ApprovalForAll(owner, operator, approved);
    }

    function isApprovedForAll(
        address account,
        address operator
    ) public view override returns (bool) {
        return _operatorApprovals[account][operator];
    }

    function safeTransferFrom(
        address from,
        address to,
        uint256 id,
        uint256 amount,
        bytes memory data
    ) public override {
        require(
            from == _msgSender() || isApprovedForAll(from, _msgSender()),
            "ERC1155: caller is not token owner nor approved"
        );
        _safeTransferFrom(from, to, id, amount, data);
        address operator = _msgSender();
        emit TransferSingle(operator, from, to, id, amount);
        _doSafeTransferAcceptanceCheck(operator, from, to, id, amount, data);
    }

    function _safeTransferFrom(
        address from,
        address to,
        uint256 id,
        uint256 amount,
        bytes memory data
    ) internal {
        require(to != address(0), "ERC1155: transfer to the zero address");
        uint256 id_ = getAnyId(id);
        require(
            _balances[id_][from] >= amount,
            "ERC1155: insufficient balance"
        );
        uint256 transfered = 0;
        for (uint256 i = 0; i < _secrets[id_].supply; i++) {
            if (_holders[id_][i] == from && !_revealed[id_][i]) {
                _holders[id_][i] = to;
                _balances[id_][from]--;
                _balances[id_][to]++;
                transfered++;
            }
            if (transfered == amount) break;
        }
        require(
            transfered == amount,
            "ERC1155: not enough sealed boxes for transfer"
        );
    }

    function safeBatchTransferFrom(
        address from,
        address to,
        uint256[] memory ids,
        uint256[] memory amounts,
        bytes memory data
    ) public override {
        require(
            from == _msgSender() || isApprovedForAll(from, _msgSender()),
            "ERC1155: caller is not token owner nor approved"
        );
        _safeBatchTransferFrom(from, to, ids, amounts, data);
        address operator = _msgSender();
        emit TransferBatch(operator, from, to, ids, amounts);
        _doSafeBatchTransferAcceptanceCheck(
            operator,
            from,
            to,
            ids,
            amounts,
            data
        );
    }

    function _safeBatchTransferFrom(
        address from,
        address to,
        uint256[] memory ids,
        uint256[] memory amounts,
        bytes memory data
    ) internal {
        require(
            ids.length == amounts.length,
            "ERC1155: ids and amounts length mismatch"
        );
        require(to != address(0), "ERC1155: transfer to the zero address");
        for (uint256 i = 0; i < ids.length; i++) {
            _safeTransferFrom(from, to, ids[i], amounts[i], data);
        }
    }

    function _doSafeTransferAcceptanceCheck(
        address operator,
        address from,
        address to,
        uint256 id,
        uint256 amount,
        bytes memory data
    ) private {
        if (to.isContract()) {
            try
                IERC1155Receiver(to).onERC1155Received(
                    operator,
                    from,
                    id,
                    amount,
                    data
                )
            returns (bytes4 response) {
                if (response != IERC1155Receiver.onERC1155Received.selector) {
                    revert("ERC1155: ERC1155Receiver rejected tokens");
                }
            } catch Error(string memory reason) {
                revert(reason);
            } catch {
                revert("ERC1155: transfer to non ERC1155Receiver implementer");
            }
        }
    }

    function _doSafeBatchTransferAcceptanceCheck(
        address operator,
        address from,
        address to,
        uint256[] memory ids,
        uint256[] memory amounts,
        bytes memory data
    ) private {
        if (to.isContract()) {
            try
                IERC1155Receiver(to).onERC1155BatchReceived(
                    operator,
                    from,
                    ids,
                    amounts,
                    data
                )
            returns (bytes4 response) {
                if (
                    response != IERC1155Receiver.onERC1155BatchReceived.selector
                ) {
                    revert("ERC1155: ERC1155Receiver rejected tokens");
                }
            } catch Error(string memory reason) {
                revert(reason);
            } catch {
                revert("ERC1155: transfer to non ERC1155Receiver implementer");
            }
        }
    }

    function mint(uint256 amount, string memory metadata) external {
        require(amount > 0, "ERC1155: amount must be positive");
        address creator = _msgSender();
        uint256 id = _nbSecrets;
        uint256 metahash = uint256(
            sha256(abi.encodePacked(id, creator, amount, metadata))
        );

        // Create Secret
        _metahashsToIds[metahash] = id;
        _secrets[id] = Secret(id, creator, amount, metadata, metahash);
        _balances[id][creator] = amount;
        for (uint256 i = 0; i < amount; i++) {
            _holders[id][i] = creator;
        }
        _nbSecrets++;
        _revealed[id][0] = true;
        emit SecretMinted(id, creator, amount, metahash);
    }

    function open(uint256 secretId, uint256 boxId) external {
        address sender = _msgSender();
        uint256 id_ = getAnyId(secretId);
        require(
            _holders[id_][boxId] == sender,
            "ERC1155: caller is not the holder"
        );
        require(!_revealed[id_][boxId], "ERC1155: box already opened");
        _revealed[id_][boxId] = true;
        emit SecretOpened(secretId, sender, boxId, _secrets[id_].metahash);
    }

    function isOpen(
        uint256 secretId,
        uint256 boxId
    ) public view returns (bool) {
        return _revealed[getAnyId(secretId)][boxId];
    }

    function getNbSecrets() public view returns (uint256) {
        return _nbSecrets;
    }

    function getIdFromMetahash(uint256 metahash) public view returns (uint256) {
        return _metahashsToIds[metahash];
    }

    function getSecret(uint256 secretId) public view returns (Secret memory) {
        return _secrets[getAnyId(secretId)];
    }

    function getHolder(
        uint256 secretId,
        uint256 boxId
    ) public view returns (address) {
        return _holders[getAnyId(secretId)][boxId];
    }
}
