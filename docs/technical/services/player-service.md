---
tags:
  - player
  - character
  - stats
---

# Player (Character) Service

**Port:** 8002  
**Language:** Python 3.12 / FastAPI  
**Database:** PostgreSQL 16

Manages all player character data: creation, D&D stats, world position, equipment, and backpack.

## Responsibilities

- Character creation with D&D 5e mechanics (4d6-drop-lowest ability scores)
- Per-account character slot management (max 3 characters per user)
- Character stats: HP, XP, level, gold
- World position tracking (zone, tile X/Y, respawn point)
- Equipment slots and backpack inventory (slots, not real item logic — items are future)

## API Endpoints

### Public (require `Authorization: Bearer <JWT>`)

| Method | Path | Description |
|---|---|---|
| `POST` | `/players/create` | Create a new character |
| `GET` | `/players/me` | List all characters for the authenticated user |
| `GET` | `/players/{characterId}` | Full character detail including position and equipment |
| `DELETE` | `/players/{characterId}` | Soft-delete a character |

### Internal (require `X-Service-Token`)

| Method | Path | Description |
|---|---|---|
| `PATCH` | `/players/{characterId}/position` | Update zone position (called by world service on zone enter/exit) |
| `PATCH` | `/players/{characterId}/stats` | Update HP/XP/gold after combat (called by combat service) |

### Ops

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness probe |

## Character Creation

D&D 5e mechanics applied server-side:

- **Classes**: Fighter, Wizard, Rogue, Cleric, Ranger, Paladin
- **Ability scores**: 4d6-drop-lowest for each of STR, DEX, CON, INT, WIS, CHA
- **Hit points**: Hit die maximum + CON modifier (minimum 1)
- **Starting position**: `starter_town` at tile (0, 0)
- **Slots**: 1–3 per account; `slot` field is unique per user

| Class | Hit Die |
|---|---|
| Fighter | d10 |
| Paladin | d10 |
| Ranger | d10 |
| Cleric | d8 |
| Rogue | d8 |
| Wizard | d6 |

## Authentication

User JWT is verified by calling the Auth Service:

```
POST /auth/verify-service-token
X-Service-Token: <hmac>
{ "token": "<user-jwt>" }
```

Internal endpoints are protected by `X-Service-Token` only — no user JWT required.

## Environment Variables

| Variable | Description |
|---|---|
| `SERVICE_TOKEN` | Shared HMAC secret for inter-service auth |
| `DATABASE_URL` | PostgreSQL DSN |
| `AUTH_SERVICE_URL` | Auth service base URL (`http://auth:8001`) |

## Database Schema

All tables in the shared `aethermoor` database. Cross-service `user_id` references are stored as strings — no DB-level foreign key to the auth service.

**`characters`** — core data, ability scores, stats  
**`character_positions`** — zone, X/Y, respawn point, last_seen  
**`equipment_slots`** — 9 named slots per character (head, chest, legs, feet, main_hand, off_hand, ring_1, ring_2, amulet)  
**`backpack_items`** — up to 24 grid-indexed inventory slots per character

## Running Tests

```bash
# Unit tests
cd services/character
pytest tests/test_unit.py -v

# Integration tests (requires PostgreSQL)
DATABASE_URL=postgresql://aethermoor:password@localhost:5432/aethermoor_test \
pytest tests/test_integration.py -v
```
