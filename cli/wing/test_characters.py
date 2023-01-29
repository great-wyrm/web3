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

        # Approve Characters contract for the character creation Terminus pool.
        cls.terminus.approve_for_pool(
            cls.character_creation_terminus_pool_id,
            cls.characters.address,
            cls.owner_tx_config,
        )


class CharactersSetupTests(CharactersTestCase):
    def test_characters_setup(self):
        contract_information_set_events = _fetch_events_chunk(
            web3_client,
            characters_events.CONTRACT_INFORMATION_SET,
            self.predeployment_block,
            self.postdeployment_block,
            self.characters.address,
        )
        self.assertEqual(len(contract_information_set_events), 1)
        event = contract_information_set_events[0]
        self.assertEqual(event["event"], "ContractInformationSet")
        self.assertEqual(event["args"]["name"], self.contract_name)
        self.assertEqual(event["args"]["symbol"], self.contract_symbol)
        self.assertEqual(event["args"]["uri"], self.contract_uri)

        self.assertEqual(self.characters.name(), self.contract_name)
        self.assertEqual(self.characters.symbol(), self.contract_symbol)
        self.assertEqual(self.characters.contract_uri(), self.contract_uri)


class CharacterCreationTests(CharactersTestCase):
    def test_character_creation_requires_character_creation_terminus_token(self):
        self.assertEqual(
            self.terminus.balance_of(
                self.random_person, self.character_creation_terminus_pool_id
            ),
            0,
        )

        with self.assertRaises(VirtualMachineError):
            self.characters.create_character(
                self.random_person.address, {"from": self.random_person}
            )

        self.assertEqual(self.characters.total_supply(), 0)

    def test_character_creation_requires_character_creation_terminus_token_even_for_admins(
        self,
    ):
        self.assertEqual(
            self.terminus.balance_of(
                self.admin, self.character_creation_terminus_pool_id
            ),
            0,
        )

        with self.assertRaises(VirtualMachineError):
            self.characters.create_character(self.admin.address, {"from": self.admin})

        self.assertEqual(self.characters.total_supply(), 0)

    def test_mint_to_self(self):
        # Mint character creation badge to player account
        self.terminus.mint(
            self.player.address,
            self.character_creation_terminus_pool_id,
            10,
            "",
            self.owner_tx_config,
        )

        total_supply_0 = self.characters.total_supply()
        character_creation_token_balance_0 = self.terminus.balance_of(
            self.player.address, self.character_creation_terminus_pool_id
        )
        player_character_balance_0 = self.characters.balance_of(self.player.address)

        self.characters.create_character(self.player.address, {"from": self.player})

        total_supply_1 = self.characters.total_supply()
        character_creation_token_balance_1 = self.terminus.balance_of(
            self.player.address, self.character_creation_terminus_pool_id
        )
        player_character_balance_1 = self.characters.balance_of(self.player.address)

        self.assertEqual(total_supply_1, total_supply_0 + 1)
        self.assertEqual(
            character_creation_token_balance_1, character_creation_token_balance_0 - 1
        )
        self.assertEqual(player_character_balance_1, player_character_balance_0 + 1)

    def test_mint_to_other(self):
        # Mint character creation badge to player account
        self.terminus.mint(
            self.player.address,
            self.character_creation_terminus_pool_id,
            10,
            "",
            self.owner_tx_config,
        )

        total_supply_0 = self.characters.total_supply()
        character_creation_token_balance_0 = self.terminus.balance_of(
            self.player.address, self.character_creation_terminus_pool_id
        )
        player_character_balance_0 = self.characters.balance_of(self.player.address)
        random_person_character_balance_0 = self.characters.balance_of(
            self.random_person.address
        )

        self.characters.create_character(
            self.random_person.address, {"from": self.player}
        )

        total_supply_1 = self.characters.total_supply()
        character_creation_token_balance_1 = self.terminus.balance_of(
            self.player.address, self.character_creation_terminus_pool_id
        )
        player_character_balance_1 = self.characters.balance_of(self.player.address)
        random_person_character_balance_1 = self.characters.balance_of(
            self.random_person.address
        )

        self.assertEqual(total_supply_1, total_supply_0 + 1)
        self.assertEqual(
            character_creation_token_balance_1, character_creation_token_balance_0 - 1
        )
        self.assertEqual(player_character_balance_1, player_character_balance_0)
        self.assertEqual(
            random_person_character_balance_1, random_person_character_balance_0 + 1
        )


