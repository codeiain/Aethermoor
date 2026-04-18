"""Unit tests for the AETHERMOOR combat engine and D&D dice mechanics.

Run with: pytest tests/test_unit.py -v
"""
from __future__ import annotations

import sys
import os

# Add parent to path so we can import combat service modules directly
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from unittest.mock import patch

from dnd_combat import (
    ability_modifier,
    add_condition,
    apply_condition_tick,
    attack_advantage_from_conditions,
    flee_check,
    has_condition,
    proficiency_bonus,
    resolve_attack,
    roll_damage,
    roll_initiative,
    saving_throw,
    xp_for_cr,
    AttackResult,
    ConditionType,
    WeaponType,
)
from schemas import (
    ActionType,
    CombatStatus,
    CombatantStats,
    StartCombatRequest,
)
from combat_engine import (
    check_combat_end,
    npc_take_turn,
    player_attack,
    player_flee,
    process_player_action,
    start_combat,
)


# ── Ability modifier tests ───────────────────────────────────────────────────

class TestAbilityModifier:
    def test_score_10_gives_zero(self):
        assert ability_modifier(10) == 0

    def test_score_11_gives_zero(self):
        assert ability_modifier(11) == 0

    def test_score_12_gives_plus_one(self):
        assert ability_modifier(12) == 1

    def test_score_8_gives_minus_one(self):
        assert ability_modifier(8) == -1

    def test_score_18_gives_plus_four(self):
        assert ability_modifier(18) == 4

    def test_score_3_gives_minus_four(self):
        assert ability_modifier(3) == -4

    def test_score_20_gives_plus_five(self):
        assert ability_modifier(20) == 5


# ── Proficiency bonus tests ──────────────────────────────────────────────────

class TestProficiencyBonus:
    def test_level_1_gives_two(self):
        assert proficiency_bonus(1) == 2

    def test_level_4_gives_two(self):
        assert proficiency_bonus(4) == 2

    def test_level_5_gives_three(self):
        assert proficiency_bonus(5) == 3

    def test_level_9_gives_four(self):
        assert proficiency_bonus(9) == 4

    def test_level_17_gives_six(self):
        assert proficiency_bonus(17) == 6


# ── Attack resolution tests ──────────────────────────────────────────────────

class TestAttackResolution:
    def test_natural_20_is_crit(self):
        with patch("dnd_combat.roll_d20", return_value=(20, [20])):
            result = resolve_attack(
                attacker_level=1,
                attacker_stat_score=10,
                weapon_type=WeaponType.LONGSWORD,
                target_ac=15,
            )
        assert result["result"] == AttackResult.CRIT
        assert result["damage"] > 0

    def test_natural_1_is_crit_miss(self):
        with patch("dnd_combat.roll_d20", return_value=(1, [1])):
            result = resolve_attack(
                attacker_level=1,
                attacker_stat_score=10,
                weapon_type=WeaponType.LONGSWORD,
                target_ac=5,
            )
        assert result["result"] == AttackResult.CRIT_MISS
        assert result["damage"] == 0

    def test_high_roll_hits(self):
        with patch("dnd_combat.roll_d20", return_value=(18, [18])):
            result = resolve_attack(
                attacker_level=1,
                attacker_stat_score=10,
                weapon_type=WeaponType.LONGSWORD,
                target_ac=15,
            )
        # 18 + 0 (STR mod) + 2 (prof) = 20 >= 15 → hit
        assert result["result"] == AttackResult.HIT
        assert result["damage"] >= 1

    def test_low_roll_misses(self):
        with patch("dnd_combat.roll_d20", return_value=(2, [2])):
            result = resolve_attack(
                attacker_level=1,
                attacker_stat_score=10,
                weapon_type=WeaponType.LONGSWORD,
                target_ac=20,
            )
        # 2 + 0 + 2 = 4 < 20 → miss
        assert result["result"] == AttackResult.MISS
        assert result["damage"] == 0

    def test_damage_minimum_one(self):
        """Even with negative STR modifier, damage is minimum 1."""
        with patch("dnd_combat.roll_d20", return_value=(15, [15])):
            with patch("dnd_combat.roll_damage", return_value=1):
                result = resolve_attack(
                    attacker_level=1,
                    attacker_stat_score=4,  # modifier = -3
                    weapon_type=WeaponType.DAGGER,
                    target_ac=10,
                )
        if result["result"] in (AttackResult.HIT, AttackResult.CRIT):
            assert result["damage"] >= 1

    def test_crit_doubles_damage_dice(self):
        """On a crit, roll_damage is called with is_crit=True."""
        with patch("dnd_combat.roll_d20", return_value=(20, [20])):
            with patch("dnd_combat.roll_damage", return_value=12) as mock_roll:
                resolve_attack(
                    attacker_level=1,
                    attacker_stat_score=10,
                    weapon_type=WeaponType.LONGSWORD,
                    target_ac=15,
                )
        mock_roll.assert_called_once_with(WeaponType.LONGSWORD, is_crit=True)


