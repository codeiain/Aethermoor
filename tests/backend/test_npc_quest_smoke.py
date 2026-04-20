import unittest

from services.world.npc_catalogue import (
    get_stat_block,
    NPC_CATALOGUE,
    DEFAULT_STAT_BLOCK,
)


class TestNPCCatalogue(unittest.TestCase):
    def test_get_stat_block_known_type(self):
        # Known NPC type should return the corresponding block with matching hp
        wolf_block = get_stat_block("wolf")
        self.assertIn("wolf", NPC_CATALOGUE)
        self.assertEqual(wolf_block.hp, NPC_CATALOGUE["wolf"].hp)

    def test_get_stat_block_unknown_returns_default(self):
        # Unknown NPC type should return the default stat block
        unknown_block = get_stat_block("nonexistent_type_xyz")
        self.assertIsNotNone(unknown_block)
        self.assertEqual(unknown_block.hp, DEFAULT_STAT_BLOCK.hp)


if __name__ == "__main__":
    unittest.main()
