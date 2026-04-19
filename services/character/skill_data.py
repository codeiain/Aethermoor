"""Static skill tree definitions for all classes.

Class mapping from CharacterClass enum:
  Fighter  → Knight  (Guardian / Berserker branches)
  Wizard   → Archmage (Elementalist / Arcanist branches)
  Ranger   → Ranger  (Sharpshooter / Warden branches)

Skill tiers and TP costs follow the skill-tree-class-progression.md spec:
  T1 (level 1–5):  1 TP, 3 skills per branch
  T2 (level 6–10): 1 TP, 3 skills per branch
  T3 (level 11–15): 2 TPs, 2 skills per branch
  T4 (level 16–20): 3 TPs, 2 skills per branch
  Branch total: 16 TPs / 10 skills
"""
from __future__ import annotations
from typing import Any

# ── Type aliases ────────────────────────────────────────────────────────────────

SkillDef = dict[str, Any]
BranchDef = dict[str, Any]
TreeDef = dict[str, Any]


def _skill(
    id: str,
    name: str,
    tier: int,
    tp_cost: int,
    level_req: int,
    prerequisites: list[str],
    skill_type: str,
    effect: str,
) -> SkillDef:
    return {
        "id": id,
        "name": name,
        "tier": tier,
        "tp_cost": tp_cost,
        "level_requirement": level_req,
        "prerequisites": prerequisites,
        "type": skill_type,  # passive | active_action | active_bonus | active_reaction
        "effect": effect,
    }


# ── KNIGHT (Fighter) ────────────────────────────────────────────────────────────

KNIGHT_GUARDIAN: BranchDef = {
    "id": "guardian",
    "name": "Guardian",
    "colour": "#4488ee",
    "passive": {
        "name": "Shield Wall",
        "effect": "While wielding a shield, AC +1.",
    },
    "skills": [
        _skill("taunt", "Taunt", 1, 1, 1, [], "active_action",
               "Force one enemy within 30ft to target only you for 2 rounds. Generates +20 flat threat. DC: CON."),
        _skill("shield_mastery", "Shield Mastery", 1, 1, 1, [], "passive",
               "Shield bash (Bonus Action): 1d4+STR bludgeoning; target STR save or knocked prone. Once per round."),
        _skill("second_wind", "Second Wind", 1, 1, 3, ["taunt"], "active_bonus",
               "Heal self: 1d10 + level HP. Once per combat."),
        _skill("deflect", "Deflect", 2, 1, 5, ["shield_mastery"], "active_reaction",
               "When hit by a melee attack, reduce damage by 1d6 + CON modifier. Once per round."),
        _skill("rallying_cry", "Rallying Cry", 2, 1, 7, ["taunt", "second_wind"], "active_action",
               "All allies within 20ft gain 1d6 + level temporary HP for 1 minute. Once per short rest."),
        _skill("fortified_stance", "Fortified Stance", 2, 1, 9, ["deflect"], "active_bonus",
               "For 1 round: +3 AC; speed reduced to 0. Can break early by moving (bonus ends)."),
        _skill("iron_will", "Iron Will", 3, 2, 11, ["second_wind", "deflect"], "passive",
               "Advantage on all CON saving throws."),
        _skill("guardians_aura", "Guardian's Aura", 3, 2, 13, ["rallying_cry", "fortified_stance"], "passive",
               "All allies within 10ft gain +1 AC (does not stack with multiple Guardians)."),
        _skill("unyielding", "Unyielding", 4, 3, 15, ["iron_will", "guardians_aura"], "passive",
               "When reduced to 0 HP, make a CON save DC 15 to survive at 1 HP instead. Once per long rest."),
        _skill("last_stand", "Last Stand", 4, 3, 17, ["unyielding"], "passive",
               "While below 25% max HP, all incoming damage is halved (rounded down, minimum 1)."),
    ],
}

