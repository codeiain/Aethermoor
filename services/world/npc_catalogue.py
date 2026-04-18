"""NPC stat-block catalogue for AETHERMOOR.

Maps npc_type strings to default combat stats used when seeding NPC templates.
Stats follow D&D 5e conventions (CR, AC, HP, ability scores).

Add new entries here when introducing new NPC types. The seed script and any
admin tooling reads this catalogue to populate NpcTemplate rows.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class NpcStatBlock:
    hp: int
    max_hp: int
    ac: int
    cr: float
    weapon: str
    gold_drop_min: int
    gold_drop_max: int
    is_hostile: bool
    npc_stats: dict = field(default_factory=lambda: {
        "strength": 10,
        "dexterity": 10,
        "constitution": 10,
        "intelligence": 10,
        "wisdom": 10,
        "charisma": 10,
    })
    dialogue: dict | None = None


# Keyed by npc_type string (matches NpcTemplate.npc_type)
NPC_CATALOGUE: dict[str, NpcStatBlock] = {
    "wolf": NpcStatBlock(
        hp=11, max_hp=11, ac=13, cr=0.25,
        weapon="bite",
        gold_drop_min=0, gold_drop_max=3,
        is_hostile=True,
        npc_stats={
            "strength": 12, "dexterity": 15, "constitution": 12,
            "intelligence": 3, "wisdom": 12, "charisma": 6,
        },
    ),
    "skeleton": NpcStatBlock(
        hp=13, max_hp=13, ac=13, cr=0.25,
        weapon="claws",
        gold_drop_min=0, gold_drop_max=5,
        is_hostile=True,
        npc_stats={
            "strength": 10, "dexterity": 14, "constitution": 15,
            "intelligence": 6, "wisdom": 8, "charisma": 5,
        },
    ),
    "guard": NpcStatBlock(
        hp=11, max_hp=11, ac=16, cr=0.125,
        weapon="longsword",
        gold_drop_min=0, gold_drop_max=0,
        is_hostile=False,
        npc_stats={
            "strength": 13, "dexterity": 12, "constitution": 12,
            "intelligence": 10, "wisdom": 11, "charisma": 10,
        },
        dialogue={
            "greeting": "Move along, citizen.",
            "farewell": "Stay out of trouble.",
        },
    ),
    "merchant": NpcStatBlock(
        hp=4, max_hp=4, ac=10, cr=0.0,
        weapon="claws",
        gold_drop_min=0, gold_drop_max=0,
        is_hostile=False,
        npc_stats={
            "strength": 10, "dexterity": 10, "constitution": 10,
            "intelligence": 12, "wisdom": 11, "charisma": 14,
        },
        dialogue={
            "greeting": "Welcome! I have the finest wares in Millhaven.",
            "farewell": "Come back soon, friend!",
        },
    ),
    "goblin": NpcStatBlock(
        hp=7, max_hp=7, ac=15, cr=0.25,
        weapon="shortsword",
        gold_drop_min=1, gold_drop_max=8,
        is_hostile=True,
        npc_stats={
            "strength": 8, "dexterity": 14, "constitution": 10,
            "intelligence": 10, "wisdom": 8, "charisma": 8,
        },
    ),
    "orc": NpcStatBlock(
        hp=15, max_hp=15, ac=13, cr=0.5,
        weapon="greataxe",
        gold_drop_min=2, gold_drop_max=12,
        is_hostile=True,
        npc_stats={
            "strength": 16, "dexterity": 12, "constitution": 16,
            "intelligence": 7, "wisdom": 11, "charisma": 10,
        },
    ),
    "bandit": NpcStatBlock(
        hp=11, max_hp=11, ac=12, cr=0.125,
        weapon="longsword",
        gold_drop_min=2, gold_drop_max=15,
        is_hostile=True,
        npc_stats={
            "strength": 11, "dexterity": 12, "constitution": 12,
            "intelligence": 10, "wisdom": 10, "charisma": 10,
        },
    ),
    "quest_giver": NpcStatBlock(
        hp=4, max_hp=4, ac=10, cr=0.0,
        weapon="claws",
        gold_drop_min=0, gold_drop_max=0,
        is_hostile=False,
        npc_stats={
            "strength": 10, "dexterity": 10, "constitution": 10,
            "intelligence": 12, "wisdom": 12, "charisma": 14,
        },
        dialogue={
            "greeting": "Ah, adventurer! I have a task that requires your skills.",
            "farewell": "May fortune favour you on your quest!",
        },
    ),
}

# Fallback for unknown npc_types
DEFAULT_STAT_BLOCK = NpcStatBlock(
    hp=10, max_hp=10, ac=10, cr=0.25,
    weapon="claws",
    gold_drop_min=0, gold_drop_max=5,
    is_hostile=True,
    npc_stats={
        "strength": 10, "dexterity": 10, "constitution": 10,
        "intelligence": 10, "wisdom": 10, "charisma": 10,
    },
)


def get_stat_block(npc_type: str) -> NpcStatBlock:
    """Return the stat block for the given npc_type, falling back to default."""
    return NPC_CATALOGUE.get(npc_type, DEFAULT_STAT_BLOCK)