# ── Condition tests ──────────────────────────────────────────────────────────

class TestConditions:
    def test_add_condition(self):
        conditions = []
        updated = add_condition(conditions, ConditionType.STUNNED)
        assert len(updated) == 1
        assert updated[0]["type"] == ConditionType.STUNNED
        assert updated[0]["stacks"] == 1

    def test_bleeding_stacks_to_three(self):
        conditions = []
        for _ in range(5):
            conditions = add_condition(conditions, ConditionType.BLEEDING)
        assert conditions[0]["stacks"] == 3  # Max stacks

    def test_condition_tick_removes_expired(self):
        conditions = [{"type": ConditionType.STUNNED, "stacks": 1, "rounds_remaining": 1}]
        updated, _ = apply_condition_tick(conditions)
        assert len(updated) == 0

    def test_condition_tick_decrements_duration(self):
        conditions = [{"type": ConditionType.POISONED, "stacks": 1, "rounds_remaining": 3}]
        updated, _ = apply_condition_tick(conditions)
        assert updated[0]["rounds_remaining"] == 2

    def test_bleeding_deals_damage_on_tick(self):
        conditions = [{"type": ConditionType.BLEEDING, "stacks": 2, "rounds_remaining": 2}]
        _, bleed_dmg = apply_condition_tick(conditions)
        assert bleed_dmg > 0  # 2 stacks × 1d4 each

    def test_has_condition(self):
        conditions = [{"type": ConditionType.POISONED, "stacks": 1, "rounds_remaining": 2}]
        assert has_condition(conditions, ConditionType.POISONED)
        assert not has_condition(conditions, ConditionType.STUNNED)

    def test_blinded_gives_disadvantage(self):
        attacker_conds = [{"type": ConditionType.BLINDED, "stacks": 1, "rounds_remaining": 2}]
        adv, dis = attack_advantage_from_conditions(attacker_conds, [])
        assert not adv
        assert dis

    def test_stunned_target_gives_advantage(self):
        target_conds = [{"type": ConditionType.STUNNED, "stacks": 1, "rounds_remaining": 1}]
        adv, dis = attack_advantage_from_conditions([], target_conds)
        assert adv
        assert not dis


# ── Initiative tests ─────────────────────────────────────────────────────────

class TestInitiative:
    def test_higher_dex_increases_average(self):
        """DEX 20 modifier is +5 — mean initiative should be higher than DEX 10."""
        with patch("dnd_combat.roll", return_value=10):
            high_dex_total, _ = roll_initiative(dexterity=20)
            low_dex_total, _ = roll_initiative(dexterity=10)
        assert high_dex_total > low_dex_total

    def test_initiative_uses_dex_modifier(self):
        with patch("dnd_combat.roll", return_value=10):
            total, raw = roll_initiative(dexterity=14)  # modifier = +2
        assert total == 12
        assert raw == 10


# ── Flee tests ───────────────────────────────────────────────────────────────

class TestFlee:
    def test_player_wins_on_tie(self):
        with patch("dnd_combat.roll_initiative", side_effect=[(10, 10), (10, 10)]):
            success, _, _ = flee_check(player_dex=10, npc_dex=10)
        assert success

    def test_player_fails_on_lower_roll(self):
        with patch("dnd_combat.roll_initiative", side_effect=[(5, 5), (15, 15)]):
            success, _, _ = flee_check(player_dex=10, npc_dex=10)
        assert not success


# ── XP rewards ───────────────────────────────────────────────────────────────

class TestXpRewards:
    def test_cr_1_gives_200_xp(self):
        assert xp_for_cr(1.0) == 200

    def test_cr_5_gives_1800_xp(self):
        assert xp_for_cr(5.0) == 1800


# ── Combat engine integration ────────────────────────────────────────────────