KNIGHT_BERSERKER: BranchDef = {
    "id": "berserker",
    "name": "Berserker",
    "colour": "#ee4433",
    "passive": {
        "name": "Battle Fury",
        "effect": "Deal +1 damage per 10% of max HP missing (stacks to +10 damage at 1 HP).",
    },
    "skills": [
        _skill("power_strike", "Power Strike", 1, 1, 1, [], "active_action",
               "One melee attack at +2 hit, +1d6 damage. Uses full Action."),
        _skill("reckless_attack", "Reckless Attack", 1, 1, 1, [], "active_action",
               "Attack with advantage on all attack rolls this round. Until your next turn, all attacks against you also have advantage."),
        _skill("cleave", "Cleave", 1, 1, 3, ["power_strike"], "passive",
               "When you hit a melee attack, adjacent enemies (within 5ft of target) take half the damage dice result (no modifier)."),
        _skill("battle_cry", "Battle Cry", 2, 1, 5, ["reckless_attack"], "active_bonus",
               "Gain advantage on your next attack roll this round. Once per round."),
        _skill("extra_attack", "Extra Attack", 2, 1, 7, ["power_strike", "battle_cry"], "passive",
               "Make 2 attacks with your Attack action instead of 1."),
        _skill("frenzy", "Frenzy", 2, 1, 9, ["reckless_attack", "battle_cry"], "active_bonus",
               "Enter Frenzy for 3 rounds: +2 to attack rolls, +1d6 damage, -2 AC; gain one free Bonus Action attack per round (1d6+STR). Once per short rest."),
        _skill("brutal_critical", "Brutal Critical", 3, 2, 11, ["cleave", "extra_attack"], "passive",
               "Critical hits roll one additional weapon damage die (e.g. longsword: 3d8 instead of 2d8 on crit)."),
        _skill("war_machine", "War Machine", 3, 2, 13, ["frenzy", "brutal_critical"], "passive",
               "While in Frenzy: ignore disadvantage from being surrounded (3+ adjacent enemies); move through enemy spaces (provoking no opportunity attacks from targets you attacked this round)."),
        _skill("overwhelming_blow", "Overwhelming Blow", 4, 3, 15, ["war_machine"], "active_action",
               "One attack at +4 to hit dealing x3 weapon dice damage. Target: STR save DC 15 or knocked prone for 1 round. Once per combat."),
        _skill("avatar_of_war", "Avatar of War", 4, 3, 17, ["overwhelming_blow"], "passive",
               "While below 50% max HP: advantage on all attacks, +4 to all damage rolls, +10 tiles/round movement."),
    ],
}

KNIGHT_TREE: TreeDef = {
    "class_id": "Fighter",
    "display_name": "Knight",
    "class_passive": {
        "name": "Iron Constitution",
        "effect": "+3 HP per level beyond base HP die.",
    },
    "branches": [KNIGHT_GUARDIAN, KNIGHT_BERSERKER],
}


# ── ARCHMAGE (Wizard) ───────────────────────────────────────────────────────────

