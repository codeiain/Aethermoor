---
tags: 
  - social 
  - friends 
  - block
---
# Social Service

**Port:** 8012  
**Language:** Python 3.12 / FastAPI  
**Database:** Redis 7

Manages friends lists, blocks, and the social graph for players.

## Responsibilities

- Add/remove friends
- Block/unblock players
- Track social relationships
- Integrate with notification and party services

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/social/add-friend` | Add a friend |
| `POST` | `/social/remove-friend` | Remove a friend |
| `POST` | `/social/block` | Block a player |
| `POST` | `/social/unblock` | Unblock a player |
| `GET` | `/social/list` | List friends and blocks |
| `GET` | `/health` | Liveness probe |

## Notes
- Requires JWT for player actions; X-Service-Token for internal calls.