def _make_start_request(**overrides) -> StartCombatRequest:
    defaults = dict(
        character_id="char-001",
        character_name="Aldric",
        character_class="Fighter",
        character_level=1,
        character_hp=12,
        character_max_hp=12,
        character_ac=16,
        character_weapon="longsword",
        character_stats=CombatantStats(
            strength=16, dexterity=12, constitution=14,
            intelligence=10, wisdom=10, charisma=10,
        ),
        npc_template_id="goblin-template",
        npc_name="Goblin",
        npc_hp=7,
        npc_max_hp=7,
        npc_ac=13,
        npc_weapon="claws",
        npc_cr=0.25,
        npc_stats=CombatantStats(
            strength=8, dexterity=14, constitution=10,
            intelligence=8, wisdom=8, charisma=8,
        ),
        npc_gold_drop_min=1,
        npc_gold_drop_max=5,
        zone_id="zone-forest-001",
    )
    defaults.update(overrides)
    return StartCombatRequest(**defaults)


class TestCombatEngine:
    def test_start_combat_creates_state(self):
        req = _make_start_request()
        state = start_combat(req)
        assert state.status == CombatStatus.ACTIVE
        assert len(state.combatants) == 2
        assert len(state.turn_order) == 2
        assert state.round == 1

    def test_start_combat_rolls_initiative(self):
        req = _make_start_request()
        state = start_combat(req)
        assert len(state.initiative_rolls) == 2

    def test_player_attack_reduces_npc_hp(self):
        req = _make_start_request()
        state = start_combat(req)
        npc_id = next(cid for cid, c in state.combatants.items() if not c.is_player)
        original_npc_hp = state.combatants[npc_id].hp

        with patch("combat_engine.resolve_attack", return_value={
            "result": "hit", "d20_roll": 15, "rolls": [15], "attack_bonus": 5, "damage": 5
        }):
            new_state, action = player_attack(state, npc_id)

        assert new_state.combatants[npc_id].hp == original_npc_hp - 5

    def test_npc_dead_triggers_player_won(self):
        req = _make_start_request(npc_hp=1)
        state = start_combat(req)
        npc_id = next(cid for cid, c in state.combatants.items() if not c.is_player)

        with patch("combat_engine.resolve_attack", return_value={
            "result": "hit", "d20_roll": 15, "rolls": [15], "attack_bonus": 5, "damage": 10
        }):
            new_state, _ = player_attack(state, npc_id)

        final_state = check_combat_end(new_state)
        assert final_state.status == CombatStatus.PLAYER_WON
        assert final_state.xp_awarded > 0

    def test_player_dead_triggers_player_died(self):
        req = _make_start_request(character_hp=1)
        state = start_combat(req)
        player_id = next(cid for cid, c in state.combatants.items() if c.is_player)

        with patch("combat_engine.resolve_attack", return_value={
            "result": "hit", "d20_roll": 15, "rolls": [15], "attack_bonus": 3, "damage": 10
        }):
            new_state, _ = npc_take_turn(state)

        final_state = check_combat_end(new_state)
        assert final_state.status == CombatStatus.PLAYER_DIED

    def test_flee_success_ends_combat(self):
        req = _make_start_request()
        state = start_combat(req)

        with patch("combat_engine.flee_check", return_value=(True, 15, 10)):
            new_state, action = player_flee(state)

        assert new_state.status == CombatStatus.PLAYER_FLED

    def test_flee_fail_continues_combat(self):
        req = _make_start_request()
        state = start_combat(req)

        with patch("combat_engine.flee_check", return_value=(False, 5, 15)):
            new_state, action = player_flee(state)

        assert new_state.status == CombatStatus.ACTIVE

    def test_full_combat_loop(self):
        """Simulate a full combat: player attacks until NPC dies."""
        req = _make_start_request(npc_hp=3, npc_max_hp=3)
        state = start_combat(req)

        rounds = 0
        while state.status == CombatStatus.ACTIVE and rounds < 20:
            with patch("combat_engine.resolve_attack") as mock_attack:
                mock_attack.return_value = {
                    "result": "hit", "d20_roll": 15, "rolls": [15], "attack_bonus": 5, "damage": 2
                }
                state, _, _ = process_player_action(
                    state, ActionType.ATTACK
                )
            rounds += 1

        assert state.status == CombatStatus.PLAYER_WON
        assert state.xp_awarded > 0

    def test_action_log_records_actions(self):
        req = _make_start_request()
        state = start_combat(req)
        npc_id = next(cid for cid, c in state.combatants.items() if not c.is_player)

        with patch("combat_engine.resolve_attack", return_value={
            "result": "miss", "d20_roll": 3, "rolls": [3], "attack_bonus": 5, "damage": 0
        }):
            new_state, _ = player_attack(state, npc_id)

        assert len(new_state.action_log) == 1
        assert new_state.action_log[0].acting_id == req.character_id
