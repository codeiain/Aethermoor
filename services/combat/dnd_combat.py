"""D&D 5e-adjacent combat mechanics for AETHERMOOR.

Reference: combat-spec document on RPGAA-14.

Covers:
  - Ability modifier calculation
  - Proficiency bonus by level
  - Initiative rolls
  - Attack rolls (advantage/disadvantage, crits, misses)
  - Damage rolls by weapon type
  - Saving throws
  - Condition application and duration tracking
  - XP rewards
"""
from __future__ import annotations

import random
from enum import Enum


# ── Ability modifiers ────────────────────────────────────────────────────────

def ability_modifier(score: int) -> int:
    """Return the D&D ability modifier: (score - 10) // 2."""
    return (score - 10) // 2


# ── Proficiency bonus ────────────────────────────────────────────────────────

def proficiency_bonus(level: int) -> int:
    """Return proficiency bonus for a given character level (1–20)."""
    return 2 + (level - 1) // 4


# ── Weapon damage dice ───────────────────────────────────────────────────────

class WeaponType(str, Enum):
    UNARMED = "unarmed"
    DAGGER = "dagger"
    SHORTSWORD = "shortsword"
    LONGSWORD = "longsword"
    GREATAXE = "greataxe"
    HANDAXE = "handaxe"
    QUARTERSTAFF = "quarterstaff"
    LONGBOW = "longbow"
    SHORTBOW = "shortbow"
    HAND_CROSSBOW = "hand_crossbow"
    ARCANE_STAFF = "arcane_staff"
    CLAWS = "claws"        # NPC melee
    BITE = "bite"          # NPC melee + bleed
    GREATSWORD = "greatsword"


_WEAPON_DAMAGE_DIE: dict[str, int] = {
    WeaponType.UNARMED: 4,
    WeaponType.DAGGER: 4,
    WeaponType.SHORTSWORD: 6,
    WeaponType.LONGSWORD: 8,
    WeaponType.GREATAXE: 12,
    WeaponType.HANDAXE: 6,
    WeaponType.QUARTERSTAFF: 6,
    WeaponType.LONGBOW: 8,
    WeaponType.SHORTBOW: 6,
    WeaponType.HAND_CROSSBOW: 6,
    WeaponType.ARCANE_STAFF: 6,
    WeaponType.CLAWS: 6,
    WeaponType.BITE: 6,
    WeaponType.GREATSWORD: 6,  # 2d6
}

_WEAPON_EXTRA_DIE: dict[str, int] = {
    WeaponType.GREATSWORD: 6,  # rolls 2d6
}

# Key ability used for attack by class
_CLASS_ATTACK_STAT: dict[str, str] = {
    "Fighter": "strength",
    "Warrior": "strength",
    "Rogue": "dexterity",
    "Ranger": "dexterity",
    "Mage": "intelligence",
    "Wizard": "intelligence",
    "Cleric": "wisdom",
    "Paladin": "charisma",
}


def attack_stat_for_class(character_class: str) -> str:
    """Return the key ability name for attack rolls by class."""
    return _CLASS_ATTACK_STAT.get(character_class, "strength")


# ── Dice ─────────────────────────────────────────────────────────────────────

def roll(sides: int) -> int:
    """Roll a single die with the given number of sides."""
    return random.randint(1, sides)


def roll_d20(advantage: bool = False, disadvantage: bool = False) -> tuple[int, list[int]]:
    """Roll d20 with optional advantage/disadvantage.

    Returns (result, [all_rolls]).
    Advantage and disadvantage cancel each other out.
    """
    if advantage and not disadvantage:
        rolls = [roll(20), roll(20)]
        return max(rolls), rolls
    if disadvantage and not advantage:
        rolls = [roll(20), roll(20)]
        return min(rolls), rolls
    r = roll(20)
    return r, [r]