ARCHMAGE_ELEMENTALIST: BranchDef = {
    "id": "elementalist",
    "name": "Elementalist",
    "colour": "#ee8833",
    "passive": {
        "name": "Elemental Mastery",
        "effect": "All elemental spells (Fire, Cold, Lightning) deal +10% damage.",
    },
    "skills": [
        _skill("firebolt_upgrade", "Firebolt Upgrade", 1, 1, 1, [], "passive",
               "Firebolt cantrip deals an additional +1d6 fire damage. Scales: +1d6 at levels 5, 10, 15."),
        _skill("frost_nova", "Frost Nova", 1, 1, 1, [], "active_action",
               "10ft radius burst centred on self; 1d6 cold damage; DEX save DC or Frozen for 12s. No slot cost; 1/short rest."),
        _skill("chain_lightning", "Chain Lightning", 1, 1, 4, ["firebolt_upgrade"], "passive",
               "Lightning-type spells arc to 1 additional enemy within 20ft of primary target for 50% damage (once per cast)."),
        _skill("ice_wall", "Ice Wall", 2, 1, 6, ["frost_nova"], "active_action",
               "Place a 3-tile solid ice wall (1 tile wide) within 30ft. Blocks movement. Lasts 3 rounds or until dealt 10+ fire damage. No slot; 1/short rest."),
        _skill("combustion", "Combustion", 2, 1, 8, ["firebolt_upgrade", "chain_lightning"], "passive",
               "Fire spells you cast apply Burning (1d6 fire/6s, 18s) on a critical hit or when cast using a 3rd-level or higher slot."),
        _skill("elemental_convergence", "Elemental Convergence", 2, 1, 9, ["ice_wall", "combustion"], "passive",
               "When you deal damage of two different elemental types to the same target in one round, that target takes a bonus 2d6 force damage (once per target per round)."),
        _skill("blizzard", "Blizzard", 3, 2, 11, ["ice_wall", "combustion"], "active_action",
               "30ft radius AoE zone, Concentration 1 min. Any creature entering or starting turn inside: 2d8 cold + DEX save or Frozen. Costs a 3rd-level spell slot."),
        _skill("thundercrash", "Thundercrash", 3, 2, 13, ["chain_lightning", "elemental_convergence"], "active_action",
               "20ft radius AoE; 4d6 lightning; DEX save halves. Frozen targets take double damage from this spell. Costs a 3rd-level slot."),
        _skill("inferno", "Inferno", 4, 3, 15, ["blizzard", "thundercrash"], "active_bonus",
               "Activate: for 1 minute, all your spells deal an additional +1d10 fire damage. Once per long rest."),
        _skill("arcane_storm", "Arcane Storm", 4, 3, 17, ["inferno", "elemental_convergence"], "active_action",
               "50ft radius Concentration zone, 1 min. Allies deal +1d8 elemental damage on hits; enemies take 2d6 elemental per round (type cycles: fire/cold/lightning each round). Costs a 5th-level slot."),
    ],
}

ARCHMAGE_ARCANIST: BranchDef = {
    "id": "arcanist",
    "name": "Arcanist",
    "colour": "#9944ee",
    "passive": {
        "name": "Arcane Focus",
        "effect": "Spell save DC +1; spell attack rolls +1.",
    },
    "skills": [
        _skill("arcane_bolt", "Arcane Bolt", 1, 1, 1, [], "active_action",
               "Ranged spell attack (100ft); 1d10 force damage. On Natural 20 attack roll: target is Stunned 1 round."),
        _skill("arcane_shield", "Arcane Shield", 1, 1, 1, [], "active_reaction",
               "When hit by any attack, gain +3 AC against that triggering attack. Once per round."),
        _skill("gravity_well", "Gravity Well", 1, 1, 4, ["arcane_bolt"], "active_action",
               "10ft radius field at a point within 60ft. Concentration, 1 min. All enemies inside: speed halved; cannot take Dash action. Costs a 1st-level slot."),
        _skill("counterspell", "Counterspell", 2, 1, 6, ["arcane_shield"], "active_reaction",
               "When an enemy within 60ft casts a spell, attempt to interrupt it: spell level <=2 auto-cancelled; spell level 3+ requires INT check DC 10 + spell level. Costs a 3rd-level slot. Once per short rest."),
        _skill("force_lance", "Force Lance", 2, 1, 8, ["arcane_bolt", "gravity_well"], "active_action",
               "120ft line attack (1 tile wide); 3d8 force damage; STR save or pushed 15ft back. Costs a 2nd-level slot."),
        _skill("arcane_echo", "Arcane Echo", 2, 1, 9, ["arcane_bolt", "arcane_shield"], "passive",
               "On any spell critical hit, deal 1d8 force damage to one additional enemy within 20ft of the target (free, no action)."),
        _skill("nullfield", "Nullfield", 3, 2, 11, ["gravity_well", "counterspell"], "active_action",
               "20ft radius zone, 1 round. All magical effects (buffs and debuffs) are suppressed; no spells can be cast inside. Costs a 3rd-level slot."),
        _skill("spell_surge", "Spell Surge", 3, 2, 13, ["force_lance", "arcane_echo"], "passive",
               "After casting any spell of 3rd level or higher, your next spell of 1st or 2nd level costs no slot. Once per short rest."),
        _skill("reality_bend", "Reality Bend", 4, 3, 15, ["nullfield", "spell_surge"], "active_bonus",
               "Teleport up to 60ft to any visible location; ignore opportunity attacks this round. Costs a 2nd-level slot. Unlimited uses."),
        _skill("reality_fracture", "Reality Fracture", 4, 3, 17, ["reality_bend", "arcane_echo"], "active_action",
               "30ft radius AoE at a point within 120ft. All enemies take 8d10 force damage (no save, no resistance applies). Allies take no damage. Costs a 5th-level slot. Once per long rest."),
    ],
}

