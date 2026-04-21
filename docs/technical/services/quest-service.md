---
tags:
  - quest
  - objectives
  - progress
---

# Quest Service

**Port:** 8007  
**Language:** Python 3.12 / FastAPI  
**Database:** PostgreSQL 16

Manages the quest catalogue, player quest progress, and quest completion logic.

## Responsibilities

- Store all available quests and objectives
- Track player quest acceptance and progress
- Validate quest completion and rewards
- Support for daily/weekly repeatable quests

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/quest/list` | List all available quests |
| `POST` | `/quest/accept` | Accept a quest |
| `POST` | `/quest/progress` | Update quest progress |
| `POST` | `/quest/complete` | Complete a quest and claim rewards |
| `GET` | `/health` | Liveness probe |

## Notes
- Requires JWT for player actions; X-Service-Token for internal calls.