def roll_damage(weapon_type: str, is_crit: bool = False) -> int:
    """Roll weapon damage dice. On crit, roll all damage dice twice."""
    die = _WEAPON_DAMAGE_DIE.get(weapon_type, 6)
    extra_die = _WEAPON_EXTRA_DIE.get(weapon_type)

    multiplier = 2 if is_crit else 1
    total = sum(roll(die) for _ in range(multiplier))
    if extra_die:
        total += sum(roll(extra_die) for _ in range(multiplier))
    return total


# ── Attack resolution ────────────────────────────────────────────────────────

class AttackResult(str, Enum):
    CRIT = "crit"
    HIT = "hit"
    MISS = "miss"
    CRIT_MISS = "crit_miss"


def resolve_attack(
    *,
    attacker_level: int,
    attacker_stat_score: int,
    weapon_type: str,
    target_ac: int,
    advantage: bool = False,
    disadvantage: bool = False,
) -> dict:
    """Resolve a melee/ranged attack roll.

    Returns dict with: result, d20_roll, rolls, attack_bonus, damage (0 on miss).
    """
    d20_result, all_rolls = roll_d20(advantage=advantage, disadvantage=disadvantage)

    if d20_result == 1:
        return {
            "result": AttackResult.CRIT_MISS,
            "d20_roll": d20_result,
            "rolls": all_rolls,
            "attack_bonus": 0,
            "damage": 0,
        }

    stat_mod = ability_modifier(attacker_stat_score)
    prof = proficiency_bonus(attacker_level)
    attack_bonus = stat_mod + prof
    total = d20_result + attack_bonus

    is_crit = d20_result == 20
    is_hit = is_crit or total >= target_ac

    if not is_hit:
        return {
            "result": AttackResult.MISS,
            "d20_roll": d20_result,
            "rolls": all_rolls,
            "attack_bonus": attack_bonus,
            "damage": 0,
        }

    raw_damage = roll_damage(weapon_type, is_crit=is_crit)
    damage = max(1, raw_damage + stat_mod)

    return {
        "result": AttackResult.CRIT if is_crit else AttackResult.HIT,
        "d20_roll": d20_result,
        "rolls": all_rolls,
        "attack_bonus": attack_bonus,
        "damage": damage,
    }


# ── Initiative ───────────────────────────────────────────────────────────────

def roll_initiative(dexterity: int) -> tuple[int, int]:
    """Roll initiative: d20 + DEX modifier. Returns (total, raw_d20)."""
    raw = roll(20)
    dex_mod = ability_modifier(dexterity)
    return raw + dex_mod, raw


# ── Saving throws ────────────────────────────────────────────────────────────

def saving_throw(stat_score: int, dc: int) -> tuple[bool, int]:
    """Make a saving throw: d20 + stat modifier >= DC.

    Returns (success, total_roll).
    """
    raw = roll(20)
    mod = ability_modifier(stat_score)
    total = raw + mod
    return total >= dc, total


# ── Flee check ───────────────────────────────────────────────────────────────

def flee_check(player_dex: int, npc_dex: int) -> tuple[bool, int, int]:
    """DEX contest to flee. Player wins on tie.

    Returns (player_succeeded, player_roll, npc_roll).
    """
    player_roll, _ = roll_initiative(player_dex)
    npc_roll, _ = roll_initiative(npc_dex)
    return player_roll >= npc_roll, player_roll, npc_roll


# ── Conditions ───────────────────────────────────────────────────────────────

class ConditionType(str, Enum):
    STUNNED = "stunned"
    POISONED = "poisoned"
    BLEEDING = "bleeding"
    BURNING = "burning"
    FROZEN = "frozen"
    CHARMED = "charmed"
    FRIGHTENED = "frightened"
    BLINDED = "blinded"


