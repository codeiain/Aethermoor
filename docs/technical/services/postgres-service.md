---
tags: 
  - database 
  - postgres
---

# Postgres Service

**Port:** 55432 (host), 5432 (container)  
**Image:** postgres:16-alpine

Primary relational database for all core services (auth, character, world, etc.).

## Responsibilities

- Store persistent data for all game and user services
- Provide transactional consistency and backup support

## Configuration
- Data volume: `postgres_data:/var/lib/postgresql/data`
- Environment: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`

## Notes
- Not exposed to public network; only internal services connect
- Healthcheck: `pg_isready`
