---
tags:
  - party
  - group
  - multiplayer
---

# Party Service

**Port:** 8011  
**Language:** Python 3.12 / FastAPI  
**Database:** Redis 7

Manages party formation, invites, and group state for multiplayer gameplay.

## Responsibilities

- Create and manage player parties
- Handle party invites and join/leave events
- Track party membership and leader
- Integrate with chat and quest services for group features

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/party/create` | Create a new party |
| `POST` | `/party/invite` | Invite a player to a party |
| `POST` | `/party/leave` | Leave a party |
| `GET` | `/party/{partyId}` | Get party details |
| `GET` | `/health` | Liveness probe |

## Notes
- Requires JWT for player actions; X-Service-Token for internal calls.
