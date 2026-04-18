"""HTTP client for awarding item rewards via the inventory service."""
import os

import httpx

from zero_trust import make_service_token

_INVENTORY_URL = os.environ.get("INVENTORY_SERVICE_URL", "http://inventory:8010")


class InventoryClientError(Exception):
    pass


async def award_item(character_id: str, item_id: str, quantity: int = 1) -> str:
    """POST /inventory/loot to grant an item reward.

    Returns the placement result string ("equipped" | "backpack" | "stacked").
    Raises InventoryClientError on non-2xx or if result is "rejected".
    """
    token = make_service_token()
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            f"{_INVENTORY_URL}/inventory/loot",
            json={"character_id": character_id, "item_id": item_id, "quantity": quantity},
            headers={"X-Service-Token": token},
        )

    if resp.status_code not in (200, 201):
        raise InventoryClientError(
            f"inventory service returned {resp.status_code}: {resp.text}"
        )

    data = resp.json()
    result = data.get("result", "unknown")
    if result == "rejected":
        raise InventoryClientError(
            f"inventory rejected item '{item_id}' for character '{character_id}': backpack full"
        )
    return result
