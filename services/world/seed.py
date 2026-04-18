"""Seed initial zone data for AETHERMOOR.

Called once on first startup (idempotent — zones with existing IDs are skipped).
Provides: Starter Town, Whispering Forest, and the Sunken Crypt dungeon.
Tilemaps use minimal Phaser.js / Tiled JSON format with Ground + Collision layers.
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import Biome, NpcTemplate, Zone
from npc_catalogue import get_stat_block


def _make_tilemap(width: int, height: int, collision_tiles: list[int] | None = None) -> dict:
    """Create a minimal Tiled JSON tilemap.

    Ground layer: all tile ID 1 (grass/floor).
    Collision layer: collision_tiles list (flat, len = width * height, 0 = walkable, 1 = blocked).
    """
    ground_data = [1] * (width * height)
    collision_data = collision_tiles if collision_tiles else [0] * (width * height)

    return {
        "version": "1.6",
        "tiledversion": "1.10.2",
        "width": width,
        "height": height,
        "tilewidth": 16,
        "tileheight": 16,
        "infinite": False,
        "layers": [
            {
                "id": 1,
                "name": "Ground",
                "type": "tilelayer",
                "width": width,
                "height": height,
                "x": 0,
                "y": 0,
                "data": ground_data,
                "opacity": 1,
                "visible": True,
            },
            {
                "id": 2,
                "name": "Collision",
                "type": "tilelayer",
                "width": width,
                "height": height,
                "x": 0,
                "y": 0,
                "data": collision_data,
                "opacity": 0,
                "visible": False,
            },
        ],
        "tilesets": [
            {
                "firstgid": 1,
                "source": "aethermoor_tileset.tsj",
            }
        ],
        "renderorder": "right-down",
        "orientation": "orthogonal",
    }


def _border_collision(width: int, height: int) -> list[int]:
    """Make the map border impassable, interior walkable."""
    data = [0] * (width * height)
    for y in range(height):
        for x in range(width):
            if x == 0 or y == 0 or x == width - 1 or y == height - 1:
                data[y * width + x] = 1
    return data


_SEED_ZONES: list[dict] = [
    {
        "id": "starter_town",
        "name": "Millhaven — Starter Town",
        "biome": Biome.TOWN,
        "level_min": 1,
        "level_max": 5,
        "max_players": 200,
        "width": 40,
        "height": 30,
        "spawn_x": 20,
        "spawn_y": 15,
        "npc_templates": [
            {
                "npc_type": "guard",
                "name": "Town Guard",
                "spawn_x": 18,
                "spawn_y": 15,
                "patrol_path": [
                    {"x": 18, "y": 15},
                    {"x": 22, "y": 15},
                    {"x": 22, "y": 18},
                    {"x": 18, "y": 18},
                ],
                "respawn_timer_sec": 30,
            },
            {
                "npc_type": "merchant",
                "name": "Hilda the Merchant",
                "spawn_x": 25,
                "spawn_y": 10,
                "patrol_path": [],  # stationary
                "respawn_timer_sec": 60,
            },
        ],
    },
    {
        "id": "whispering_forest",
        "name": "Whispering Forest",
        "biome": Biome.FOREST,
        "level_min": 3,
        "level_max": 10,
        "max_players": 150,
        "width": 60,
        "height": 60,
        "spawn_x": 5,
        "spawn_y": 5,
        "npc_templates": [
            {
                "npc_type": "wolf",
                "name": "Forest Wolf",
                "spawn_x": 30,
                "spawn_y": 30,
                "patrol_path": [
                    {"x": 30, "y": 30},
                    {"x": 35, "y": 30},
                    {"x": 35, "y": 35},
                    {"x": 30, "y": 35},
                ],
                "respawn_timer_sec": 45,
            },
        ],
    },
    {
        "id": "sunken_crypt_b1",
        "name": "Sunken Crypt — Floor 1",
        "biome": Biome.DUNGEON,
        "level_min": 8,
        "level_max": 15,
        "max_players": 50,
        "width": 30,
        "height": 30,
        "spawn_x": 2,
        "spawn_y": 2,
        "npc_templates": [
            {
                "npc_type": "skeleton",
                "name": "Risen Skeleton",
                "spawn_x": 15,
                "spawn_y": 15,
                "patrol_path": [
                    {"x": 15, "y": 15},
                    {"x": 20, "y": 15},
                    {"x": 20, "y": 20},
                    {"x": 15, "y": 20},
                ],
                "respawn_timer_sec": 20,
            },
        ],
    },
]


async def seed_zones(db: AsyncSession) -> int:
    """Insert seed zones if they don't already exist. Returns count of new zones added."""
    added = 0
    for zone_data in _SEED_ZONES:
        existing = await db.get(Zone, zone_data["id"])
        if existing is not None:
            continue

        npc_templates_data = zone_data.pop("npc_templates", [])
        width = zone_data["width"]
        height = zone_data["height"]
        tilemap = _make_tilemap(width, height, _border_collision(width, height))

        zone = Zone(**zone_data, tilemap=tilemap)
        db.add(zone)
        await db.flush()  # get zone.id

        for tmpl_data in npc_templates_data:
            stats = get_stat_block(tmpl_data["npc_type"])
            tmpl = NpcTemplate(
                zone_id=zone.id,
                hp=stats.hp,
                max_hp=stats.max_hp,
                ac=stats.ac,
                cr=stats.cr,
                weapon=stats.weapon,
                npc_stats=stats.npc_stats,
                gold_drop_min=stats.gold_drop_min,
                gold_drop_max=stats.gold_drop_max,
                is_hostile=stats.is_hostile,
                dialogue=stats.dialogue,
                **tmpl_data,
            )
            db.add(tmpl)

        added += 1

    await db.commit()
    return added
