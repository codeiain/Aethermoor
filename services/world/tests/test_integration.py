"""Integration tests for the world service.

Runs against real PostgreSQL and Redis — no mocks for DB or cache layers.
Auth service JWT verification is mocked (auth service not running here).
Player service position updates are mocked (character service not running here).
"""
import os
import sys
import uuid
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from zero_trust import make_service_token

FAKE_USER = {"user_id": str(uuid.uuid4()), "username": "world_tester"}
FAKE_CHAR_ID = str(uuid.uuid4())
FAKE_CHAR_ID_2 = str(uuid.uuid4())


def _auth_mock(user: dict):
    return patch(
        "routers.zones.verify_user_jwt",
        new=AsyncMock(return_value=user),
    )


def _player_client_mock():
    return patch(
        "routers.zones.update_character_position",
        new=AsyncMock(return_value=None),
    )


# ── Health ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
class TestHealth:
    async def test_health(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok", "service": "world"}


# ── Zone listing ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
class TestListZones:
    async def test_empty_before_seed(self, client):
        resp = await client.get("/world/zones")
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_lists_seeded_zones(self, seeded_client):
        resp = await seeded_client.get("/world/zones")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3
        zone_ids = {z["id"] for z in data}
        assert "starter_town" in zone_ids
        assert "whispering_forest" in zone_ids
        assert "sunken_crypt_b1" in zone_ids

    async def test_zone_summary_has_no_tilemap(self, seeded_client):
        resp = await seeded_client.get("/world/zones")
        data = resp.json()
        for zone in data:
            assert "tilemap" not in zone

    async def test_zone_summary_has_capacity_info(self, seeded_client):
        resp = await seeded_client.get("/world/zones")
        zone = next(z for z in resp.json() if z["id"] == "starter_town")
        assert "current_players" in zone
        assert "max_players" in zone
        assert zone["current_players"] == 0


# ── Zone detail ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
class TestGetZone:
    async def test_zone_detail_includes_tilemap(self, seeded_client):
        resp = await seeded_client.get("/world/zones/starter_town")
        assert resp.status_code == 200
        data = resp.json()
        assert "tilemap" in data
        tilemap = data["tilemap"]
        assert "layers" in tilemap
        assert tilemap["width"] == 40
        assert tilemap["height"] == 30

    async def test_zone_detail_includes_npc_templates(self, seeded_client):
        resp = await seeded_client.get("/world/zones/starter_town")
        data = resp.json()
        assert "npc_templates" in data
        assert len(data["npc_templates"]) >= 1
        npc = data["npc_templates"][0]
        assert "id" in npc
        assert "npc_type" in npc
        assert "patrol_path" in npc

    async def test_nonexistent_zone_404(self, seeded_client):
        resp = await seeded_client.get("/world/zones/does_not_exist")
        assert resp.status_code == 404


# ── Zone entry / exit ────────────────────────────────────────────────────────

@pytest.mark.asyncio
class TestZoneEnterExit:
    def _service_headers(self):
        return {"X-Service-Token": make_service_token()}

    async def test_enter_zone_succeeds(self, seeded_client):
        with _player_client_mock():
            resp = await seeded_client.post(
                "/world/zones/starter_town/enter",
                json={"character_id": FAKE_CHAR_ID},
                headers=self._service_headers(),
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["zone_id"] == "starter_town"
        assert data["current_players"] == 1
        assert data["spawn_x"] == 20
        assert data["spawn_y"] == 15

    async def test_enter_zone_increments_count(self, seeded_client):
        with _player_client_mock():
            await seeded_client.post(
                "/world/zones/starter_town/enter",
                json={"character_id": FAKE_CHAR_ID},
                headers=self._service_headers(),
            )
            resp2 = await seeded_client.post(
                "/world/zones/starter_town/enter",
                json={"character_id": FAKE_CHAR_ID_2},
                headers=self._service_headers(),
            )
        data = resp2.json()
        assert data["current_players"] == 2

    async def test_exit_zone_decrements_count(self, seeded_client):
        with _player_client_mock():
            await seeded_client.post(
                "/world/zones/starter_town/enter",
                json={"character_id": FAKE_CHAR_ID},
                headers=self._service_headers(),
            )
        resp_exit = await seeded_client.post(
            "/world/zones/starter_town/exit",
            json={"character_id": FAKE_CHAR_ID},
            headers=self._service_headers(),
        )
        assert resp_exit.status_code == 200

        resp_list = await seeded_client.get("/world/zones/starter_town")
        assert resp_list.json()["current_players"] == 0

    async def test_enter_requires_service_token(self, seeded_client):
        resp = await seeded_client.post(
            "/world/zones/starter_town/enter",
            json={"character_id": FAKE_CHAR_ID},
        )
        assert resp.status_code == 401

    async def test_exit_requires_service_token(self, seeded_client):
        resp = await seeded_client.post(
            "/world/zones/starter_town/exit",
            json={"character_id": FAKE_CHAR_ID},
        )
        assert resp.status_code == 401

    async def test_enter_nonexistent_zone_404(self, seeded_client):
        with _player_client_mock():
            resp = await seeded_client.post(
                "/world/zones/ghost_zone/enter",
                json={"character_id": FAKE_CHAR_ID},
                headers=self._service_headers(),
            )
        assert resp.status_code == 404


# ── Nearby players ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
class TestNearbyPlayers:
    def _service_headers(self):
        return {"X-Service-Token": make_service_token()}

    async def test_nearby_players_empty(self, seeded_client):
        with _auth_mock(FAKE_USER):
            resp = await seeded_client.get(
                "/world/zones/starter_town/players?x=20&y=15",
                headers={"Authorization": "Bearer fake-token"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 0
        assert data["players"] == []

    async def test_nearby_players_within_radius(self, seeded_client):
        with _player_client_mock():
            await seeded_client.post(
                "/world/zones/starter_town/enter",
                json={"character_id": FAKE_CHAR_ID},
                headers=self._service_headers(),
            )
        with _auth_mock(FAKE_USER):
            resp = await seeded_client.get(
                "/world/zones/starter_town/players?x=20&y=15",
                headers={"Authorization": "Bearer fake-token"},
            )
        data = resp.json()
        # Player entered at spawn (20, 15) — should be within radius of (20, 15)
        assert data["count"] >= 1
        char_ids = {p["character_id"] for p in data["players"]}
        assert FAKE_CHAR_ID in char_ids

    async def test_nearby_players_requires_auth(self, seeded_client):
        resp = await seeded_client.get("/world/zones/starter_town/players?x=0&y=0")
        assert resp.status_code == 403


# ── NPC state ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
class TestNpcState:
    def _service_headers(self):
        return {"X-Service-Token": make_service_token()}

    async def test_get_zone_npcs(self, seeded_client):
        resp = await seeded_client.get("/world/zones/starter_town/npcs")
        assert resp.status_code == 200
        data = resp.json()
        assert data["zone_id"] == "starter_town"
        assert isinstance(data["npcs"], list)

    async def test_kill_npc_transitions_to_respawning(self, seeded_client, db_session):
        from models import NpcTemplate
        from sqlalchemy import select

        result = await db_session.execute(
            select(NpcTemplate).where(NpcTemplate.zone_id == "starter_town")
        )
        tmpl = result.scalars().first()
        assert tmpl is not None

        resp = await seeded_client.post(
            "/world/npcs/kill",
            json={"npc_id": tmpl.id, "zone_id": "starter_town"},
            headers=self._service_headers(),
        )
        assert resp.status_code == 200

        import cache as redis_cache
        state = await redis_cache.get_npc_state("starter_town", tmpl.id)
        assert state is not None
        assert state["state"] == redis_cache.NPC_STATE_RESPAWNING

    async def test_kill_npc_requires_service_token(self, seeded_client, db_session):
        from models import NpcTemplate
        from sqlalchemy import select

        result = await db_session.execute(
            select(NpcTemplate).where(NpcTemplate.zone_id == "starter_town")
        )
        tmpl = result.scalars().first()

        resp = await seeded_client.post(
            "/world/npcs/kill",
            json={"npc_id": tmpl.id, "zone_id": "starter_town"},
        )
        assert resp.status_code == 401


# ── NPC tick ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
class TestNpcTick:
    def _service_headers(self):
        return {"X-Service-Token": make_service_token()}

    async def test_tick_initialises_npc_state(self, seeded_client):
        resp = await seeded_client.post(
            "/world/zones/starter_town/npcs/tick",
            headers=self._service_headers(),
        )
        assert resp.status_code == 200

        import cache as redis_cache
        from models import NpcTemplate
        from sqlalchemy import select

        # Can't use seeded_client's db_session directly — use a fresh query
        # We just verify the endpoint ran without error

    async def test_tick_requires_service_token(self, seeded_client):
        resp = await seeded_client.post("/world/zones/starter_town/npcs/tick")
        assert resp.status_code == 401


# ── Fishing dock soft cap ────────────────────────────────────────────────────

@pytest.mark.asyncio
class TestFishingDock:
    async def test_fishing_dock_under_cap(self):
        import cache as redis_cache
        result = await redis_cache.fishing_dock_enter("starter_town", "dock_1")
        assert result is True

    async def test_fishing_dock_at_cap_rejected(self):
        import cache as redis_cache
        # Fill the dock to cap
        for _ in range(redis_cache.FISHING_DOCK_SOFT_CAP):
            await redis_cache.fishing_dock_enter("starter_town", "dock_2")
        # One more should be rejected
        result = await redis_cache.fishing_dock_enter("starter_town", "dock_2")
        assert result is False

    async def test_fishing_dock_exit_frees_slot(self):
        import cache as redis_cache
        for _ in range(redis_cache.FISHING_DOCK_SOFT_CAP):
            await redis_cache.fishing_dock_enter("starter_town", "dock_3")
        # Should be full
        assert not await redis_cache.fishing_dock_enter("starter_town", "dock_3")
        # Exit one
        await redis_cache.fishing_dock_exit("starter_town", "dock_3")
        # Now should succeed
        assert await redis_cache.fishing_dock_enter("starter_town", "dock_3")


# ── World events ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
class TestWorldEvents:
    async def test_list_active_events_empty(self, client):
        resp = await client.get("/world/events")
        assert resp.status_code == 200
        assert resp.json()["events"] == []


# ── Live config ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
class TestLiveConfig:
    def _service_headers(self):
        return {"X-Service-Token": make_service_token()}

    async def test_get_default_config(self, client):
        resp = await client.get(
            "/world/admin/config/npc_respawn_default_sec",
            headers=self._service_headers(),
        )
        assert resp.status_code == 200
        assert resp.json()["value"] == "30"

    async def test_update_config_no_restart_required(self, client):
        resp = await client.put(
            "/world/admin/config/npc_respawn_default_sec",
            json={"value": "60"},
            headers=self._service_headers(),
        )
        assert resp.status_code == 200
        assert resp.json()["value"] == "60"

        # Verify the new value is read back
        resp2 = await client.get(
            "/world/admin/config/npc_respawn_default_sec",
            headers=self._service_headers(),
        )
        assert resp2.json()["value"] == "60"

    async def test_config_endpoints_require_service_token(self, client):
        resp = await client.get("/world/admin/config/npc_respawn_default_sec")
        assert resp.status_code == 401
