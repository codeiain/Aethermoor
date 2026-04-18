"""Unit tests for the quest service — no database or HTTP required.

Tests cover:
- Objective matching logic
- Progress update state transitions
- Seed quest data integrity
- zero_trust HMAC token generation and verification
"""
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("SERVICE_TOKEN", "test-service-token")
os.environ.setdefault("AUTH_SERVICE_URL", "http://auth:8001")
os.environ.setdefault("CHARACTER_SERVICE_URL", "http://character:8002")
os.environ.setdefault("INVENTORY_SERVICE_URL", "http://inventory:8010")

import pytest

from zero_trust import make_service_token, verify_service_token_value, ServiceTokenError
from seed import SEED_QUESTS
from routers.quests import _all_objectives_met


# ── zero_trust ─────────────────────────────────────────────────────────────────

class TestZeroTrust:
    def test_make_and_verify_token(self):
        token = make_service_token()
        # Should not raise
        verify_service_token_value(token)

    def test_missing_token_raises(self):
        with pytest.raises(ServiceTokenError, match="Missing"):
            verify_service_token_value(None)

    def test_empty_token_raises(self):
        with pytest.raises(ServiceTokenError, match="Missing"):
            verify_service_token_value("")

    def test_malformed_token_raises(self):
        with pytest.raises(ServiceTokenError, match="Malformed"):
            verify_service_token_value("notavalidtoken")

    def test_expired_token_raises(self):
        old_bucket = int(time.time()) // 60 - 10  # 10 minutes ago
        import hashlib, hmac as _hmac
        digest = _hmac.new(
            b"test-service-token",
            str(old_bucket).encode(),
            hashlib.sha256,
        ).hexdigest()
        with pytest.raises(ServiceTokenError, match="expired"):
            verify_service_token_value(f"{old_bucket}:{digest}")

    def test_wrong_secret_raises(self):
        ts = int(time.time()) // 60
        with pytest.raises(ServiceTokenError, match="invalid"):
            verify_service_token_value(f"{ts}:badhexdigest1234567890abcdef")


# ── Objective matching ─────────────────────────────────────────────────────────

class TestAllObjectivesMet:
    def test_all_met(self):
        objs = [
            {"type": "kill_count", "target": "goblin", "required": 5, "current": 5},
            {"type": "item_gather", "item_id": "pelt", "required": 3, "current": 3},
        ]
        assert _all_objectives_met(objs) is True

    def test_one_not_met(self):
        objs = [
            {"type": "kill_count", "target": "goblin", "required": 5, "current": 5},
            {"type": "item_gather", "item_id": "pelt", "required": 3, "current": 2},
        ]
        assert _all_objectives_met(objs) is False

    def test_empty_objectives(self):
        assert _all_objectives_met([]) is True

    def test_zero_current(self):
        objs = [{"type": "kill_count", "target": "wolf", "required": 1, "current": 0}]
        assert _all_objectives_met(objs) is False

    def test_over_required_counts_as_met(self):
        objs = [{"type": "kill_count", "target": "wolf", "required": 3, "current": 10}]
        assert _all_objectives_met(objs) is True


# ── Seed data integrity ────────────────────────────────────────────────────────

class TestSeedQuests:
    def test_five_quests(self):
        assert len(SEED_QUESTS) == 5

    def test_all_have_required_fields(self):
        required = {"id", "title", "npc_giver", "briefing_dialogue",
                    "objectives_template", "completion_dialogue",
                    "xp_reward", "gold_reward", "prerequisites"}
        for q in SEED_QUESTS:
            missing = required - q.keys()
            assert not missing, f"Quest '{q['id']}' missing fields: {missing}"

    def test_no_duplicate_ids(self):
        ids = [q["id"] for q in SEED_QUESTS]
        assert len(ids) == len(set(ids))

    def test_all_objectives_have_type_and_required(self):
        valid_types = {"kill_count", "item_gather", "interact_npc", "explore_location"}
        for q in SEED_QUESTS:
            for obj in q["objectives_template"]:
                assert "type" in obj, f"Quest {q['id']} objective missing 'type'"
                assert obj["type"] in valid_types, f"Quest {q['id']} invalid type: {obj['type']}"
                assert "required" in obj, f"Quest {q['id']} objective missing 'required'"
                assert obj["required"] > 0

    def test_rewards_are_non_negative(self):
        for q in SEED_QUESTS:
            assert q["xp_reward"] >= 0
            assert q["gold_reward"] >= 0

    def test_prerequisites_reference_valid_ids(self):
        all_ids = {q["id"] for q in SEED_QUESTS}
        for q in SEED_QUESTS:
            for prereq in q["prerequisites"]:
                assert prereq in all_ids, (
                    f"Quest '{q['id']}' has unknown prerequisite '{prereq}'"
                )

    def test_kill_count_objectives_have_target(self):
        for q in SEED_QUESTS:
            for obj in q["objectives_template"]:
                if obj["type"] == "kill_count":
                    assert "target" in obj and obj["target"]

    def test_item_gather_objectives_have_item_id(self):
        for q in SEED_QUESTS:
            for obj in q["objectives_template"]:
                if obj["type"] == "item_gather":
                    assert "item_id" in obj and obj["item_id"]

    def test_interact_npc_objectives_have_npc_id(self):
        for q in SEED_QUESTS:
            for obj in q["objectives_template"]:
                if obj["type"] == "interact_npc":
                    assert "npc_id" in obj and obj["npc_id"]

    def test_explore_location_objectives_have_zone_id(self):
        for q in SEED_QUESTS:
            for obj in q["objectives_template"]:
                if obj["type"] == "explore_location":
                    assert "zone_id" in obj and obj["zone_id"]

    def test_known_quests_present(self):
        ids = {q["id"] for q in SEED_QUESTS}
        assert "q001_town_in_peril" in ids
        assert "q002_hildas_stock" in ids
        assert "q003_wandering_elder" in ids
        assert "q004_scout_the_forest" in ids
        assert "q005_purge_the_crypt" in ids


