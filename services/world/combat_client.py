"""HTTP client for calling the Combat Service from the World Service.

Uses X-Service-Token (zero-trust). Called by the NPC engage endpoint to initiate
a combat session after the world service has verified the player and NPC state.
"""
import os

import httpx

from zero_trust import make_service_token

_COMBAT_SERVICE_URL = os.environ.get("COMBAT_SERVICE_URL", "http://combat:8007")


class CombatClientError(Exception):
    pass


async def start_combat(
    character_id: str,
    character_name: str,
    character_class: str,
    character_level: int,
    character_hp: int,
    character_max_hp: int,
    character_ac: int,
    character_weapon: str,
    character_stats: dict,
    npc_template_id: str,
    npc_name: str,
    npc_hp: int,
    npc_max_hp: int,
    npc_ac: int,
    npc_weapon: str,
    npc_cr: float,
    npc_stats: dict,
    npc_gold_drop_min: int,
    npc_gold_drop_max: int,
    zone_id: str,
) -> str:
    """Start a combat encounter. Returns the combat_id from the combat service."""
    service_token = make_service_token()
    payload = {
        "character_id": character_id,
        "character_name": character_name,
        "character_class": character_class,
        "character_level": character_level,
        "character_hp": character_hp,
        "character_max_hp": character_max_hp,
        "character_ac": character_ac,
        "character_weapon": character_weapon,
        "character_stats": character_stats,
        "npc_template_id": npc_template_id,
        "npc_name": npc_name,
        "npc_hp": npc_hp,
        "npc_max_hp": npc_max_hp,
        "npc_ac": npc_ac,
        "npc_weapon": npc_weapon,
        "npc_cr": npc_cr,
        "npc_stats": npc_stats,
        "npc_gold_drop_min": npc_gold_drop_min,
        "npc_gold_drop_max": npc_gold_drop_max,
        "zone_id": zone_id,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{_COMBAT_SERVICE_URL}/combat/start",
                json=payload,
                headers={"X-Service-Token": service_token},
            )
    except httpx.RequestError as exc:
        raise CombatClientError(f"Combat service unreachable: {exc}") from exc

    if response.status_code != 201:
        raise CombatClientError(
            f"Combat service returned {response.status_code}: {response.text}"
        )

    return response.json()["combat_id"]
