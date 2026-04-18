"""HTTP client for calling the Character Service internal backpack endpoints."""
import os

import httpx

from zero_trust import make_service_token

_CHARACTER_SERVICE_URL = os.environ.get("CHARACTER_SERVICE_URL", "http://character:8002")


class CharacterClientError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


async def get_backpack(character_id: str) -> list[dict]:
    """Fetch the character's backpack items from the character service.

    Returns a list of {slot_index, item_id, quantity} dicts.
    """
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get(
            f"{_CHARACTER_SERVICE_URL}/players/{character_id}/backpack",
            headers={"X-Service-Token": make_service_token()},
        )
    if resp.status_code != 200:
        _raise(resp)
    return resp.json()["items"]


async def apply_craft(
    character_id: str,
    items_to_remove: list[dict],
    items_to_add: list[dict],
) -> None:
    """Atomically deduct materials and add crafted result via the character service."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            f"{_CHARACTER_SERVICE_URL}/players/{character_id}/backpack/apply-craft",
            json={"items_to_remove": items_to_remove, "items_to_add": items_to_add},
            headers={"X-Service-Token": make_service_token()},
        )
    if resp.status_code != 200:
        _raise(resp)


def _raise(resp: httpx.Response) -> None:
    try:
        detail = resp.json().get("detail", resp.text)
    except Exception:
        detail = resp.text
    raise CharacterClientError(resp.status_code, detail)
