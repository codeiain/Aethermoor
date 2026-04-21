---
tags:
  - chat
  - messaging
  - pubsub
---

# Chat Service

**Port:** 8005  
**Language:** Python 3.12 / FastAPI  
**Database:** PostgreSQL 16, Redis 7 (pub/sub)

Handles all in-game chat, including zone chat and party chat, using Redis pub/sub for real-time message delivery.

## Responsibilities

- Zone chat (all players in a zone)
- Party chat (private group chat)
- Message moderation and filtering
- Chat history persistence (optional)
- Rate limiting and anti-spam

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/chat/send` | Send a chat message |
| `GET` | `/chat/zone/{zoneId}` | Get recent zone chat messages |
| `GET` | `/chat/party/{partyId}` | Get recent party chat messages |
| `GET` | `/health` | Liveness probe |

## Notes
- Uses Redis pub/sub for real-time delivery.
- Requires JWT for user messages; X-Service-Token for internal moderation.