ARCHMAGE_TREE: TreeDef = {
    "class_id": "Wizard",
    "display_name": "Archmage",
    "class_passive": {
        "name": "Arcane Recovery",
        "effect": "Once per long rest, after a short rest, recover spell slots with total levels equal to half your level (round up).",
    },
    "branches": [ARCHMAGE_ELEMENTALIST, ARCHMAGE_ARCANIST],
}


# ── RANGER ──────────────────────────────────────────────────────────────────────

RANGER_SHARPSHOOTER: BranchDef = {
    "id": "sharpshooter",
    "name": "Sharpshooter",
    "colour": "#ddcc22",
    "passive": {
        "name": "Eagle Eye",
        "effect": "Ranged attacks ignore half-cover; +1 attack rolls against targets at range >60ft.",
    },
    "skills": [
        _skill("aimed_shot", "Aimed Shot", 1, 1, 1, [], "active_bonus",
               "Spend Bonus Action aiming; next attack this round gains +2 hit and +1d8 damage."),
        _skill("steady_hand", "Steady Hand", 1, 1, 1, [], "passive",
               "No disadvantage on ranged attacks while adjacent to enemies."),
        _skill("vital_strike", "Vital Strike", 1, 1, 4, ["aimed_shot"], "passive",
               "On a critical hit with a ranged weapon, target gains Bleeding (1d4/6s) for 18s."),
        _skill("long_shot", "Long Shot", 2, 1, 6, ["steady_hand"], "passive",
               "All bow/crossbow range increments increased by 50%. No penalty die at long range."),
        _skill("piercing_arrow", "Piercing Arrow", 2, 1, 8, ["aimed_shot", "vital_strike"], "active_action",
               "One arrow penetrates through primary target and hits the next enemy directly behind it in a line for 60% damage."),
        _skill("hunters_mark", "Hunter's Mark", 2, 1, 9, ["long_shot"], "active_bonus",
               "Mark one target; deal +1d6 damage on all hits against them for 1 hour. On marked target's death, automatically re-marks nearest enemy (free, no action). Concentration."),
        _skill("glancing_shot", "Glancing Shot", 3, 2, 11, ["piercing_arrow", "hunters_mark"], "passive",
               "On a ranged miss, deal DEX modifier damage to the target (minimum 1; no dice)."),
        _skill("sniper_stance", "Sniper Stance", 3, 2, 13, ["vital_strike", "glancing_shot"], "active_bonus",
               "Toggle on: lose 10 tiles/round movement; gain +3 to all ranged attack rolls. Toggle off: free."),
        _skill("eagle_eye_mastery", "Eagle Eye Mastery", 4, 3, 15, ["sniper_stance", "hunters_mark"], "passive",
               "Crits occur on a roll of 19-20 for all ranged attacks. Critical hits apply Vital Strike's Bleeding even without the Vital Strike skill."),
        _skill("perfect_shot", "Perfect Shot", 4, 3, 17, ["eagle_eye_mastery"], "active_action",
               "One ranged attack that automatically hits and deals maximum damage (no roll, no random). Once per combat."),
    ],
}

