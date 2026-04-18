"""Unit tests for the world service — no database or Redis required.

Tests pathfinding, collision grid construction, and cache helper logic.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Patch env vars before imports
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")
os.environ.setdefault("SERVICE_TOKEN", "test-token")
os.environ.setdefault("AUTH_SERVICE_URL", "http://auth:8001")
os.environ.setdefault("CHARACTER_SERVICE_URL", "http://character:8002")

import pytest

from pathfinding import CollisionGrid


class TestCollisionGrid:
    def _open_grid(self, w: int = 10, h: int = 10) -> CollisionGrid:
        return CollisionGrid(w, h, [False] * (w * h))

    def test_open_grid_all_walkable(self):
        grid = self._open_grid()
        assert grid.is_walkable(0, 0)
        assert grid.is_walkable(9, 9)
        assert grid.is_walkable(5, 5)

    def test_out_of_bounds_not_walkable(self):
        grid = self._open_grid()
        assert not grid.is_walkable(-1, 0)
        assert not grid.is_walkable(0, -1)
        assert not grid.is_walkable(10, 0)
        assert not grid.is_walkable(0, 10)

    def test_blocked_tile_not_walkable(self):
        blocked = [False] * 100
        blocked[5 * 10 + 5] = True  # tile at (5, 5)
        grid = CollisionGrid(10, 10, blocked)
        assert not grid.is_walkable(5, 5)
        assert grid.is_walkable(4, 5)

    def test_neighbors_open_center(self):
        grid = self._open_grid()
        n = grid.neighbors(5, 5)
        assert set(n) == {(6, 5), (4, 5), (5, 6), (5, 4)}

    def test_neighbors_corner(self):
        grid = self._open_grid()
        n = grid.neighbors(0, 0)
        assert set(n) == {(1, 0), (0, 1)}

    def test_neighbors_excludes_blocked(self):
        blocked = [False] * 100
        blocked[5 * 10 + 6] = True  # (6, 5) blocked
        grid = CollisionGrid(10, 10, blocked)
        n = grid.neighbors(5, 5)
        assert (6, 5) not in n

    def test_next_step_adjacent(self):
        grid = self._open_grid()
        step = grid.next_step(5, 5, 6, 5)
        assert step == (6, 5)

    def test_next_step_same_position_returns_none(self):
        grid = self._open_grid()
        assert grid.next_step(5, 5, 5, 5) is None

    def test_next_step_unreachable_returns_none(self):
        # Build a walled-off target
        blocked = [False] * 100
        # Surround (9, 9) with walls
        blocked[8 * 10 + 9] = True  # (9, 8)
        blocked[9 * 10 + 8] = True  # (8, 9)
        grid = CollisionGrid(10, 10, blocked)
        assert grid.next_step(0, 0, 9, 9) is None

    def test_next_step_navigates_around_obstacle(self):
        """Path from (0,0) to (2,0) with a wall at (1,0)."""
        blocked = [False] * 100
        blocked[0 * 10 + 1] = True  # (1, 0) blocked
        grid = CollisionGrid(10, 10, blocked)
        step = grid.next_step(0, 0, 2, 0)
        # Must go around via y=1 row — first step is (0,1)
        assert step is not None
        assert step != (1, 0)  # must not step into the wall

    def test_next_step_long_path(self):
        grid = self._open_grid()
        step = grid.next_step(0, 0, 9, 9)
        # Should take exactly one step (either right or down)
        assert step in {(1, 0), (0, 1)}

    def test_from_tilemap_no_collision_layer(self):
        tilemap = {"layers": [], "width": 5, "height": 5}
        grid = CollisionGrid.from_tilemap(tilemap, 5, 5)
        assert all(not b for b in grid.blocked)

    def test_from_tilemap_parses_collision_layer(self):
        data = [0] * 25
        data[2 * 5 + 2] = 1  # tile at (2, 2) blocked
        tilemap = {
            "width": 5,
            "height": 5,
            "layers": [
                {
                    "name": "Collision",
                    "type": "tilelayer",
                    "width": 5,
                    "height": 5,
                    "data": data,
                }
            ],
        }
        grid = CollisionGrid.from_tilemap(tilemap, 5, 5)
        assert not grid.is_walkable(2, 2)
        assert grid.is_walkable(0, 0)

    def test_from_tilemap_case_insensitive_layer_name(self):
        data = [1] * 9  # all blocked
        tilemap = {
            "layers": [
                {"name": "COLLISION", "type": "tilelayer", "width": 3, "height": 3, "data": data}
            ]
        }
        grid = CollisionGrid.from_tilemap(tilemap, 3, 3)
        assert all(grid.blocked)


class TestZeroTrust:
    def test_make_and_verify_token(self):
        from zero_trust import make_service_token, verify_service_token_value
        token = make_service_token()
        verify_service_token_value(token)  # should not raise

    def test_missing_token_raises(self):
        from zero_trust import ServiceTokenError, verify_service_token_value
        with pytest.raises(ServiceTokenError, match="Missing"):
            verify_service_token_value(None)

    def test_malformed_token_raises(self):
        from zero_trust import ServiceTokenError, verify_service_token_value
        with pytest.raises(ServiceTokenError, match="Malformed"):
            verify_service_token_value("notavalidtoken")

    def test_wrong_digest_raises(self):
        from zero_trust import ServiceTokenError, verify_service_token_value
        import time
        ts = int(time.time()) // 60
        with pytest.raises(ServiceTokenError, match="invalid"):
            verify_service_token_value(f"{ts}:wrongdigest")
