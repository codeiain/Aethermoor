---
tags: 
  - websocket 
  - multiplayer
  - realtime
	- gateway
---

# WebSocket Gateway Service

**Port:** 8010  
**Language:** Python 3.12 / FastAPI + WebSockets  
**Database:** Redis 7

Acts as the multiplayer relay for real-time game events and player presence.

## Responsibilities

- Manage player WebSocket connections
- Relay real-time game events (movement, chat, combat)
- Broadcast presence and zone updates
- Integrate with Redis for pub/sub event delivery

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/ws` | WebSocket endpoint for clients |
| `GET` | `/health` | Liveness probe |

## Notes
- All multiplayer events are relayed through this service.
- Requires JWT for player connections; X-Service-Token for internal events.
