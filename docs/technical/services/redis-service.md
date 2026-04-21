---
tags: 
  - database
  - redis
---

# Redis Service

**Port:** (internal only)  
**Image:** redis:7-alpine

Primary in-memory database for caching, pub/sub, and ephemeral state.

## Responsibilities

- Store ephemeral state for combat, chat, world, etc.
- Provide pub/sub for real-time messaging
- Support rate limiting and token blacklisting

## Configuration
- Data volume: `redis_data:/data`
- Environment: `REDIS_PASSWORD`

## Notes
- Not exposed to public network; only internal services connect
- Healthcheck: `redis-cli ping`
