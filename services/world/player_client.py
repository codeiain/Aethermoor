"""HTTP client for updating character positions in the Player Service.

Called when a player enters or exits a zone. Uses X-Service-Token (zero-trust).
"""
import os

import httpx

from zero_trust import make_service_token

_CHARACTER_SERVICE_URL = os.environ.get("CHARACTER_SERVICE_URL", "http://character:8002")


class PlayerServiceError(Exception):
    pass


async def update_character_position(
    character_id: str,
    zone_id: str,
    x: int,
    y: int,
    respawn_zone_id: str | None = None,
    respawn_x: int | None = None,
    respawn_y: int | None = None,
) -> None:
    """Notify the Player Service of a character's new zone and coordinates.

    Fire-and-forget is not used here: we wait for acknowledgment so the caller
    knows the position was persisted before broadcasting it to other players.
    """
    service_token = make_service_token()
    payload: dict = {"zone_id": zone_id, "x": x, "y": y}
    if respawn_zone_id is not None:
        payload["respawn_zone_id"] = respawn_zone_id
    if respawn_x is not None:
        payload["respawn_x"] = respawn_x
    if respawn_y is not None:
        payload["respawn_y"] = respawn_y

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.patch(
                f"{_CHARACTER_SERVICE_URL}/players/{character_id}/position",
                json=payload,
                headers={"X-Service-Token": service_token},
            )
    except httpx.RequestError as exc:
        raise PlayerServiceError(f"Player service unreachable: {exc}") from exc

    if response.status_code not in (200, 204):
        raise PlayerServiceError(
            f"Player service position update failed: {response.status_code}"
        )
