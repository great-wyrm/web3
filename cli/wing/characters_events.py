CONTRACT_INFORMATION_SET = {
    "anonymous": False,
    "inputs": [
        {"indexed": False, "internalType": "string", "name": "name", "type": "string"},
        {
            "indexed": False,
            "internalType": "string",
            "name": "symbol",
            "type": "string",
        },
        {"indexed": False, "internalType": "string", "name": "uri", "type": "string"},
    ],
    "name": "ContractInformationSet",
    "type": "event",
}
INVENTORY_SET = {
    "anonymous": False,
    "inputs": [
        {
            "indexed": False,
            "internalType": "address",
            "name": "inventoryAddress",
            "type": "address",
        }
    ],
    "name": "InventorySet",
    "type": "event",
}
TOKEN_URI_SET = {
    "anonymous": False,
    "inputs": [
        {
            "indexed": True,
            "internalType": "uint256",
            "name": "tokenId",
            "type": "uint256",
        },
        {
            "indexed": True,
            "internalType": "address",
            "name": "changer",
            "type": "address",
        },
        {"indexed": False, "internalType": "string", "name": "uri", "type": "string"},
    ],
    "name": "TokenURISet",
    "type": "event",
}
TOKEN_VALIDITY_SET = {
    "anonymous": False,
    "inputs": [
        {
            "indexed": True,
            "internalType": "uint256",
            "name": "tokenId",
            "type": "uint256",
        },
        {
            "indexed": True,
            "internalType": "address",
            "name": "changer",
            "type": "address",
        },
        {"indexed": False, "internalType": "bool", "name": "valid", "type": "bool"},
    ],
    "name": "TokenValiditySet",
    "type": "event",
}
