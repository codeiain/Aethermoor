---
tags:
  - guild
  - clan
---

# Guild Service
**Port:** 8014  
**Language:** Python 3.12 / FastAPI  
**Database:** Redis 7

Manages guild creation, membership, and guild features for players.

## Responsibilities

- Create and manage guilds
- Handle guild invites and membership
- Track guild roles and permissions
- Integrate with chat and notification services

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/guild/create` | Create a new guild |
| `POST` | `/guild/invite` | Invite a player to a guild |
| `POST` | `/guild/leave` | Leave a guild |
| `GET` | `/guild/{guildId}` | Get guild details |
| `GET` | `/health` | Liveness probe |

## Notes
- Requires JWT for player actions; X-Service-Token for internal calls.
