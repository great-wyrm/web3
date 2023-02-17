# contracts
Smart contracts for the Great Wyrm decentralized roleplaying game

## Characters

Characters in the world of Great Wyrm:

- [Design document](docs/characters.md)
- [Contracts](contracts/characters/GreatWyrmCharacters.sol)

### Deployments

#### Wyrm chain

The Great Wyrm Characters contract has been deployed to the Wyrm chain. The deployment addresses are:

```json
{
    "contracts": {
        "DiamondCutFacet": "0x59F85f5EF3ab84d0Acbebc7B7c24ea8dD13A51F6",
        "Diamond": "0xDfbC5320704b417C5DBbd950738A32B8B5Ed75b3",
        "DiamondLoupeFacet": "0xe65507aF6BaC7d76e6Ee8944967e301e3D6aB632",
        "OwnershipFacet": "0x730B911a9bE224514FC80E3df0E9D0Ad96130c2C",
        "CharactersFacet": "0x4a0bD5DfE03f039bc701A1313C798F48Ae8555F6"
    },
    "attached": [
        "DiamondLoupeFacet",
        "OwnershipFacet",
        "CharactersFacet"
    ]
}
```

To interact with the proxy contract, use this address: `0xDfbC5320704b417C5DBbd950738A32B8B5Ed75b3`.
