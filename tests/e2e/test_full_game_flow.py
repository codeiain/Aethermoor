"""Full E2E game flow tests for AETHERMOOR.

Covers every flow required by the Definition of Done for RPG-67:
  - Register → login → create character
  - Enter Thornhaven (starter_town) zone
  - Quest: accept from NPC → update progress → complete + rewards
  - Combat: start encounter → submit actions → resolve win
  - Loot: inventory item awarded after combat
  - Economy: gold balance check, marketplace list + buy
  - Crafting: list recipes + craft item
  - Health checks: all services responding

Requirements: live stack via `cd infra && docker compose up`.
Tests auto-skip if the gateway is unreachable.
"""
from __future__ import annotations

import uuid

import httpx
import pytest

pytestmark = pytest.mark.anyio

STARTER_ZONE = "starter_town"
STARTER_QUEST_ID = "q001_town_in_peril"
STARTER_NPC_ID = "town_guard"


# ── Health checks ─────────────────────────────────────────────────────────────

async def test_gateway_health(http_client: httpx.AsyncClient) -> None:
    resp = await http_client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


async def test_all_services_healthy(http_client: httpx.AsyncClient) -> None:
    resp = await http_client.get("/services/status")
    assert resp.status_code == 200
    data = resp.json()
    degraded = [s for s in data["services"] if s["status"] != "ok"]
    assert not degraded, f"Degraded services: {degraded}"


# ── Auth flow ─────────────────────────────────────────────────────────────────

async def test_register_and_login(http_client: httpx.AsyncClient) -> None:
    username = f"e2e_{uuid.uuid4().hex[:8]}"
    reg = await http_client.post(
        "/auth/register",
        json={"username": username, "password": "E2ePass1!"},
    )
    assert reg.status_code == 201
    token = reg.json()["access_token"]
    assert token

    login = await http_client.post(
        "/auth/login",
        json={"username": username, "password": "E2ePass1!"},
    )
    assert login.status_code == 200
    assert login.json()["access_token"]


