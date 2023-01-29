#!/usr/bin/env bash

# Expects a Python environment to be active in which `wing` has been installed for development.
# You can set up the local copy of `wing` for development using:
# pip install -e .[dev]

set -e

SCRIPT_DIR="$(dirname $(realpath $0))"

usage() {
    echo "Usage: $0"
    echo
    echo "Regenerates Python interfaces to all important smart contracts"
}

if [ "$1" = "-h" ] || [ "$1" = "--help" ]
then
    usage
    exit 2
fi

IMPORTANT_CONTRACTS=( \
    "CharactersFacet" \
    "Diamond" \
    "DiamondCutFacet" \
    "DiamondLoupeFacet" \
    "MockERC20" \
    "MockTerminus" \
    "OwnershipFacet" \
)

cd $SCRIPT_DIR

brownie compile

for contract_name in "${IMPORTANT_CONTRACTS[@]}"
do
    echo "Regenerating Python interface for: $contract_name"
    moonworm generate-brownie -p .. -o wing/ -n "$contract_name"
done
