# Deployment & Operations — Docker Compose

> Last updated: 2026-04-14

All AETHERMOOR services run in Docker on a Raspberry Pi 4. A single Docker Compose stack in `infra/docker-compose.yml` defines the full system.

## Quick Start

```bash
cd infra
cp .env.example .env
# Edit .env — set JWT_SECRET, SERVICE_TOKEN, POSTGRES_PASSWORD, REDIS_PASSWORD
docker compose up --build
```

The stack starts all services. On first run, each service creates its database schema automatically.

## Service Ports (Host-Accessible)

| Service | Host Port | Notes |
|---|---|---|
| Frontend (Nginx) | 3000 | SPA — main entry point |
| Gateway | 8000 | API entry point for external clients |
| Auth | 8001 | Direct access for debugging; normally via gateway |
| Character | 8002 | Direct access for debugging |
| World | 8003 | Direct access for debugging |
| Combat | 8004 | Stub |
| Chat | 8005 | Stub |
| Inventory | 8006 | Stub |
| Quest | 8007 | Stub |
| Economy | 8008 | Stub |
| Notification | 8009 | Stub |
| Prometheus | 9090 | Metrics collection |
| Grafana | 5007 (configurable) | Dashboards — default `admin`/`admin` |
| Loki | 3110 | Log aggregation |
| cAdvisor | 8080 | Container metrics |
| Redis Exporter | 9121 | Redis Prometheus metrics |

Backend services on the `internal` network are only reachable from within Docker. The host-port mappings above exist for debugging; in production they should be removed and all traffic routed through the gateway.

## Environment Variables

Copy `infra/.env.example` to `infra/.env`. Never commit `.env`.

| Variable | Required | Description |
|---|---|---|
| `JWT_SECRET` | Yes | HS256 signing secret — `openssl rand -hex 64` |
| `SERVICE_TOKEN` | Yes | Inter-service HMAC secret — `openssl rand -hex 32` |
| `POSTGRES_USER` | Yes | PostgreSQL username |
| `POSTGRES_PASSWORD` | Yes | PostgreSQL password |
| `REDIS_PASSWORD` | Yes | Redis `requirepass` value |
| `GRAFANA_PORT` | No | Grafana host port (default `5007`) |
| `TZ` | No | Timezone for containers (default `UTC`) |

## Startup Order

The Compose `depends_on` + `healthcheck` chain enforces this order:

```
postgres (healthy) ─┐
redis (healthy)    ─┼─▶ auth (healthy) ─┬─▶ character (healthy) ─┐
                    │                   │                          │
                    └───────────────────┴──────────────────────────┴─▶ world
                                                                   │
                    ┌──────────────────────────────────────────────┘
                    ▼
                 gateway ─▶ frontend
```

## Development Workflow (Hot Reload)

Run backend services in Docker, frontend with Vite for hot module replacement:

```bash
# Start backend only
cd infra
docker compose up postgres redis auth character world gateway

# Start frontend dev server (separate terminal)
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

The Vite dev server proxies `/api/*` → `http://localhost:8000` with path rewrite. All other routes serve the SPA.

## Rebuilding a Single Service

```bash
docker compose build world
docker compose up -d world
```

## Viewing Logs

```bash
# Tail all services
docker compose logs -f

# Single service
docker compose logs -f gateway

# Structured JSON logs can also be queried in Grafana / Loki
```

## Health Checks

Every service exposes `GET /health`. The gateway aggregates all health checks:

```bash
curl http://localhost:8000/services/status
```

Returns per-service status and overall system health.

## Raspberry Pi Considerations

- **ARM64 images**: All base images (`python:3.12-slim`, `postgres:16-alpine`, `redis:7-alpine`, `nginx:1.27-alpine`) have ARM64 variants and pull correctly on a Pi 4.
- **Memory**: The full stack uses approximately 800MB–1.2GB RAM. A Pi 4 with 4GB RAM is sufficient. Close unused stub services to reduce footprint.
- **CPU**: NPC tick loop skips zones with zero players — idle zones consume no CPU. Monitor CPU with cAdvisor + Grafana under load.
- **Storage**: PostgreSQL and Redis data are stored in named Docker volumes (`postgres_data`, `redis_data`). Back these up before any Pi OS upgrades.
- **Swap**: Enable a 2GB swap file on the Pi's SD card as a safety net for memory spikes during Docker builds.

## Backup

```bash
# Postgres dump
docker compose exec postgres pg_dump -U $POSTGRES_USER aethermoor > backup.sql

# Redis RDB snapshot (Redis is configured with appendonly yes — AOF also available)
docker compose exec redis redis-cli -a $REDIS_PASSWORD BGSAVE
# RDB file is in the redis_data volume at /data/dump.rdb
```

## Dockerfile

All Python services share `infra/Dockerfile.service`:

- **Build stage**: `python:3.12-slim` — installs dependencies via `pip install --no-cache-dir`
- **Runtime stage**: same image, non-root `appuser`
- `npm ci --ignore-scripts` equivalent: Python install scripts are not a concern here, but `--no-cache-dir` keeps image size down

The frontend uses `infra/Dockerfile.frontend` with a two-stage build:
- **Build stage**: `node:22-alpine` — `npm ci && npm run build`
- **Runtime stage**: `nginx:1.27-alpine` — serves `dist/` as static files with `nginx.conf`