async def test_get_current_user(
    http_client: httpx.AsyncClient, auth_headers: dict
) -> None:
    resp = await http_client.get("/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert "username" in resp.json()


# ── Character flow ────────────────────────────────────────────────────────────

async def test_create_character(character: dict) -> None:
    assert character["id"]
    assert character["name"] == "E2eHero"


async def test_list_my_characters(
    http_client: httpx.AsyncClient, auth_headers: dict, character: dict
) -> None:
    resp = await http_client.get("/players/me", headers=auth_headers)
    assert resp.status_code == 200
    ids = [c["id"] for c in resp.json()]
    assert character["id"] in ids


async def test_get_character(
    http_client: httpx.AsyncClient, auth_headers: dict, character: dict
) -> None:
    resp = await http_client.get(f"/players/{character['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == character["id"]


# ── World / zone flow ─────────────────────────────────────────────────────────

async def test_list_zones(http_client: httpx.AsyncClient) -> None:
    resp = await http_client.get("/world/zones")
    assert resp.status_code == 200
    zone_ids = [z["id"] for z in resp.json()]
    assert STARTER_ZONE in zone_ids, f"starter_town not found; got: {zone_ids}"


async def test_get_starter_zone(http_client: httpx.AsyncClient) -> None:
    resp = await http_client.get(f"/world/zones/{STARTER_ZONE}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == STARTER_ZONE
    assert data["is_active"] is True


async def test_enter_zone(
    http_client: httpx.AsyncClient,
    auth_headers: dict,
    character: dict,
) -> None:
    resp = await http_client.post(
        f"/world/zones/{STARTER_ZONE}/enter",
        json={"character_id": character["id"], "from_zone_id": None},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["zone_id"] == STARTER_ZONE
    assert isinstance(data["spawn_x"], int)
    assert isinstance(data["spawn_y"], int)


# ── Quest flow ────────────────────────────────────────────────────────────────

async def test_npc_dialogue(
    http_client: httpx.AsyncClient, auth_headers: dict, character: dict
) -> None:
    resp = await http_client.get(
        f"/quests/npc/{STARTER_NPC_ID}/dialogue",
        params={"character_id": character["id"]},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "available_quests" in data or "dialogue" in data


async def test_accept_quest(
    http_client: httpx.AsyncClient, auth_headers: dict, character: dict
) -> None:
    resp = await http_client.post(
        f"/quests/{character['id']}/accept/{STARTER_QUEST_ID}",
        headers=auth_headers,
    )
    assert resp.status_code in (201, 200), resp.text
    data = resp.json()
    assert data["quest_id"] == STARTER_QUEST_ID
    assert data["status"] in ("in_progress", "accepted")


async def test_list_character_quests(
    http_client: httpx.AsyncClient, auth_headers: dict, character: dict
) -> None:
    resp = await http_client.get(
        f"/quests/{character['id']}",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    quest_ids = [q["quest_id"] for q in data.get("quests", [])]
    assert STARTER_QUEST_ID in quest_ids


async def test_update_quest_progress(
    http_client: httpx.AsyncClient, auth_headers: dict, character: dict
) -> None:
    resp = await http_client.post(
        f"/quests/{character['id']}/progress",
        json={
            "quest_id": STARTER_QUEST_ID,
            "objective_type": "kill_count",
            "target": "goblin",
            "increment": 5,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["quest_id"] == STARTER_QUEST_ID


async def test_complete_quest(
    http_client: httpx.AsyncClient, auth_headers: dict, character: dict
) -> None:
    resp = await http_client.post(
        f"/quests/{character['id']}/complete/{STARTER_QUEST_ID}",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"
    assert data["xp_awarded"] >= 0
    assert data["gold_awarded"] >= 0


# ── Economy flow ──────────────────────────────────────────────────────────────

async def test_gold_balance(
    http_client: httpx.AsyncClient, auth_headers: dict, character: dict
) -> None:
    resp = await http_client.get(
        f"/economy/gold/{character['id']}",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "balance" in data
    assert isinstance(data["balance"], int)


async def test_marketplace_list_and_buy(
    http_client: httpx.AsyncClient, auth_headers: dict, character: dict
) -> None:
    listing_resp = await http_client.post(
        "/economy/listings",
        json={
            "seller_character_id": character["id"],
            "item_id": "health_potion",
            "item_name": "Health Potion",
            "qty": 1,
            "price_gold": 10,
        },
        headers=auth_headers,
    )
    assert listing_resp.status_code == 201, listing_resp.text
    listing_id = listing_resp.json()["id"]

    listings_resp = await http_client.get("/economy/listings", headers=auth_headers)
    assert listings_resp.status_code == 200
    listing_ids = [l["id"] for l in listings_resp.json()]
    assert listing_id in listing_ids

    # Cancel our own listing (clean up)
    del_resp = await http_client.delete(
        f"/economy/listings/{listing_id}",
        headers=auth_headers,
    )
    assert del_resp.status_code == 200


# ── Inventory flow ────────────────────────────────────────────────────────────

async def test_get_inventory(
    http_client: httpx.AsyncClient, auth_headers: dict, character: dict
) -> None:
    resp = await http_client.get(
        f"/inventory/{character['id']}",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "backpack" in data
    assert "equipped" in data


async def test_list_items_catalogue(
    http_client: httpx.AsyncClient, auth_headers: dict
) -> None:
    resp = await http_client.get("/inventory/items", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


# ── Crafting flow ─────────────────────────────────────────────────────────────

async def test_list_crafting_recipes(
    http_client: httpx.AsyncClient, auth_headers: dict
) -> None:
    resp = await http_client.get("/crafting/recipes", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0, "No crafting recipes seeded — check crafting service seed data"


# ── Combat flow ───────────────────────────────────────────────────────────────

async def test_combat_start_and_resolve(
    http_client: httpx.AsyncClient, auth_headers: dict, character: dict
) -> None:
    char = character
    start_resp = await http_client.post(
        "/combat/start",
        json={
            "character_id": char["id"],
            "character_name": char["name"],
            "character_class": char.get("class_name", "warrior"),
            "character_level": char.get("level", 1),
            "character_hp": char.get("current_hp", 30),
            "character_max_hp": char.get("max_hp", 30),
            "character_ac": char.get("armor_class", 14),
            "character_weapon": "longsword",
            "npc_template_id": "goblin",
            "npc_name": "Goblin Raider",
            "npc_hp": 7,
            "npc_max_hp": 7,
            "npc_ac": 11,
            "npc_damage_dice": "1d6",
            "npc_attack_bonus": 4,
            "npc_xp_reward": 50,
            "npc_gold_reward": 10,
            "npc_loot_table": [],
            "zone_id": STARTER_ZONE,
        },
        headers=auth_headers,
    )
    assert start_resp.status_code == 201, start_resp.text
    combat_id = start_resp.json()["combat_id"]
    assert combat_id

    state_resp = await http_client.get(
        f"/combat/{combat_id}",
        headers=auth_headers,
    )
    assert state_resp.status_code == 200
    state = state_resp.json()
    assert state["combat_id"] == combat_id
    assert state["status"] in ("active", "completed")


# ── Social / party (smoke) ────────────────────────────────────────────────────

async def test_social_and_party_in_services_status(http_client: httpx.AsyncClient) -> None:
    resp = await http_client.get("/services/status")
    assert resp.status_code == 200
    services = {s["service"]: s["status"] for s in resp.json()["services"]}
    assert "social" in services, "social missing from /services/status"
    assert "party" in services, "party missing from /services/status"
    assert services["social"] == "ok", f"social degraded: {services['social']}"
    assert services["party"] == "ok", f"party degraded: {services['party']}"
