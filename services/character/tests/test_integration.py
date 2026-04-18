"""Integration tests for the player service.

Runs against real PostgreSQL — no mocks for DB layer.
Auth service calls are mocked (auth service not running in unit test context).
"""
import sys
import os
import uuid
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from zero_trust import make_service_token

# A fake user returned by the mocked auth verification
FAKE_USER = {"user_id": str(uuid.uuid4()), "username": "testplayer"}
FAKE_USER_2 = {"user_id": str(uuid.uuid4()), "username": "otherplayer"}


def _auth_mock(user: dict):
    """Return a patch target that resolves verify_user_jwt to the given user."""
    return patch(
        "routers.players.verify_user_jwt",
        new=AsyncMock(return_value=user),
    )


@pytest.mark.asyncio
class TestHealthEndpoint:
    async def test_health(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok", "service": "player"}


@pytest.mark.asyncio
class TestCreateCharacter:
    async def test_create_character_success(self, client):
        with _auth_mock(FAKE_USER):
            resp = await client.post(
                "/players/create",
                json={"name": "Aldric", "character_class": "Fighter", "slot": 1},
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Aldric"
        assert data["character_class"] == "Fighter"
        assert data["slot"] == 1
        assert data["level"] == 1
        assert data["xp"] == 0
        assert data["gold"] == 0
        assert data["current_hp"] == data["max_hp"]
        # D&D ability scores present and in range
        scores = data["ability_scores"]
        for key in ("strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"):
            assert 3 <= scores[key] <= 18
        # Position initialised
        pos = data["position"]
        assert pos["zone_id"] == "starter_town"
        assert pos["x"] == 0
        assert pos["y"] == 0
        # Equipment slots present (9 slots)
        assert len(data["equipment"]) == 9
        # Backpack is empty
        assert data["backpack"] == []

    async def test_duplicate_slot_rejected(self, client):
        with _auth_mock(FAKE_USER):
            await client.post(
                "/players/create",
                json={"name": "Aldric", "character_class": "Fighter", "slot": 1},
                headers={"Authorization": "Bearer fake-token"},
            )
            resp = await client.post(
                "/players/create",
                json={"name": "Merlin", "character_class": "Wizard", "slot": 1},
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code == 409

    async def test_max_three_characters(self, client):
        with _auth_mock(FAKE_USER):
            for slot, cls in [(1, "Fighter"), (2, "Wizard"), (3, "Rogue")]:
                r = await client.post(
                    "/players/create",
                    json={"name": f"Char{slot}", "character_class": cls, "slot": slot},
                    headers={"Authorization": "Bearer fake-token"},
                )
                assert r.status_code == 201
            # Fourth character should fail
            resp = await client.post(
                "/players/create",
                json={"name": "Overflow", "character_class": "Cleric", "slot": 1},
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code in (400, 409)

    async def test_invalid_slot_rejected(self, client):
        with _auth_mock(FAKE_USER):
            resp = await client.post(
                "/players/create",
                json={"name": "Bad", "character_class": "Fighter", "slot": 4},
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code == 422

    async def test_invalid_class_rejected(self, client):
        with _auth_mock(FAKE_USER):
            resp = await client.post(
                "/players/create",
                json={"name": "Bad", "character_class": "Barbarian", "slot": 1},
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code == 422

    async def test_invalid_name_rejected(self, client):
        with _auth_mock(FAKE_USER):
            resp = await client.post(
                "/players/create",
                json={"name": "A", "character_class": "Fighter", "slot": 1},
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code == 422

    async def test_no_auth_rejected(self, client):
        resp = await client.post(
            "/players/create",
            json={"name": "Aldric", "character_class": "Fighter", "slot": 1},
        )
        assert resp.status_code == 403  # HTTPBearer returns 403 when no credentials


@pytest.mark.asyncio
class TestListMyCharacters:
    async def test_empty_list(self, client):
        with _auth_mock(FAKE_USER):
            resp = await client.get("/players/me", headers={"Authorization": "Bearer fake-token"})
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_lists_only_own_characters(self, client):
        # Create a character for user 1
        with _auth_mock(FAKE_USER):
            await client.post(
                "/players/create",
                json={"name": "UserOneChar", "character_class": "Fighter", "slot": 1},
                headers={"Authorization": "Bearer fake-token"},
            )
        # Create a character for user 2
        with _auth_mock(FAKE_USER_2):
            await client.post(
                "/players/create",
                json={"name": "UserTwoChar", "character_class": "Wizard", "slot": 1},
                headers={"Authorization": "Bearer fake-token"},
            )

        # User 1 should only see their own character
        with _auth_mock(FAKE_USER):
            resp = await client.get("/players/me", headers={"Authorization": "Bearer fake-token"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "UserOneChar"


@pytest.mark.asyncio
class TestGetCharacter:
    async def test_get_own_character(self, client):
        with _auth_mock(FAKE_USER):
            create_resp = await client.post(
                "/players/create",
                json={"name": "Aldric", "character_class": "Paladin", "slot": 1},
                headers={"Authorization": "Bearer fake-token"},
            )
            char_id = create_resp.json()["id"]
            resp = await client.get(
                f"/players/{char_id}",
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code == 200
        assert resp.json()["id"] == char_id

    async def test_get_other_users_character_forbidden(self, client):
        with _auth_mock(FAKE_USER):
            create_resp = await client.post(
                "/players/create",
                json={"name": "Aldric", "character_class": "Ranger", "slot": 1},
                headers={"Authorization": "Bearer fake-token"},
            )
            char_id = create_resp.json()["id"]

        with _auth_mock(FAKE_USER_2):
            resp = await client.get(
                f"/players/{char_id}",
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code == 403

    async def test_get_nonexistent_character(self, client):
        with _auth_mock(FAKE_USER):
            resp = await client.get(
                f"/players/{uuid.uuid4()}",
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code == 404


@pytest.mark.asyncio
class TestDeleteCharacter:
    async def test_delete_own_character(self, client):
        with _auth_mock(FAKE_USER):
            create_resp = await client.post(
                "/players/create",
                json={"name": "Doomed", "character_class": "Rogue", "slot": 1},
                headers={"Authorization": "Bearer fake-token"},
            )
            char_id = create_resp.json()["id"]
            resp = await client.delete(
                f"/players/{char_id}",
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code == 200
        assert "deleted" in resp.json()["message"].lower()

    async def test_deleted_character_not_visible(self, client):
        with _auth_mock(FAKE_USER):
            create_resp = await client.post(
                "/players/create",
                json={"name": "Gone", "character_class": "Cleric", "slot": 1},
                headers={"Authorization": "Bearer fake-token"},
            )
            char_id = create_resp.json()["id"]
            await client.delete(
                f"/players/{char_id}",
                headers={"Authorization": "Bearer fake-token"},
            )
            list_resp = await client.get("/players/me", headers={"Authorization": "Bearer fake-token"})
        assert all(c["id"] != char_id for c in list_resp.json())


@pytest.mark.asyncio
class TestInternalPositionUpdate:
    async def _create_char(self, client) -> str:
        with _auth_mock(FAKE_USER):
            r = await client.post(
                "/players/create",
                json={"name": "Wanderer", "character_class": "Ranger", "slot": 1},
                headers={"Authorization": "Bearer fake-token"},
            )
        return r.json()["id"]

    async def test_update_position(self, client):
        char_id = await self._create_char(client)
        service_token = make_service_token()
        resp = await client.patch(
            f"/players/{char_id}/position",
            json={"zone_id": "dungeon_1", "x": 42, "y": 17},
            headers={"X-Service-Token": service_token},
        )
        assert resp.status_code == 200

        # Verify position updated
        with _auth_mock(FAKE_USER):
            detail = await client.get(
                f"/players/{char_id}",
                headers={"Authorization": "Bearer fake-token"},
            )
        pos = detail.json()["position"]
        assert pos["zone_id"] == "dungeon_1"
        assert pos["x"] == 42
        assert pos["y"] == 17

    async def test_position_update_requires_service_token(self, client):
        char_id = await self._create_char(client)
        resp = await client.patch(
            f"/players/{char_id}/position",
            json={"zone_id": "dungeon_1", "x": 0, "y": 0},
        )
        assert resp.status_code == 401


@pytest.mark.asyncio
class TestInternalStatsUpdate:
    async def _create_char(self, client) -> str:
        with _auth_mock(FAKE_USER):
            r = await client.post(
                "/players/create",
                json={"name": "Battler", "character_class": "Fighter", "slot": 1},
                headers={"Authorization": "Bearer fake-token"},
            )
        return r.json()["id"]

    async def test_update_xp_levels_up(self, client):
        char_id = await self._create_char(client)
        service_token = make_service_token()
        resp = await client.patch(
            f"/players/{char_id}/stats",
            json={"xp": 300},  # level 2 threshold
            headers={"X-Service-Token": service_token},
        )
        assert resp.status_code == 200

        with _auth_mock(FAKE_USER):
            detail = await client.get(
                f"/players/{char_id}",
                headers={"Authorization": "Bearer fake-token"},
            )
        data = detail.json()
        assert data["xp"] == 300
        assert data["level"] == 2

    async def test_update_hp(self, client):
        char_id = await self._create_char(client)
        service_token = make_service_token()
        resp = await client.patch(
            f"/players/{char_id}/stats",
            json={"current_hp": 1},
            headers={"X-Service-Token": service_token},
        )
        assert resp.status_code == 200

    async def test_stats_update_requires_service_token(self, client):
        char_id = await self._create_char(client)
        resp = await client.patch(
            f"/players/{char_id}/stats",
            json={"current_hp": 0},
        )
        assert resp.status_code == 401
