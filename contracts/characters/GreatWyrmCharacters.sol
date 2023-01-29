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
        keccak256("great-wyrm.characters.storage");

    struct CharactersStorage {
        address InventoryAddress;
        address AdminTerminusAddress;
        uint256 AdminTerminusPoolID;
        uint256 CharacterCreationTerminusPoolID;
        string ContractName;
        string ContractSymbol;
        string ContractURI;
        // TokenID => string storing the token URI for each character
        mapping(uint256 => string) TokenURIs;
        // Token ID => bool describing whether or not the metadata for the character represented by that
        // token ID is licensed appopriately.
        mapping(uint256 => bool) MetadataValid;
    }

    /**
    Loads the DELEGATECALL-compliant storage structure for LibCharacters.
     */
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
CharactersFacet contains all the characters in the universe of Great Wyrm.
 */
contract CharactersFacet is ERC721Base, ERC721Enumerable {
    /// InventorySet is fired every time the inventory address changes on the character contract.
    event InventorySet(address inventoryAddress);
    /// ContractInformationSet is fired every time the name, symbol, or contract metadata URI are
    /// changed on the character contract.
    event ContractInformationSet(string name, string symbol, string uri);
    /// TokenURISet is fired every time a player changes the metadata URI for one of their characters.
    event TokenURISet(
        uint256 indexed tokenId,
        address indexed changer,
        string uri
    );
    /// TokenValiditySet is fired every time a game master marks a token's metadata as valid or invalid.
    event TokenValiditySet(
        uint256 indexed tokenId,
        address indexed changer,
        bool valid
    );

    /// onlyGameMaster modifies functions that can only be called by game masters.
    modifier onlyGameMaster() {
        LibCharacters.CharactersStorage storage cs = LibCharacters
            .charactersStorage();
        ITerminus adminTerminusContract = ITerminus(cs.AdminTerminusAddress);
        require(
            adminTerminusContract.balanceOf(
                msg.sender,
                cs.AdminTerminusPoolID
            ) >= 1,
            "CharactersFacet.onlyGameMaster: Message sender is not a game master"
        );
        _;
    }

    /// onlyPlayerOf modifies functions that apply to a specific character and enforces that those functions
    /// are only being called by a sender which currently controls that character.
    modifier onlyPlayerOf(uint256 tokenId) {
        require(
            msg.sender == _ownerOf(tokenId),
            "CharactersFacet.onlyPlayerOf: Message sender does not control the given character"
        );
        _;
    }

    /// supportsInterface is implemented here for deployment of the characters contract as a standalone,
    /// immutable contract. In an EIP-2535 setup, this should be served via the DiamondLoupeFacet.
    function supportsInterface(bytes4 interfaceId)
        external
        pure
        returns (bool)
    {
        return
            interfaceId == type(IERC721).interfaceId ||
            interfaceId == type(IERC721Enumerable).interfaceId ||
            interfaceId == type(IERC721Metadata).interfaceId;
    }

    /// Initializes a character contract by specifying:
    /// 1. An address for a Terminus contract on which the access control badges will be defined.
    /// 2. The pool ID for the game master pool on the Terminus contract specified in (1).
    /// 3. The pool ID for the Terminus pool on the Terminus contract specified in (1) from which tokens are
    ///    required in order to create new Great Wyrm characters. This requirement helps ensure that
    ///    someone doesn't just create characters on an infinite loop and overpopulate the world.
    /// 4. A name for the contract.
    /// 5. A symbol for the contract.
    /// 6. A metadata URI for the contract.
    function init(
        address adminTerminusAddress,
        uint256 adminTerminusPoolId,
        uint256 characterCreationTerminusPoolId,
        string calldata contractName,
        string calldata contractSymbol,
        string calldata contractUri
    ) public {
        LibDiamond.enforceIsContractOwner();

        LibCharacters.CharactersStorage storage cs = LibCharacters
            .charactersStorage();
        cs.AdminTerminusAddress = adminTerminusAddress;
        cs.AdminTerminusPoolID = adminTerminusPoolId;
        cs.CharacterCreationTerminusPoolID = characterCreationTerminusPoolId;
        cs.ContractName = contractName;
        cs.ContractSymbol = contractSymbol;
        cs.ContractURI = contractUri;

        emit ContractInformationSet(
            cs.ContractName,
            cs.ContractSymbol,
            cs.ContractURI
        );

        LibDiamond.DiamondStorage storage ds = LibDiamond.diamondStorage();
        ds.supportedInterfaces[type(IERC721).interfaceId] = true;
        ds.supportedInterfaces[type(IERC721Enumerable).interfaceId] = true;
        ds.supportedInterfaces[type(IERC721Metadata).interfaceId] = true;
    }

    /// setInventory allows the owner of the character contract to set the address of the Inventory
    /// contract it uses.
    /// For more information about Inventory:
    /// 1. Source code: https://github.com/G7DAO/contracts/blob/cafd8ed8bfbb61d3eff3ce5b21da77063d2592df/contracts/inventory/Inventory.sol
    /// 2. Design document: https://docs.google.com/document/d/1Oa9I9b7t46_ngYp-Pady5XKEDW8M2NE9rI0GBRACZBI/edit?usp=sharing
    function setInventory(address inventoryAddress) external {
        LibDiamond.enforceIsContractOwner();

        LibCharacters.CharactersStorage storage cs = LibCharacters
            .charactersStorage();
        cs.InventoryAddress = inventoryAddress;

        emit InventorySet(inventoryAddress);
    }

    /// Returns the address of the Inventory contract (if any) that the character contract is using.
    function inventory() external view returns (address) {
        return LibCharacters.charactersStorage().InventoryAddress;
    }

    /// Allows contract owner to modify contract name, symbol, or metadata URI.
    function setContractInformation(
        string calldata contractName,
        string calldata contractSymbol,
        string calldata contractUri
    ) external {
        LibDiamond.enforceIsContractOwner();

        LibCharacters.CharactersStorage storage cs = LibCharacters
            .charactersStorage();
        cs.ContractName = contractName;
        cs.ContractSymbol = contractSymbol;
        cs.ContractURI = contractUri;

        emit ContractInformationSet(
            cs.ContractName,
            cs.ContractSymbol,
            cs.ContractURI
        );
    }

    /// Returns the contract name.
    function name() external view returns (string memory) {
        return LibCharacters.charactersStorage().ContractName;
    }

    /// Returns the contract symbol.
    function symbol() external view returns (string memory) {
        return LibCharacters.charactersStorage().ContractSymbol;
    }

    /// Returns the contract metadata URI.
    function contractURI() external view returns (string memory) {
        return LibCharacters.charactersStorage().ContractURI;
    }

    /// Returns the metadata URI for a given character (specified by tokenId). This metadata at this
    /// URI represents the character's profile in the Great Wyrm game.
    function tokenURI(uint256 tokenId) external view returns (string memory) {
        return LibCharacters.charactersStorage().TokenURIs[tokenId];
    }

    /// Allows a player to set the metadata URI for one of their characters.
    /// The `isAppropriatelyLicensed` argument is a certification from the player that the content at
    /// the metadata URI may be used by the Great Wyrm community under a CC0 license.
    function setTokenUri(
        uint256 tokenId,
        string calldata uri,
        bool isAppropriatelyLicensed
    ) external onlyPlayerOf(tokenId) {
        require(
            isAppropriatelyLicensed,
            "CharactersFacet.setTokenUri: Please set the last parameter to this function to true, to certify that the content at that URI is appropriately licensed."
        );
        LibCharacters.CharactersStorage storage cs = LibCharacters
            .charactersStorage();
        cs.TokenURIs[tokenId] = uri;
        cs.MetadataValid[tokenId] = false;

        emit TokenURISet(tokenId, msg.sender, uri);
        // We do not emit a TokenValiditySet event - that is reserved for Game Masters.
    }

    /// Checks if the metadata for a given character is valid according to the game masters of Great Wyrm.
    function isMetadataValid(uint256 tokenId) external view returns (bool) {
        return LibCharacters.charactersStorage().MetadataValid[tokenId];
    }

    /// Allows game masters to mark a character's metadata as being valid or invalid.
    function setMetadataValidity(uint256 tokenId, bool valid)
        external
        onlyGameMaster
    {
        LibCharacters.CharactersStorage storage cs = LibCharacters
            .charactersStorage();
        cs.MetadataValid[tokenId] = valid;
        emit TokenValiditySet(tokenId, msg.sender, valid);
    }

    /// Allows anyone possessing a character creation Terminus token to create a Greaty Wyrm character.
    /// The character creation Terminus token is used up in the process.
    function createCharacter(address player) external returns (uint256) {
        LibCharacters.CharactersStorage storage cs = LibCharacters
            .charactersStorage();
        ITerminus adminTerminusContract = ITerminus(cs.AdminTerminusAddress);
        adminTerminusContract.burn(
            msg.sender,
            cs.CharacterCreationTerminusPoolID,
            1
        );
        uint256 tokenId = _totalSupply() + 1;
        _mint(player, tokenId);
        return tokenId;
    }
}
