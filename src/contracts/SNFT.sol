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
    mapping(address => mapping(address => bool)) private _operatorApprovals;

    struct SecretBox {
        uint256 id;
        address owner;
        bool revealed;
    }

    struct SecretHolder {
        uint256 balance;
        mapping(uint256 => SecretBox) boxes;
    }

    struct Secret {
        uint256 id;
        address creator;
        uint256 supply; // number of NFTs
        uint256 metahash; // sha256 of secretId, creator, supply, and metadata
        mapping(uint256 => SecretBox) boxes; // map of NFT ids to boxes
        mapping(address => SecretHolder) holders; // map of NFT holders
    }

    mapping(uint256 => uint256) private _metahashs; // metahash to secretId
    mapping(uint256 => Secret) private _secrets; // secretId to secret
    uint256 private _numSecrets; // numbers of secrets
    string private _uri;

    constructor(string memory uri_) {
        _setURI(uri_);
    }

    function uri(uint256) public view override returns (string memory) {
        return _uri;
    }

    function _setURI(string memory newuri) internal {
        _uri = newuri;
    }

    function supportsInterface(
        bytes4 interfaceId
    ) public view override(ERC165, IERC165) returns (bool) {
        return
            interfaceId == type(IERC1155).interfaceId ||
            interfaceId == type(IERC1155MetadataURI).interfaceId ||
            super.supportsInterface(interfaceId);
    }

    function balanceOf(
        address account,
        uint256 id
    ) public view override returns (uint256) {
        uint256 id_;
        return _secrets[_metahashs(id) || id].holders[account].balance;
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
            batchBalances[i] = _secrets[_metahashs(ids[i]) || ids[i]]
                .holders[accounts[i]]
                .balance;
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
    }

    function _safeTransferFrom(
        address from,
        address to,
        uint256 id,
        uint256 amount,
        bytes memory data
    ) internal {
        require(to != address(0), "ERC1155: transfer to the zero address");
        address operator = _msgSender();
        Secret memory secret = _secrets[_metahashs[id] || id];
        SecretHolder memory fromHolder = secret.holders[from];
        if (secret.holders[to].balance == 0) {
            secret.holders[to] = SecretHolder(
                0,
                new mapping(uint256 => SecretBox)()
            );
        }
        SecretHolder memory toHolder = secret.holders[to];
        uint256 fromBalance = fromHolder.balance;
        require(
            fromBalance >= amount,
            "ERC1155: insufficient balance for transfer"
        );

        uint256 transferedBoxes = 0;
        for (uint256 i = fromBalance - 1; i >= 0; i--) {
            SecretBox memory box = fromHolder.boxes[i];
            if (box.revealed == false) {
                box.owner = to;
                fromHolder.balance -= 1;
                fromHolder.boxes[i] = 0;
                toHolder.boxes[toHolder.balance] = box;
                toHolder.balance += 1;
                transferedBoxes++;
            }
        }
        require(
            transferedBoxes == amount,
            "ERC1155: not enough sealed boxes for transfer"
        );
        if (fromHolder.balance == 0) {
            delete secret.holders[from];
        }
        emit TransferSingle(operator, from, to, id, amount);
        _doSafeTransferAcceptanceCheck(operator, from, to, id, amount, data);
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
        address operator = _msgSender();
        for (uint256 i = 0; i < ids.length; i++) {
            safeTransferFrom(from, to, ids[i], amounts[i], data);
        }
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

    function mint(
        address to,
        uint256 id,
        uint256 amount,
        bytes memory data
    ) internal virtual {
        require(to != address(0), "ERC1155: mint to the zero address");
        require(to == _msgSender(), "ERC1155: only msg.sender can mint");
        require(amount > 0, "ERC1155: amount must be positive");

        // TODO

        emit TransferSingle(to, address(0), to, id, amount);
        _doSafeTransferAcceptanceCheck(to, address(0), to, id, amount, data);
    }
}
