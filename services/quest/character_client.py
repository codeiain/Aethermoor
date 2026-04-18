"""HTTP client for awarding XP and gold to the character service."""
import os

import httpx

from zero_trust import make_service_token

_CHARACTER_URL = os.environ.get("CHARACTER_SERVICE_URL", "http://character:8002")


class CharacterClientError(Exception):
    pass


async def award_xp_and_gold(character_id: str, xp: int, gold: int) -> None:
    """PATCH /players/{character_id}/stats with delta fields.

    Uses xp_delta and gold_delta so the character service applies the addition
    atomically within its own DB transaction — no read-modify-write race here.
    """
    if xp == 0 and gold == 0:
        return

    payload: dict = {}
    if xp > 0:
        payload["xp_delta"] = xp
    if gold > 0:
        payload["gold_delta"] = gold

    token = make_service_token()
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.patch(
            f"{_CHARACTER_URL}/players/{character_id}/stats",
            json=payload,
            headers={"X-Service-Token": token},
        )

    if resp.status_code not in (200, 204):
        raise CharacterClientError(
            f"character service returned {resp.status_code}: {resp.text}"
        )
