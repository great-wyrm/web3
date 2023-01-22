# Characters in Great Wyrm

Great Wyrm characters are represented by tokens on an [ERC721](https://eips.ethereum.org/EIPS/eip-721)
smart contract.

While it does conform to the standard, the Great Wyrm character contract breaks from conventional ERC721
implementations in a few ways.

This document elaborates on how the Great Wyrm characters are implemented.

## The authority to change token metadata

The Great Wyrm character contract implements the metadata extension to ERC721.

Conventionally, it is the administrator of the ERC721 contract who has the authority to set metadata
URIs for the tokens on an ERC721 contract.

In the Great Wyrm character contract, the owner of a token is the only party allowed to set the metadata
URI for that token.

A token's owner may elect to include offensive content in its metadata. For moderation purposes, the
Great Wyrm ERC721 contract also allows moderators (accounts possessing a specific [Terminus](https://docs.moonstream.to/terminus/))
badge to flag and unflag tokens for offensive content. The state of a token being flagged or unflagged
will be readable from a separate view method on the contract (TODO(zomglings): `isFlagged`?).

## Inventory

Great Wyrm will make extensive use of the [Inventory](https://github.com/G7DAO/contracts/blob/a74ba464c81125956c4014eb0cd4051980988b9b/contracts/inventory/Inventory.sol)
contract developed by [Game7 DAO](https://game7.io) and [Moonstream DAO](https://moonstream.to). This
will allow Great Wyrm characters to take ownership of items in the game world as opposed to ownership
defaulting to the players. Great Wyrm will also use the inventory system to denote the era in which
characters are active, their health, their skills, and their achievements.

For more information about the Inventory contract, its purpose, and its uses, read the design document:
[*An Inventory system for web3 games*](https://docs.google.com/document/d/1Oa9I9b7t46_ngYp-Pady5XKEDW8M2NE9rI0GBRACZBI/edit?usp=sharing).

The Great Wyrm character contract will contain a reference to the inventory contract that it is being
used with (TODO(zomglings): `inventoryAddress`?).

## Upgradability using the EIP-2535 Diamond standard

The Great Wyrm character contract will be implemented as an [EIP-2535 Diamond proxy contract](https://eips.ethereum.org/EIPS/eip-2535).

Although this does mean that the contract deployer will have total authority over the state of the contract,
this implementation will allow the contract to evolve as more features and mechanics are added into Great
Wyrm without requiring tedious cross-contract migrations.

The authority of the contract deployer can be mitigated in the future by transferring ownership of
the contract from the original deployer(s) to a community-controlled account (e.g. a multisig contract).

One reason we have chosen EIP-2535 is that Moonstream, which initiated this project, has extensive
experience managing EIP-2535 proxy contracts on mainnets.

## Eras and origins

Every character that will ever exist in the history of Great Wyrm will exist as a token on the Great Wyrm
character contract. This means that characters that lived in different eras will coexist as NFTs in the
same collection.

The question is, how will people and programs distinguish between characters from different periods of
Great Wyrm history?

Conventionally, this kind of information is denoted in token metadata. That approach works well for
the kind of *centralized* games that have existed until now, published by a single studio and closed
to anyone else for extension or modification.

Great Wyrm is a *decentralized* game, which means that anybody should be able to build for the Great
Wyrm community and make use of *any* of the Great Wyrm mechanics they wish to in the process. This makes
it the responsibility of anyone commiting to the Great Wyrm codebase to ensure to the best of our abilities
that we support this kind of extension in our programs.

Our mandate for decentralization means that we cannot simply rely on token metadata to convey the time
in history, geographic origins, current residence, or any other information about a character from the
world of Great Wyrm. We need to make this information available to smart contracts *and* off-chain programs
that may not even exist yet. The best way to do so is to simply represent the information on-chain and
publish the representation transparently for anyone to consume.

The inventory system we are using provides good support for this kind of metadata, and we will make
extensive use of it to represent this information about characters.

For example, a character token will require its minter to provide an "act" token when the character
is minted. This will denote that the character was created during the period of history represented
by that act.

Similarly, a player will use a region token to denote the place that the character hails from.

All these tokens will be equipped into non-unequippable inventory slots, meaning that the choices
are permanent for each character.

## Metadata and CC0

Despite the hard requirement to represent character attributes on-chain, there are certain aspects to
Great Wyrm characters that do not make sense to store on-chain. For example, players will have the ability
to create character portraits and write character descriptions so that other players know how to interact
with them. This information need not be represented on-chain as it does not affect the game's mechanics,
only its social interactions.

As described earlier, the owner of a character will have complete authority on setting the metadata.
The Great Wyrm character contract will not impose any restrictions on *where* this data can be stored
and it will not impose a restriction that the storage mechanism should be decentralized. We suggest to
anyone developing a game client that they build a reasonable default for tokens which do not have valid
metadata URIs.

We also foresee services springing up which make it easy for players to create and store their character
sheets. We welcome this, as this is what decentralized gaming stands for!

The only restriction imposed on players is that the metadata they set for their characters be released
under the [CC0 Creative Commons License](https://creativecommons.org/share-your-work/public-domain/cc0/).
This will ensure that the Great Wyrm community can build the game world without having to worry about
lawsuits tainting the magic of our shared creation.

The method that players use to set metadata URIs on the Great Wyrm character contract will take a boolean
argument (`cc0Consent`) that they have to explicitly set to `true` else the transaction will fail. This
is how we will represent players' consent to release their content to the Great Wyrm community under
CC0.
