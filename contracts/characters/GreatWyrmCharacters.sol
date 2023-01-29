// SPDX-License-Identifier: MIT

/**
 * Authors: Moonstream Engineering (engineering@moonstream.to)
 * GitHub: https://github.com/great-wyrm/contracts
 */

pragma solidity ^0.8.0;

import {ERC721Base, IERC721} from "@solidstate/contracts/token/ERC721/base/ERC721Base.sol";
import {ERC721Enumerable, IERC721Enumerable} from "@solidstate/contracts/token/ERC721/enumerable/ERC721Enumerable.sol";
import {IERC721Metadata} from "@solidstate/contracts/token/ERC721/metadata/IERC721Metadata.sol";
import {LibDiamond} from "../diamond/libraries/LibDiamond.sol";
import {ITerminus} from "../interfaces/ITerminus.sol";

library LibCharacters {
    bytes32 constant CHARACTER_METADATA_STORAGE_POSITION =
        keccak256("great-wyrm.characters.metadata");


    struct CharactersStorage {
        address InventoryAddress;
        address AdminTerminusAddress;
        uint256 AdminTerminusPoolID;
        uint256 CharacterCreationTerminusPoolID;
        string ContractName;
        string ContractSymbol;
        // TokenID => string storing the token URI for each character
        mapping(uint256 => string) TokenURIs;
        // Token ID => bool describing whether or not the metadata for the character represented by that
        // token ID is licensed appopriately.
        mapping(uint256 => bool) MetadataInvalid;
    }

    function charactersStorage()
        internal
        pure
        returns (CharactersStorage storage cs)
    {
        bytes32 position = CHARACTER_METADATA_STORAGE_POSITION;
        assembly {
            cs.slot := position
        }
    }
}

/**
GreatWyrmCharacters contains all the characters in the universe of Great Wyrm.
 */
contract GreatWyrmCharacters is ERC721Base, ERC721Enumerable {
    event InventorySet(address inventoryAddress);
    event TokenURISet(uint256 indexed tokenId, address indexed changer, string uri);
    event TokenValiditySet(uint256 indexed tokenId, address indexed changer, bool valid);

    modifier onlyGameMaster() {
        LibCharacters.CharactersStorage storage cs = LibCharacters.charactersStorage();
        ITerminus adminTerminusContract = ITerminus(cs.AdminTerminusAddress);
        require(adminTerminusContract.balanceOf(msg.sender, cs.AdminTerminusPoolID) >= 1, "GreatWyrmCharacters.onlyGameMaster: Message sender is not a game master");
        _;
    }

    modifier onlyPlayerOf(uint256 tokenId) {
        require(msg.sender == _ownerOf(tokenId), "GreatWyrmCharacters.onlyPlayerOf: Message sender does not control the given character");
        _;
    }

    function supportsInterface(bytes4 interfaceId) external pure returns (bool) {
        return interfaceId == type(IERC721).interfaceId || interfaceId == type(IERC721Enumerable).interfaceId || interfaceId == type(IERC721Metadata).interfaceId;
    }

    function init(address adminTerminusAddress, uint256 adminTerminusPoolId, uint256 characterCreationTerminusPoolId, string calldata contractName, string calldata contractSymbol) external {
        LibDiamond.enforceIsContractOwner();

        LibCharacters.CharactersStorage storage cs = LibCharacters.charactersStorage();
        cs.AdminTerminusAddress = adminTerminusAddress;
        cs.AdminTerminusPoolID = adminTerminusPoolId;
        cs.CharacterCreationTerminusPoolID = characterCreationTerminusPoolId;
        cs.ContractName = contractName;
        cs.ContractSymbol = contractSymbol;

        LibDiamond.DiamondStorage storage ds = LibDiamond.diamondStorage();
        ds.supportedInterfaces[type(IERC721).interfaceId] = true;
        ds.supportedInterfaces[type(IERC721Enumerable).interfaceId] = true;
        ds.supportedInterfaces[type(IERC721Metadata).interfaceId] = true;
    }

    function setInventory(address inventoryAddress) external {
        LibDiamond.enforceIsContractOwner();

        LibCharacters.CharactersStorage storage cs = LibCharacters.charactersStorage();
        cs.InventoryAddress = inventoryAddress;

        emit InventorySet(inventoryAddress);
    }

    function name() external view returns (string memory) {
        return LibCharacters.charactersStorage().ContractName;
    }

    function symbol() external view returns (string memory) {
        return LibCharacters.charactersStorage().ContractSymbol;
    }

    function tokenURI(uint256 tokenId) external view returns (string memory) {
        return LibCharacters.charactersStorage().TokenURIs[tokenId];
    }

    function setTokenUri(uint256 tokenId, string calldata uri, bool isAppropriatelyLicensed) external onlyPlayerOf(tokenId) {
        require(isAppropriatelyLicensed, "GreatWyrmCharacters.setTokenUri: Please set the last parameter to this function to true, to certify that the content at that URI is appropriately licensed.");
        LibCharacters.CharactersStorage storage cs = LibCharacters.charactersStorage();
        cs.TokenURIs[tokenId] = uri;

        emit TokenURISet(tokenId, msg.sender, uri);
    }

    function isMetadataInvalid(uint256 tokenId) external view returns (bool) {
        return LibCharacters.charactersStorage().MetadataInvalid[tokenId];
    }

    function setMetadataValidity(uint256 tokenId, bool valid) external onlyGameMaster {
        LibCharacters.CharactersStorage storage cs = LibCharacters.charactersStorage();
        cs.MetadataInvalid[tokenId] = valid;
        emit TokenValiditySet(tokenId, msg.sender, valid);
    }

    function mint(address player) external returns (uint256) {
        LibCharacters.CharactersStorage storage cs = LibCharacters.charactersStorage();
        ITerminus adminTerminusContract = ITerminus(cs.AdminTerminusAddress);
        adminTerminusContract.burn(msg.sender, cs.CharacterCreationTerminusPoolID, 1);
        uint256 tokenId = _totalSupply() + 1;
        _mint(player, tokenId);
        return tokenId;
    }
}
