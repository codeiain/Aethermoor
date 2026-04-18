"""HTTP client for fetching character combat stats from the Character Service.

Uses X-Service-Token (zero-trust). Called by the NPC engage endpoint to get
the player's ability scores, HP, AC, and weapon before starting combat.
"""
import os

import httpx

from zero_trust import make_service_token

_CHARACTER_SERVICE_URL = os.environ.get("CHARACTER_SERVICE_URL", "http://character:8002")

# Maps main_hand item_id prefixes/exact values to combat service WeaponType strings.
# Unknown item_ids fall back to "longsword" (common melee default).
_ITEM_TO_WEAPON: dict[str, str] = {
    "basic_sword": "longsword",
    "iron_sword": "longsword",
    "greatsword": "greatsword",
    "dagger": "dagger",
    "iron_dagger": "dagger",
    "handaxe": "handaxe",
    "greataxe": "greataxe",
    "shortbow": "shortbow",
    "longbow": "longbow",
    "hand_crossbow": "hand_crossbow",
    "quarterstaff": "quarterstaff",
    "iron_staff": "quarterstaff",
    "arcane_staff": "arcane_staff",
    "shortsword": "shortsword",
}
_DEFAULT_WEAPON = "longsword"


class CharacterClientError(Exception):
    pass


def _item_id_to_weapon(item_id: str | None) -> str:
    if item_id is None:
        return _DEFAULT_WEAPON
    weapon = _ITEM_TO_WEAPON.get(item_id)
    if weapon:
        return weapon
    # Substring fallback
    lower = item_id.lower()
    for key, wtype in _ITEM_TO_WEAPON.items():
        if key in lower:
            return wtype
    return _DEFAULT_WEAPON


async def get_combat_stats(character_id: str, user_id: str) -> dict:
    """Fetch a character's combat stats for initiating a battle.

    Returns a dict with keys: name, character_class, level, current_hp, max_hp,
    ac, weapon, stats (dict of ability scores).

    Raises CharacterClientError on network errors or unexpected responses.
    """
    service_token = make_service_token()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{_CHARACTER_SERVICE_URL}/players/{character_id}/combat-stats",
                params={"user_id": user_id},
                headers={"X-Service-Token": service_token},
            )
    except httpx.RequestError as exc:
        raise CharacterClientError(f"Character service unreachable: {exc}") from exc

    if response.status_code == 404:
        raise CharacterClientError(f"Character {character_id} not found")
    if response.status_code == 403:
        raise CharacterClientError("Character does not belong to the requesting user")
    if response.status_code != 200:
        raise CharacterClientError(
            f"Character service returned {response.status_code}: {response.text}"
        )

    return response.json()