RANGER_WARDEN: BranchDef = {
    "id": "warden",
    "name": "Warden",
    "colour": "#44bb55",
    "passive": {
        "name": "Nature's Bond",
        "effect": "You may summon an Animal Companion (Wolf) at will once you invest in this branch.",
    },
    "skills": [
        _skill("entangle", "Entangle", 1, 1, 1, [], "active_action",
               "15ft radius at a point within 60ft; vines erupt. DEX save or Restrained 2 rounds. Costs a 1st-level slot; 1/short rest if no slot."),
        _skill("barbed_trap", "Barbed Trap", 1, 1, 1, [], "active_action",
               "Place a trap on an adjacent tile. Triggers on any enemy entering the tile: 2d6 piercing + Bleeding (1d4/6s, 18s). Lasts 10 minutes. Carry up to 3 traps."),
        _skill("camouflage", "Camouflage", 1, 1, 4, ["entangle"], "active_bonus",
               "Become invisible while standing still on a vegetation tile (forest, grass, swamp). Breaks on movement or attack. No cost; unlimited uses."),
        _skill("pack_hunter", "Pack Hunter", 2, 1, 6, ["barbed_trap"], "passive",
               "You and your Animal Companion have Pack Tactics: both gain advantage on attack rolls against an enemy if the other is within 5ft of that enemy."),
        _skill("multi_arrow", "Multi-Arrow", 2, 1, 8, ["entangle", "barbed_trap"], "active_action",
               "Fire arrows at up to 3 separate targets within 30ft; each takes 1d6 + DEX modifier piercing damage. Uses full Action."),
        _skill("poison_arrow", "Poison Arrow", 2, 1, 9, ["pack_hunter", "barbed_trap"], "active_bonus",
               "Coat your next 3 arrows with poison (1 minute preparation). Each poisoned arrow deals +1d6 poison damage on hit; target CON save DC 13 or Poisoned 18s."),
        _skill("volley", "Volley", 3, 2, 11, ["multi_arrow", "camouflage"], "active_action",
               "Rain arrows in a 20ft radius at a point within 120ft. All targets take 2d8 piercing damage; DEX save halves."),
        _skill("beast_bond", "Beast Bond", 3, 2, 13, ["pack_hunter", "poison_arrow"], "passive",
               "Animal Companion gains: +2 to attack rolls, +3 HP per Ranger level (retroactive), Pack Hunter range extended to 20ft."),
        _skill("storm_of_arrows", "Storm of Arrows", 4, 3, 15, ["volley", "beast_bond"], "active_action",
               "Massive arrow volley. 40ft radius AoE at a point within 120ft. All enemies: 4d8 piercing + 2d6 poison (no save). Once per long rest."),
        _skill("apex_predator", "Apex Predator", 4, 3, 17, ["storm_of_arrows"], "passive",
               "Once per combat, when you or your Animal Companion kills an enemy, both of you immediately gain one free action (attack, move, or use an ability)."),
    ],
}

RANGER_TREE: TreeDef = {
    "class_id": "Ranger",
    "display_name": "Ranger",
    "class_passive": {
        "name": "Wilderness Expertise",
        "effect": "Advantage on Perception checks; cannot be surprised in outdoor zones.",
    },
    "branches": [RANGER_SHARPSHOOTER, RANGER_WARDEN],
}


# ── Registry ─────────────────────────────────────────────────────────────────────

# Keyed by CharacterClass enum value
SKILL_TREES: dict[str, TreeDef] = {
    "Fighter": KNIGHT_TREE,
    "Wizard": ARCHMAGE_TREE,
    "Ranger": RANGER_TREE,
}


def get_tree(character_class: str) -> TreeDef | None:
    return SKILL_TREES.get(character_class)


def get_skill(character_class: str, skill_id: str) -> SkillDef | None:
    tree = get_tree(character_class)
    if tree is None:
        return None
    for branch in tree["branches"]:
        for skill in branch["skills"]:
            if skill["id"] == skill_id:
                return skill
    return None
