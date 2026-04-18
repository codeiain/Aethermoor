# AETHERMOOR Player Service

Handles all player character data: creation, stats, world position, and inventory.

Runs on port **8002** inside the Docker network.

---

## API Contract

### Public Endpoints (require user JWT `Authorization: Bearer <token>`)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/players/create` | Create a new character |
| `GET` | `/players/me` | List all characters for authenticated user |
| `GET` | `/players/{characterId}` | Get full character details |
| `DELETE` | `/players/{characterId}` | Soft-delete a character |

### Internal Endpoints (require `X-Service-Token: <hmac-token>`)

| Method | Path | Description |
|--------|------|-------------|
| `PATCH` | `/players/{characterId}/position` | Update world position (called by world service) |
| `PATCH` | `/players/{characterId}/stats` | Update HP/XP/gold after combat (called by combat service) |

### Ops

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness check |

---

## Character Creation

Characters are created using D&D 5e mechanics:

- **Classes**: Fighter, Wizard, Rogue, Cleric, Ranger, Paladin
- **Ability scores**: Generated using 4d6-drop-lowest for each of: STR, DEX, CON, INT, WIS, CHA
- **Hit points**: Hit die maximum + CON modifier (minimum 1)
- **Starting position**: `starter_town` at (0, 0)
- **Slots**: Up to 3 characters per account (slots 1–3)

Hit dice by class: Fighter d10, Wizard d6, Rogue d8, Cleric d8, Ranger d10, Paladin d10.

---

## Authentication

**User endpoints** — the service verifies the user's JWT by calling the Auth Service:

```
POST /auth/verify-service-token
X-Service-Token: <hmac-token>
{ "token": "<user-jwt>" }
```

**Internal endpoints** — protected by HMAC-SHA256 `X-Service-Token`. The token is derived from `SERVICE_TOKEN` (shared secret) and the current 60-second time bucket. One previous bucket is accepted to tolerate clock skew.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SERVICE_TOKEN` | Yes | Shared HMAC secret for inter-service auth |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `AUTH_SERVICE_URL` | Yes | Auth service base URL (e.g. `http://auth:8001`) |

---

## Database Schema

All tables live in the shared `aethermoor` PostgreSQL database.

- **`characters`** — core character data, ability scores, HP, XP, level, gold
- **`character_positions`** — zone ID, X/Y position, respawn point, last seen timestamp
- **`equipment_slots`** — 9 named equipment slots per character (head, chest, legs, feet, main_hand, off_hand, ring_1, ring_2, amulet)
- **`backpack_items`** — up to 24 grid-indexed inventory slots per character

Cross-service user references (`user_id`) are stored as strings — no database-level foreign key to the auth service.

---

## Running Tests

### Unit tests (no database required)

```bash
cd services/character
pip install -r requirements.txt pytest
pytest tests/test_unit.py -v
```

### Integration tests (requires PostgreSQL)

```bash
export DATABASE_URL="postgresql://aethermoor:password@localhost:5432/aethermoor_test"
pip install -r requirements.txt pytest pytest-asyncio httpx
pytest tests/test_integration.py -v
```
