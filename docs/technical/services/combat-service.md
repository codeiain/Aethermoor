---
tags:
  - combat
  - battle
  - dnd
---

# Combat Service

**Port:** 8004  
**Language:** Python 3.12 / FastAPI  
**Database:** PostgreSQL 16, Redis 7

Handles all turn-based combat logic using D&D 5e rules. Manages combat state, turn order, and applies damage, effects, and rewards.

## Responsibilities

- Initiate and resolve combat encounters
- Track turn order, HP, status effects
- Validate player and NPC actions
- Calculate damage, healing, and XP rewards
- Store combat logs for audit/debug

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/combat/start` | Start a new combat encounter |
| `POST` | `/combat/action` | Submit a player or NPC action |
| `GET` | `/combat/{id}` | Get combat state |
| `POST` | `/combat/end` | End a combat encounter |
| `GET` | `/health` | Liveness probe |

## Notes
- Requires valid JWT and X-Service-Token for internal calls.
- Relies on world, player, and inventory services for context.
