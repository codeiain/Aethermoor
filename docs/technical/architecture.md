# AETHERMOOR — System Architecture

> Last updated: 2026-04-14

## Overview

AETHERMOOR is a cross-platform 2D MMO RPG. The backend is a Python microservice mesh. The frontend is a single React + Phaser.js application targeting mobile, tablet, and web. Everything runs in Docker on a Raspberry Pi.

## High-Level Diagram

```
Browser / Mobile App
        │
        ▼
┌───────────────┐   port 3000
│   Frontend    │   React + Phaser.js (Nginx)
│  (Nginx SPA)  │
└───────┬───────┘
        │ /api/* (same-origin)
        ▼
┌───────────────┐   port 8000
│    Gateway    │   FastAPI reverse proxy
│               │   CORS, rate limiting, zero-trust token injection
└──┬──┬──┬──┬──┘
   │  │  │  │   Internal Docker network — all calls carry X-Service-Token
   ▼  ▼  ▼  ▼
┌────┐ ┌────────────┐ ┌───────┐ ┌──────────┐  ... (future services)
│Auth│ │ Character  │ │ World │ │  Combat  │
│8001│ │    8002    │ │ 8003  │ │   8004   │
└──┬─┘ └─────┬──────┘ └───┬───┘ └────┬─────┘
   │         │             │          │
   └────┬────┴─────────────┴──────────┘
        │
   ┌────┴─────┐  ┌──────────┐
   │PostgreSQL│  │  Redis 7 │
   │    16    │  │          │
   └──────────┘  └──────────┘
```

## Services

| Service | Port | Description | Status |
|---|---|---|---|
| `gateway` | 8000 | API gateway — single entry point for all browser requests | Live |
| `auth` | 8001 | User registration, login, JWT issuance + verification | Live |
| `character` | 8002 | Player characters, stats, inventory, position | Live |
| `world` | 8003 | Zones, tilemaps, NPCs, world events | Live |
| `combat` | 8004 | Combat resolution | Stub |
| `chat` | 8005 | Zone and global chat | Stub |
| `inventory` | 8006 | Item management | Stub |
| `quest` | 8007 | Quest tracking | Stub |
| `economy` | 8008 | Gold, auction house, trading | Stub |
| `notification` | 8009 | Push notifications | Stub |
| `frontend` | 3000 | React + Phaser.js SPA (Nginx) | Live |

## Tech Stack

| Layer | Technology |
|---|---|
| Backend language | Python 3.12 |
| Backend framework | FastAPI + uvicorn[standard] |
| ORM | SQLAlchemy 2.0 async + asyncpg |
| Cache / real-time state | Redis 7 |
| Persistent storage | PostgreSQL 16 |
| Frontend language | TypeScript |
| Frontend framework | React 18 |
| Game engine | Phaser.js 3 |
| State management | Zustand 5 |
| Mobile joystick | nipplejs |
| Container runtime | Docker + Docker Compose |
| Deployment target | Raspberry Pi 4 (ARM64) |
| Observability | Prometheus + Grafana + Loki + Promtail |

## Network Isolation

Two Docker networks:

- **`public`**: gateway + frontend only. Exposed to the host.
- **`internal`**: all backend services. Not accessible from the host. No service can receive direct internet traffic except via the gateway.

## Data Ownership

Each service owns its own data in the shared PostgreSQL database. Cross-service user references use string UUIDs — no database-level foreign keys between service schemas. This preserves service independence and allows future schema separation.

| Service | PostgreSQL tables | Redis keys |
|---|---|---|
| auth | `users` | `blacklist:*`, `rate:*` |
| character | `characters`, `character_positions`, `equipment_slots`, `backpack_items` | — |
| world | `zones`, `npc_templates`, `world_events` | `zone:players:*`, `zone:count:*`, `npc:*`, `dock:*`, `world:config:*` |

## Observability

- Every service emits **structured JSON logs** via `python-json-logger`. Promtail collects logs from Docker and ships to Loki.
- Every service exposes **Prometheus metrics** on `/metrics` (request counts, latencies, error rates).
- Grafana dashboards at port `5007` (configurable). Prometheus scrapes on `9090`.
- cAdvisor provides container-level CPU/memory metrics at `8080`.
- Redis metrics via `redis-exporter` on `9121`.

## Architecture Decision Records

ADRs are tracked in `docs/technical/` alongside the documentation they apply to. Key decisions:

| Decision | Where documented |
|---|---|
| Phaser.js chosen over PixiJS for game engine | [services/api-gateway.md](services/api-gateway.md) — client section |
| Fixed viewport camera over following camera | [rendering-camera-system.md](rendering-camera-system.md) |
| Zero-trust HMAC tokens over mTLS for prototype | [security.md](security.md) |
| PostgreSQL JSONB for tilemap storage | [services/game-world-service.md](services/game-world-service.md) |
| Redis Lua CAS for fishing dock soft cap | [services/game-world-service.md](services/game-world-service.md) |
| JWT in memory only (no localStorage) | [services/api-gateway.md](services/api-gateway.md) |
| Synthetic tile textures for prototype | [services/api-gateway.md](services/api-gateway.md) — frontend section |
