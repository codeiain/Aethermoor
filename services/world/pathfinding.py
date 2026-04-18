"""Simple A* pathfinding for NPC patrol movement.

Design constraints (Raspberry Pi aware):
- Grid-based 4-directional movement (no diagonals — matches Zelda-style tile movement)
- Uses heapq for the open set — no numpy, no heavy dependencies
- Early-exit on adjacent-tile patrol steps (NPCs move 1 tile/sec, so we only need
  the *next step*, not the full path, on each tick)
- Obstacle detection via a flat collision array (from the zone's tilemap JSONB)

Collision layer convention (Tiled / Phaser.js):
  - Tile ID 0 = empty / walkable
  - Any non-zero tile ID in the "Collision" layer = blocked

Usage:
    grid = CollisionGrid.from_tilemap(zone.tilemap, zone.width, zone.height)
    next_x, next_y = grid.next_step(from_x=5, from_y=3, to_x=10, to_y=7)
"""
from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from typing import Any


@dataclass(order=True)
class _Node:
    f: float
    g: float = field(compare=False)
    x: int = field(compare=False)
    y: int = field(compare=False)
    parent: "_Node | None" = field(compare=False, default=None)


class CollisionGrid:
    """Walkability grid built from a Phaser.js / Tiled JSON tilemap.

    Attributes:
        width: tile columns
        height: tile rows
        blocked: flat bool array; blocked[y * width + x] = True if unwalkable
    """

    def __init__(self, width: int, height: int, blocked: list[bool]) -> None:
        self.width = width
        self.height = height
        self.blocked = blocked

    @classmethod
    def from_tilemap(cls, tilemap: dict[str, Any], width: int, height: int) -> "CollisionGrid":
        """Parse a Phaser.js / Tiled JSON tilemap and extract the collision layer.

        Looks for a layer named "Collision" (case-insensitive). If not found,
        all tiles are treated as walkable (permissive default for zones without
        explicit collision data).
        """
        blocked = [False] * (width * height)

        layers: list[dict] = tilemap.get("layers", [])
        collision_layer: dict | None = None
        for layer in layers:
            if layer.get("name", "").lower() == "collision" and layer.get("type") == "tilelayer":
                collision_layer = layer
                break

        if collision_layer is None:
            return cls(width, height, blocked)

        data: list[int] = collision_layer.get("data", [])
        for i, tile_id in enumerate(data):
            if i < len(blocked) and tile_id != 0:
                blocked[i] = True

        return cls(width, height, blocked)

    def is_walkable(self, x: int, y: int) -> bool:
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return False
        return not self.blocked[y * self.width + x]

    def neighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        """4-directional neighbors that are walkable."""
        candidates = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        return [(nx, ny) for nx, ny in candidates if self.is_walkable(nx, ny)]

    def next_step(
        self, from_x: int, from_y: int, to_x: int, to_y: int
    ) -> tuple[int, int] | None:
        """Return the next (x, y) step on the shortest path from (from_x, from_y)
        to (to_x, to_y), or None if no path exists or already at destination.

        Implements A* with Manhattan distance heuristic.
        Capped at 512 nodes expanded to keep per-tick cost bounded on the Pi.
        """
        if (from_x, from_y) == (to_x, to_y):
            return None

        if not self.is_walkable(to_x, to_y):
            return None

        def h(x: int, y: int) -> float:
            return abs(x - to_x) + abs(y - to_y)

        start = _Node(f=h(from_x, from_y), g=0.0, x=from_x, y=from_y)
        open_heap: list[_Node] = [start]
        visited: set[tuple[int, int]] = set()
        expanded = 0
        MAX_EXPAND = 512

        while open_heap and expanded < MAX_EXPAND:
            current = heapq.heappop(open_heap)
            pos = (current.x, current.y)
            if pos in visited:
                continue
            visited.add(pos)
            expanded += 1

            if pos == (to_x, to_y):
                # Walk back to find the first step
                node: "_Node | None" = current
                while node and node.parent and (node.parent.x, node.parent.y) != (from_x, from_y):
                    node = node.parent
                if node and node.parent:
                    return (node.x, node.y)
                return (current.x, current.y)

            for nx, ny in self.neighbors(current.x, current.y):
                if (nx, ny) not in visited:
                    g = current.g + 1.0
                    f = g + h(nx, ny)
                    heapq.heappush(open_heap, _Node(f=f, g=g, x=nx, y=ny, parent=current))

        return None
