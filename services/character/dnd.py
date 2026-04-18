"""D&D mechanic helpers for AETHERMOOR character generation.

Reference: D&D 5e Standard Array / 4d6-drop-lowest method.
"""
import random


# XP thresholds per level (indices 0–19 = levels 1–20)
_XP_THRESHOLDS = [
    0,       # level 1
    300,     # level 2
    900,     # level 3
    2700,    # level 4
    6500,    # level 5
    14000,   # level 6
    23000,   # level 7
    34000,   # level 8
    48000,   # level 9
    64000,   # level 10
    85000,   # level 11
    100000,  # level 12
    120000,  # level 13
    140000,  # level 14
    165000,  # level 15
    195000,  # level 16
    225000,  # level 17
    265000,  # level 18
    305000,  # level 19
    355000,  # level 20
]

# Hit dice by class (d-value)
_HIT_DICE: dict[str, int] = {
    "Fighter": 10,
    "Wizard": 6,
    "Rogue": 8,
    "Cleric": 8,
    "Ranger": 10,
    "Paladin": 10,
}


def roll_4d6_drop_lowest() -> int:
    """Roll 4d6, drop the lowest die, return the sum. Range: 3–18."""
    rolls = [random.randint(1, 6) for _ in range(4)]
    return sum(sorted(rolls)[1:])  # drop lowest


def generate_ability_scores() -> dict[str, int]:
    """Generate the six D&D ability scores using 4d6-drop-lowest for each."""
    return {
        "strength": roll_4d6_drop_lowest(),
        "dexterity": roll_4d6_drop_lowest(),
        "constitution": roll_4d6_drop_lowest(),
        "intelligence": roll_4d6_drop_lowest(),
        "wisdom": roll_4d6_drop_lowest(),
        "charisma": roll_4d6_drop_lowest(),
    }


def constitution_modifier(constitution: int) -> int:
    """Return the D&D ability modifier for a given score: (score - 10) // 2."""
    return (constitution - 10) // 2


def max_hp_at_level_1(character_class: str, constitution: int) -> int:
    """Level-1 max HP = hit die maximum + CON modifier. Minimum 1."""
    hit_die = _HIT_DICE.get(character_class, 8)
    hp = hit_die + constitution_modifier(constitution)
    return max(1, hp)


def xp_to_level(xp: int) -> int:
    """Return the D&D level for a given XP total (capped at 20)."""
    level = 1
    for i, threshold in enumerate(_XP_THRESHOLDS):
        if xp >= threshold:
            level = i + 1
        else:
            break
    return min(level, 20)
