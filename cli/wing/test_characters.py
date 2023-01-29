import unittest

from brownie import accounts, network, web3 as web3_client, ZERO_ADDRESS
from brownie.exceptions import VirtualMachineError
from brownie.network import chain
from moonworm.watch import _fetch_events_chunk

from . import characters_events, CharactersFacet, MockERC20, MockTerminus
from .core import characters_gogogo

MAX_UINT = 2**256 - 1

class CharactersTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            network.connect()
        except:
            pass

        cls.owner = accounts[0]
        cls.owner_tx_config = {"from": cls.owner}

        cls.admin = accounts[1]
        cls.player = accounts[2]
        cls.random_person = accounts[3]

        cls.terminus = MockTerminus.MockTerminus(None)
        cls.terminus.deploy(cls.owner_tx_config)

        cls.payment_token = MockERC20.MockERC20(None)
        cls.payment_token.deploy("lol", "lol", cls.owner_tx_config)

        cls.terminus.set_payment_token(cls.payment_token.address, cls.owner_tx_config)
        cls.terminus.set_pool_base_price(1, cls.owner_tx_config)

        cls.payment_token.mint(cls.owner.address, 999999, cls.owner_tx_config)

        cls.payment_token.approve(cls.terminus.address, MAX_UINT, cls.owner_tx_config)

        cls.terminus.create_pool_v1(1, False, True, cls.owner_tx_config)
        cls.admin_terminus_pool_id = cls.terminus.total_pools()
        cls.terminus.create_pool_v1(MAX_UINT, True, True, cls.owner_tx_config)
        cls.character_creation_terminus_pool_id = cls.terminus.total_pools()

        # Mint admin badge to administrator account
        cls.terminus.mint(
            cls.admin.address, cls.admin_terminus_pool_id, 1, "", cls.owner_tx_config
        )

        # Mint character creation badges to player account
        cls.terminus.mint(cls.player.address, cls.character_creation_terminus_pool_id, 10, "", cls.owner_tx_config)

        cls.contract_name = "Great Wyrm Test Characters"
        cls.contract_symbol = "WYRMTEST"
        cls.contract_uri = "https://example.com"

        cls.predeployment_block = len(chain)
        cls.deployed_contracts = characters_gogogo(
            cls.terminus.address,
            cls.admin_terminus_pool_id,
            cls.character_creation_terminus_pool_id,
            cls.contract_name,
            cls.contract_symbol,
            cls.contract_uri,
            cls.owner_tx_config,
        )
        cls.postdeployment_block = len(chain)
        cls.characters = CharactersFacet.CharactersFacet(
            cls.deployed_contracts["contracts"]["Diamond"]
        )


class CharactersSetupTests(CharactersTestCase):
    def test_characters_setup(self):
        current_block = len(chain)
        contract_information_set_events = _fetch_events_chunk(web3_client, characters_events.CONTRACT_INFORMATION_SET, 0, current_block, self.characters.address)
        self.assertEqual(len(contract_information_set_events), 1)
        event = contract_information_set_events[0]
        self.assertEqual(event["event"], "ContractInformationSet")
        self.assertEqual(event["args"]["name"], self.contract_name)
        self.assertEqual(event["args"]["symbol"], self.contract_symbol)
        self.assertEqual(event["args"]["uri"], self.contract_uri)

        self.assertEqual(self.characters.name(), self.contract_name)
        self.assertEqual(self.characters.symbol(), self.contract_symbol)
        self.assertEqual(self.characters.contract_uri(), self.contract_uri)
