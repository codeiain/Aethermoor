---
tags:
  - notification
  - alerts
  - push
---

# Notification Service

**Port:** 8009  
**Language:** Python 3.12 / FastAPI  
**Database:** PostgreSQL 16, Redis 7

Handles push notifications and in-game alerts for players.

## Responsibilities

- Send real-time notifications to players
- Store notification history
- Support for in-game alerts and system messages
- Integrate with quest, party, and social services for event-driven notifications

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/notification/send` | Send a notification to a player |
| `GET` | `/notification/history` | Get notification history for a player |
| `GET` | `/health` | Liveness probe |

## Notes
- Requires JWT for player actions; X-Service-Token for internal calls.