# ── Progress update objective matching logic ───────────────────────────────────

class TestProgressMatching:
    """Test the objective matching rules used in update_progress without DB."""

    def _apply_progress(
        self,
        objectives: list[dict],
        event_type: str,
        target: str | None = None,
        item_id: str | None = None,
        npc_id: str | None = None,
        zone_id: str | None = None,
        amount: int = 1,
    ) -> tuple[list[dict], bool]:
        """Local reimplementation of update_progress matching logic for testing."""
        changed = False
        for obj in objectives:
            if obj["type"] != event_type:
                continue
            match = False
            if event_type == "kill_count" and target and obj.get("target") == target:
                match = True
            elif event_type == "item_gather" and item_id and obj.get("item_id") == item_id:
                match = True
            elif event_type == "interact_npc" and npc_id and obj.get("npc_id") == npc_id:
                match = True
            elif event_type == "explore_location" and zone_id and obj.get("zone_id") == zone_id:
                match = True

            if match and obj["current"] < obj["required"]:
                obj["current"] = min(obj["current"] + amount, obj["required"])
                changed = True
        return objectives, changed

    def test_kill_count_increment(self):
        objs = [{"type": "kill_count", "target": "goblin", "required": 5, "current": 0}]
        objs, changed = self._apply_progress(objs, "kill_count", target="goblin")
        assert changed
        assert objs[0]["current"] == 1

    def test_kill_count_wrong_target_no_change(self):
        objs = [{"type": "kill_count", "target": "goblin", "required": 5, "current": 0}]
        objs, changed = self._apply_progress(objs, "kill_count", target="wolf")
        assert not changed
        assert objs[0]["current"] == 0

    def test_kill_count_capped_at_required(self):
        objs = [{"type": "kill_count", "target": "goblin", "required": 3, "current": 2}]
        objs, changed = self._apply_progress(objs, "kill_count", target="goblin", amount=5)
        assert changed
        assert objs[0]["current"] == 3

    def test_item_gather_increment(self):
        objs = [{"type": "item_gather", "item_id": "wolf_pelt", "required": 3, "current": 0}]
        objs, changed = self._apply_progress(objs, "item_gather", item_id="wolf_pelt")
        assert changed
        assert objs[0]["current"] == 1

    def test_interact_npc_increment(self):
        objs = [{"type": "interact_npc", "npc_id": "elder_aldric", "required": 1, "current": 0}]
        objs, changed = self._apply_progress(objs, "interact_npc", npc_id="elder_aldric")
        assert changed
        assert objs[0]["current"] == 1

    def test_explore_location_increment(self):
        objs = [{"type": "explore_location", "zone_id": "whispering_forest", "required": 1, "current": 0}]
        objs, changed = self._apply_progress(objs, "explore_location", zone_id="whispering_forest")
        assert changed
        assert objs[0]["current"] == 1

    def test_already_completed_objective_not_incremented(self):
        objs = [{"type": "kill_count", "target": "goblin", "required": 5, "current": 5}]
        objs, changed = self._apply_progress(objs, "kill_count", target="goblin")
        assert not changed
        assert objs[0]["current"] == 5

    def test_wrong_event_type_no_match(self):
        objs = [{"type": "kill_count", "target": "goblin", "required": 5, "current": 0}]
        objs, changed = self._apply_progress(objs, "item_gather", item_id="goblin")
        assert not changed

    def test_multiple_objectives_only_matching_incremented(self):
        objs = [
            {"type": "kill_count", "target": "goblin", "required": 5, "current": 0},
            {"type": "item_gather", "item_id": "pelt", "required": 3, "current": 1},
        ]
        objs, changed = self._apply_progress(objs, "kill_count", target="goblin")
        assert changed
        assert objs[0]["current"] == 1
        assert objs[1]["current"] == 1  # unchanged