class TestCharacterProfiles(CharactersTestCase):
    def setUp(self):
        self.terminus.mint(
            self.player.address,
            self.character_creation_terminus_pool_id,
            2,
            "",
            self.owner_tx_config,
        )
        self.characters.create_character(self.player.address, {"from": self.player})
        self.token_id = self.characters.total_supply()

    def test_player_can_change_character_metadata(self):
        self.assertFalse(self.characters.is_metadata_valid(self.token_id))
        self.assertEqual(self.characters.token_uri(self.token_id), "")

        profile_uri = f"https://example.com/characters/{self.token_id}/profile.json"
        self.characters.set_token_uri(
            self.token_id, profile_uri, True, {"from": self.player}
        )

        self.assertFalse(self.characters.is_metadata_valid(self.token_id))
        self.assertEqual(self.characters.token_uri(self.token_id), profile_uri)

    def test_player_cannot_change_character_metadata_if_they_do_not_agree_to_license_terms(
        self,
    ):
        self.assertFalse(self.characters.is_metadata_valid(self.token_id))
        self.assertEqual(self.characters.token_uri(self.token_id), "")

        profile_uri = f"https://example.com/characters/{self.token_id}/profile.json"
        with self.assertRaises(VirtualMachineError):
            self.characters.set_token_uri(
                self.token_id, profile_uri, False, {"from": self.player}
            )

        self.assertFalse(self.characters.is_metadata_valid(self.token_id))
        self.assertEqual(self.characters.token_uri(self.token_id), "")

    def test_admin_cannot_change_player_character_metadata(self):
        self.assertFalse(self.characters.is_metadata_valid(self.token_id))
        self.assertEqual(self.characters.token_uri(self.token_id), "")

        profile_uri = f"https://example.com/characters/{self.token_id}/profile.json"
        with self.assertRaises(VirtualMachineError):
            self.characters.set_token_uri(
                self.token_id, profile_uri, False, {"from": self.admin}
            )

        self.assertFalse(self.characters.is_metadata_valid(self.token_id))
        self.assertEqual(self.characters.token_uri(self.token_id), "")

    def test_admin_can_approve_profile(self):
        self.assertFalse(self.characters.is_metadata_valid(self.token_id))
        self.characters.set_metadata_validity(self.token_id, True, {"from": self.admin})
        self.assertTrue(self.characters.is_metadata_valid(self.token_id))

    def test_player_cannot_approve_profile(self):
        self.assertFalse(self.characters.is_metadata_valid(self.token_id))
        with self.assertRaises(VirtualMachineError):
            self.characters.set_metadata_validity(
                self.token_id, True, {"from": self.player}
            )
        self.assertFalse(self.characters.is_metadata_valid(self.token_id))

    def test_admin_can_approve_then_unapprove_profile(self):
        self.assertFalse(self.characters.is_metadata_valid(self.token_id))
        self.characters.set_metadata_validity(self.token_id, True, {"from": self.admin})
        self.assertTrue(self.characters.is_metadata_valid(self.token_id))
        self.characters.set_metadata_validity(
            self.token_id, False, {"from": self.admin}
        )
        self.assertFalse(self.characters.is_metadata_valid(self.token_id))

    def test_random_person_cannot_change_player_character_metadata(self):
        self.assertFalse(self.characters.is_metadata_valid(self.token_id))
        self.assertEqual(self.characters.token_uri(self.token_id), "")

        profile_uri = f"https://example.com/characters/{self.token_id}/profile.json"
        with self.assertRaises(VirtualMachineError):
            self.characters.set_token_uri(
                self.token_id, profile_uri, False, {"from": self.random_person}
            )

        self.assertFalse(self.characters.is_metadata_valid(self.token_id))
        self.assertEqual(self.characters.token_uri(self.token_id), "")

    def test_contract_owner_cannot_change_player_character_metadata(self):
        self.assertFalse(self.characters.is_metadata_valid(self.token_id))
        self.assertEqual(self.characters.token_uri(self.token_id), "")

        profile_uri = f"https://example.com/characters/{self.token_id}/profile.json"
        with self.assertRaises(VirtualMachineError):
            self.characters.set_token_uri(
                self.token_id, profile_uri, False, {"from": self.owner}
            )

        self.assertFalse(self.characters.is_metadata_valid(self.token_id))
        self.assertEqual(self.characters.token_uri(self.token_id), "")

    def test_random_person_cannot_change_profile_validity(self):
        self.assertFalse(self.characters.is_metadata_valid(self.token_id))
        with self.assertRaises(VirtualMachineError):
            self.characters.set_metadata_validity(
                self.token_id, True, {"from": self.random_person}
            )
        self.assertFalse(self.characters.is_metadata_valid(self.token_id))

    def test_contract_owner_cannot_change_profile_validity(self):
        self.assertFalse(self.characters.is_metadata_valid(self.token_id))
        with self.assertRaises(VirtualMachineError):
            self.characters.set_metadata_validity(
                self.token_id, True, {"from": self.owner}
            )
        self.assertFalse(self.characters.is_metadata_valid(self.token_id))
