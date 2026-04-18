"""Seed the quest catalogue with the 5 starter quests from RPG-48.

All quests are idempotent — existing quests by ID are skipped.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Quest

SEED_QUESTS: list[dict] = [
    {
        "id": "q001_town_in_peril",
        "title": "A Town in Peril",
        "npc_giver": "town_guard",
        "briefing_dialogue": (
            "Traveller! Thank the gods you're here. Goblins have been raiding the outskirts "
            "of Millhaven — three attacks this week alone. We're stretched thin on the walls. "
            "Would you venture out and drive them back? Kill five of the blighters and we'll "
            "make it worth your while."
        ),
        "objectives_template": [
            {"type": "kill_count", "target": "goblin", "required": 5}
        ],
        "completion_dialogue": (
            "Five goblins? Already? By the gods, you move fast. Millhaven owes you a debt. "
            "Take this gold — you've earned it."
        ),
        "xp_reward": 120,
        "gold_reward": 50,
        "item_reward": None,
        "item_reward_qty": 1,
        "prerequisites": [],
        "sort_order": 1,
    },
    {
        "id": "q002_hildas_stock",
        "title": "Hilda's Lost Stock",
        "npc_giver": "hilda_merchant",
        "briefing_dialogue": (
            "Oh, you look capable! My last supply cart was ambushed by wolves on the forest road. "
            "Three crates of merchant goods scattered across the Whispering Forest. "
            "I can't close the shop to go fetch them myself. Bring them back and I'll reward you "
            "handsomely — and throw in something useful from my stockroom."
        ),
        "objectives_template": [
            {"type": "item_gather", "item_id": "merchant_goods_crate", "required": 3}
        ],
        "completion_dialogue": (
            "All three crates! Wonderful! You have no idea how much stock was in those. "
            "Here's your coin, and take this healing potion — you might need it out there."
        ),
        "xp_reward": 100,
        "gold_reward": 75,
        "item_reward": "health_potion",
        "item_reward_qty": 2,
        "prerequisites": [],
        "sort_order": 2,
    },
    {
        "id": "q003_wandering_elder",
        "title": "The Wandering Elder",
        "npc_giver": "town_guard",
        "briefing_dialogue": (
            "The village elder, Aldric, wandered into the Whispering Forest two days ago and "
            "hasn't returned. He goes on these walks to commune with the old trees — harmless "
            "normally, but the wolves are restless. Find him at the old stone circle deep in the "
            "forest and tell him to come home."
        ),
        "objectives_template": [
            {"type": "interact_npc", "npc_id": "forest_elder_aldric", "required": 1}
        ],
        "completion_dialogue": (
            "Aldric returned safe — I saw him walk in this morning, calm as you please. "
            "Said a traveller sent him home. That was you, wasn't it? You have our thanks."
        ),
        "xp_reward": 80,
        "gold_reward": 40,
        "item_reward": None,
        "item_reward_qty": 1,
        "prerequisites": ["q001_town_in_peril"],
        "sort_order": 3,
    },
    {
        "id": "q004_scout_the_forest",
        "title": "Scout the Forest",
        "npc_giver": "hilda_merchant",
        "briefing_dialogue": (
            "I need a reliable traveller to map the safe paths through the Whispering Forest — "
            "my suppliers are too scared to use the old routes. Head in and scout the area. "
            "Just make it back alive and tell me what you saw."
        ),
        "objectives_template": [
            {"type": "explore_location", "zone_id": "whispering_forest", "required": 1}
        ],
        "completion_dialogue": (
            "You explored the whole forest and came back? You're braver than most. "
            "Here's your payment — and my respect, which counts for something in Millhaven."
        ),
        "xp_reward": 90,
        "gold_reward": 60,
        "item_reward": None,
        "item_reward_qty": 1,
        "prerequisites": [],
        "sort_order": 4,
    },
    {
        "id": "q005_purge_the_crypt",
        "title": "Purge the Crypt",
        "npc_giver": "town_guard",
        "briefing_dialogue": (
            "The Sunken Crypt beneath the old chapel has woken up. Five skeletons marched out "
            "last night — we drove them back, but there are more below. We need someone to go "
            "down there and put them to rest permanently. Five skeletons. Can you do it?"
        ),
        "objectives_template": [
            {"type": "kill_count", "target": "skeleton", "required": 5}
        ],
        "completion_dialogue": (
            "Five skeletons, silenced. The crypt is quiet again — for now. You're a true "
            "warrior, friend. Take this equipment as a token of Millhaven's gratitude."
        ),
        "xp_reward": 200,
        "gold_reward": 100,
        "item_reward": "iron_sword",
        "item_reward_qty": 1,
        "prerequisites": ["q001_town_in_peril"],
        "sort_order": 5,
    },
]


async def seed_quests(db: AsyncSession) -> int:
    """Insert seed quests if they don't already exist. Returns count of new quests added."""
    added = 0
    for data in SEED_QUESTS:
        existing = await db.get(Quest, data["id"])
        if existing is not None:
            continue
        db.add(Quest(**data))
        added += 1

    if added:
        await db.commit()
    return added
