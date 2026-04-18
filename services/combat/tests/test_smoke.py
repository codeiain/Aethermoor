"""Smoke tests for the combat service — validates test framework works."""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dnd_combat import (
    ability_modifier,
    proficiency_bonus,
    roll,
    roll_d20,
    roll_initiative,
    resolve_attack,
    xp_for_cr,
    ConditionType,
    WeaponType,
    add_condition,
    has_condition,
    apply_condition_tick,
    attack_advantage_from_conditions,
)
from schemas import (
    CombatantStats,
    Combatant,
    CombatStatus,
    StartCombatRequest,
)
from combat_engine import start_combat


class TestAbilityModifiers:
    def test_ability_modifier_standard_scores(self):
        assert ability_modifier(10) == 0
        assert ability_modifier(8) == -1
        assert ability_modifier(12) == 1
        assert ability_modifier(14) == 2
        assert ability_modifier(15) == 2
        assert ability_modifier(16) == 3
        assert ability_modifier(20) == 5
        assert ability_modifier(1) == -5

    def test_proficiency_bonus_by_level(self):
        assert proficiency_bonus(1) == 2
        assert proficiency_bonus(4) == 2
        assert proficiency_bonus(5) == 3
        assert proficiency_bonus(8) == 3
        assert proficiency_bonus(9) == 4
        assert proficiency_bonus(12) == 4
        assert proficiency_bonus(17) == 6


class TestDiceRolling:
    def test_roll_returns_within_bounds(self):
        for _ in range(100):
            result = roll(20)
            assert 1 <= result <= 20

    def test_roll_d20_normal(self):
        result, rolls = roll_d20()
        assert 1 <= result <= 20
        assert rolls == [result]

    def test_roll_d20_advantage(self):
        result, rolls = roll_d20(advantage=True)
        assert 1 <= result <= 20
        assert len(rolls) == 2
        assert result == max(rolls)

    def test_roll_d20_disadvantage(self):
        result, rolls = roll_d20(disadvantage=True)
        assert 1 <= result <= 20
        assert len(rolls) == 2
        assert result == min(rolls)

    def test_roll_initiative(self):
        total, raw = roll_initiative(10)
        assert total == raw
        total, raw = roll_initiative(14)
        assert total == raw + 2


class TestCombatEngine:
    def test_start_combat_creates_valid_state(self):
        req = StartCombatRequest(
            character_id="char-123",
            character_name="Aldric",
            character_class="Fighter",
            character_level=5,
            character_hp=45,
            character_max_hp=50,
            character_ac=18,
            character_weapon="longsword",
            character_stats=CombatantStats(strength=16, dexterity=12),
            npc_template_id="goblin-warrior",
            npc_name="Goblin Warrior",
            npc_hp=12,
            npc_max_hp=12,
            npc_ac=13,
            npc_weapon="scimitar",
            npc_cr=0.5,
            npc_stats=CombatantStats(strength=10, dexterity=14),
            npc_gold_drop_min=1,
            npc_gold_drop_max=5,
            zone_id="zone-001",
        )
        state = start_combat(req)

        assert state.id is not None
        assert state.status == CombatStatus.ACTIVE
        assert state.round == 1
        assert len(state.turn_order) == 2
        assert "char-123" in state.combatants
        assert "npc:goblin-warrior" in state.combatants

    def test_start_combat_player_has_correct_stats(self):
        req = StartCombatRequest(
            character_id="char-456",
            character_name="Lyra",
            character_class="Mage",
            character_level=3,
            character_hp=20,
            character_max_hp=20,
            character_ac=12,
            npc_template_id="skeleton",
            npc_name="Skeleton",
            npc_hp=8,
            npc_max_hp=8,
            npc_ac=13,
            zone_id="zone-002",
        )
        state = start_combat(req)
        player = state.combatants["char-456"]

        assert player.is_player is True
        assert player.name == "Lyra"
        assert player.character_class == "Mage"
        assert player.level == 3


class TestConditions:
    def test_add_condition(self):
        conditions = []
        conditions = add_condition(conditions, ConditionType.BLEEDING)
        assert has_condition(conditions, ConditionType.BLEEDING)

    def test_add_condition_respects_max_stacks(self):
        conditions = []
        for _ in range(5):
            conditions = add_condition(conditions, ConditionType.BLEEDING)
        bleeding = next(c for c in conditions if c["type"] == ConditionType.BLEEDING)
        assert bleeding["stacks"] == 3

    def test_condition_tick_reduces_duration(self):
        conditions = [{"type": ConditionType.BLEEDING, "stacks": 1, "rounds_remaining": 3}]
        updated, _ = apply_condition_tick(conditions)
        assert updated[0]["rounds_remaining"] == 2

    def test_condition_expires(self):
        conditions = [{"type": ConditionType.BLEEDING, "stacks": 1, "rounds_remaining": 1}]
        updated, bleed_dmg = apply_condition_tick(conditions)
        assert len(updated) == 0
        assert bleed_dmg > 0


class TestAdvantageFromConditions:
    def test_blinded_gives_advantage_to_attacker(self):
        attacker = []
        target = [{"type": ConditionType.BLINDED, "stacks": 1, "rounds_remaining": 2}]
        adv, dis = attack_advantage_from_conditions(attacker, target)
        assert adv is True
        assert dis is False

    def test_stunned_gives_disadvantage(self):
        attacker = [{"type": ConditionType.STUNNED, "stacks": 1, "rounds_remaining": 1}]
        target = []
        adv, dis = attack_advantage_from_conditions(attacker, target)
        assert adv is False
        assert dis is True


class TestXPRewards:
    def test_xp_for_cr(self):
        assert xp_for_cr(1.0) == 200
        assert xp_for_cr(0.5) == 100
        assert xp_for_cr(0.25) == 50

    def test_xp_for_unknown_cr_returns_max(self):
        assert xp_for_cr(100.0) == 5900