# Max stacks per condition
_CONDITION_MAX_STACKS: dict[str, int] = {
    ConditionType.BLEEDING: 3,
    ConditionType.BURNING: 1,
    ConditionType.POISONED: 1,
    ConditionType.STUNNED: 1,
    ConditionType.FROZEN: 1,
    ConditionType.CHARMED: 1,
    ConditionType.FRIGHTENED: 1,
    ConditionType.BLINDED: 1,
}

# Base duration in rounds
_CONDITION_DURATION_ROUNDS: dict[str, int] = {
    ConditionType.STUNNED: 1,
    ConditionType.POISONED: 5,   # ~30 seconds at 6s/round
    ConditionType.BLEEDING: 3,
    ConditionType.BURNING: 2,
    ConditionType.FROZEN: 2,
    ConditionType.CHARMED: 3,
    ConditionType.FRIGHTENED: 2,
    ConditionType.BLINDED: 2,
}


def apply_condition_tick(conditions: list[dict]) -> tuple[list[dict], int]:
    """Tick all conditions at end of round. Returns (updated_conditions, bleed_damage).

    Decrements durations, removes expired, calculates bleed damage.
    """
    bleed_damage = 0
    updated = []
    for cond in conditions:
        ctype = cond["type"]
        stacks = cond.get("stacks", 1)

        # Bleed ticks each round: 1d4 per stack
        if ctype == ConditionType.BLEEDING:
            for _ in range(stacks):
                bleed_damage += roll(4)

        remaining = cond.get("rounds_remaining", 1) - 1
        if remaining > 0:
            updated.append({**cond, "rounds_remaining": remaining})

    return updated, bleed_damage


def add_condition(conditions: list[dict], condition_type: str) -> list[dict]:
    """Add a condition, respecting max stacks and refreshing duration."""
    max_stacks = _CONDITION_MAX_STACKS.get(condition_type, 1)
    duration = _CONDITION_DURATION_ROUNDS.get(condition_type, 2)

    existing = next((c for c in conditions if c["type"] == condition_type), None)
    if existing:
        new_stacks = min(existing["stacks"] + 1, max_stacks)
        return [
            {**c, "stacks": new_stacks, "rounds_remaining": duration}
            if c["type"] == condition_type else c
            for c in conditions
        ]

    return conditions + [{
        "type": condition_type,
        "stacks": 1,
        "rounds_remaining": duration,
    }]


def has_condition(conditions: list[dict], condition_type: str) -> bool:
    """Return True if the entity currently has the given condition."""
    return any(c["type"] == condition_type for c in conditions)


def attack_advantage_from_conditions(
    attacker_conditions: list[dict],
    target_conditions: list[dict],
    is_ranged: bool = False,
) -> tuple[bool, bool]:
    """Derive advantage/disadvantage on an attack from combatant conditions.

    Returns (advantage, disadvantage).
    """
    advantage = False
    disadvantage = False

    if has_condition(attacker_conditions, ConditionType.BLINDED):
        disadvantage = True
    if has_condition(attacker_conditions, ConditionType.FRIGHTENED):
        disadvantage = True
    if has_condition(attacker_conditions, ConditionType.STUNNED):
        disadvantage = True

    if has_condition(target_conditions, ConditionType.BLINDED):
        advantage = True
    if has_condition(target_conditions, ConditionType.STUNNED):
        advantage = True

    return advantage, disadvantage


# ── XP rewards ───────────────────────────────────────────────────────────────

# XP by enemy challenge rating (CR)
_CR_XP: dict[float, int] = {
    0.0: 10,
    0.125: 25,
    0.25: 50,
    0.5: 100,
    1.0: 200,
    2.0: 450,
    3.0: 700,
    4.0: 1100,
    5.0: 1800,
    6.0: 2300,
    7.0: 2900,
    8.0: 3900,
    9.0: 5000,
    10.0: 5900,
}


def xp_for_cr(cr: float) -> int:
    """Return XP award for defeating an enemy of given challenge rating."""
    return _CR_XP.get(cr, max(_CR_XP.values()))
