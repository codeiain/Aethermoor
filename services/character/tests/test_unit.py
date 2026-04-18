"""Unit tests for D&D stat generation and character validation logic."""
import sys
import os

# Add the service root to the path so we can import modules directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from dnd import (
    constitution_modifier,
    generate_ability_scores,
    max_hp_at_level_1,
    roll_4d6_drop_lowest,
    xp_to_level,
)


class TestRoll4d6DropLowest:
    def test_result_in_range(self):
        """4d6 drop lowest result must be in [3, 18]."""
        for _ in range(1000):
            result = roll_4d6_drop_lowest()
            assert 3 <= result <= 18, f"Out of range: {result}"

    def test_result_is_integer(self):
        assert isinstance(roll_4d6_drop_lowest(), int)

    def test_minimum_possible(self):
        """Minimum is 3 (three 1s after dropping the lowest 1)."""
        # Statistical: with 10_000 rolls we should never get < 3
        for _ in range(10_000):
            assert roll_4d6_drop_lowest() >= 3


class TestGenerateAbilityScores:
    def test_returns_six_scores(self):
        scores = generate_ability_scores()
        assert set(scores.keys()) == {
            "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"
        }

    def test_all_scores_in_range(self):
        for _ in range(200):
            scores = generate_ability_scores()
            for key, val in scores.items():
                assert 3 <= val <= 18, f"{key}={val} out of range"


class TestConstitutionModifier:
    @pytest.mark.parametrize("score,expected", [
        (10, 0),
        (11, 0),
        (12, 1),
        (8, -1),
        (18, 4),
        (3, -4),
        (20, 5),
        (1, -5),
    ])
    def test_modifier(self, score, expected):
        assert constitution_modifier(score) == expected


class TestMaxHpAtLevel1:
    @pytest.mark.parametrize("character_class,constitution,expected_min", [
        ("Fighter", 10, 10),   # d10 + 0 modifier
        ("Fighter", 12, 11),   # d10 + 1
        ("Wizard", 10, 6),     # d6 + 0
        ("Cleric", 10, 8),     # d8 + 0
        ("Paladin", 14, 12),   # d10 + 2
        ("Rogue", 8, 7),       # d8 - 1
    ])
    def test_hp_value(self, character_class, constitution, expected_min):
        hp = max_hp_at_level_1(character_class, constitution)
        assert hp == expected_min

    def test_minimum_hp_is_1(self):
        """Even with very low CON, HP is never below 1."""
        hp = max_hp_at_level_1("Wizard", 1)  # d6 + (-5) modifier → max(1, 1) = 1
        assert hp >= 1

    def test_unknown_class_defaults_to_d8(self):
        hp = max_hp_at_level_1("UnknownClass", 10)
        assert hp == 8  # d8 + 0


class TestXpToLevel:
    @pytest.mark.parametrize("xp,expected_level", [
        (0, 1),
        (299, 1),
        (300, 2),
        (900, 3),
        (2700, 4),
        (6500, 5),
        (355000, 20),
        (999999, 20),  # capped at 20
    ])
    def test_level_thresholds(self, xp, expected_level):
        assert xp_to_level(xp) == expected_level


# ── Tutorial step validation ──────────────────────────────────────────────────

TUTORIAL_STEPS = 5


def advance_step_logic(current: int | None, step: int) -> int | None:
    """Pure function mirroring the advance_tutorial_step route logic."""
    if step not in range(TUTORIAL_STEPS) and step != -1:
        raise ValueError(f"step must be 0–{TUTORIAL_STEPS - 1} or -1")
    if current == -1:
        return current  # already done/skipped — idempotent
    if step == -1 or current is None or step > current:
        return step
    return current


class TestTutorialStepLogic:
    def test_first_advance_from_none(self):
        assert advance_step_logic(None, 0) == 0

    def test_advance_sequential(self):
        s = None
        for i in range(TUTORIAL_STEPS):
            s = advance_step_logic(s, i)
            assert s == i

    def test_skip_from_none(self):
        assert advance_step_logic(None, -1) == -1

    def test_skip_from_mid(self):
        assert advance_step_logic(2, -1) == -1

    def test_idempotent_when_done(self):
        assert advance_step_logic(-1, 0) == -1
        assert advance_step_logic(-1, -1) == -1

    def test_cannot_regress(self):
        assert advance_step_logic(3, 1) == 3  # stays at 3

    def test_invalid_step_raises(self):
        with pytest.raises(ValueError):
            advance_step_logic(None, 5)

    def test_invalid_negative_step_raises(self):
        with pytest.raises(ValueError):
            advance_step_logic(None, -2)

    def test_last_valid_step(self):
        assert advance_step_logic(3, 4) == 4
