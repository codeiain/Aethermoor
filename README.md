## Per-Service Breakdown

Below is a summary of every service in the Docker Compose stack, including infrastructure, monitoring, and application services.

### Application & Game Services

- **gateway** (8000): API gateway, rate limiting, zero-trust token injection. Entry point for all API traffic.
- **auth** (8001): Authentication (register, login, JWT refresh). Depends on postgres, redis.
- **character** (8002): Player character management. Depends on auth, postgres.
- **world** (8003): Game world, zones, NPCs, presence. Depends on character, auth, postgres, redis.
- **combat** (8004): Turn-based combat logic. Depends on postgres, redis.
- **chat** (8005): Zone and party chat (Redis pub/sub). Depends on postgres, redis.
- **inventory** (8006): Item storage, equipment, loot. Depends on postgres.
- **quest** (8007): Quest catalogue and progress. Depends on postgres.
- **economy** (8008): Gold balances, marketplace. Depends on postgres, redis, auth.
- **notification** (8009): Push notifications, in-game alerts. Depends on postgres, redis.
- **websocket-gateway** (8010): Multiplayer WebSocket relay. Depends on redis.
- **party** (8011): Party formation, invites, group state. Depends on redis, auth.
- **social** (8012): Friends list, blocks, social graph. Depends on redis, auth.
- **crafting** (8013): Recipe catalogue, item crafting. Depends on postgres, auth, character.
- **guild** (8014): Guild management. Depends on redis, auth.
- **frontend** (3000): React + Phaser.js game client, served by Nginx. Depends on gateway.

### Notes, Dashboard, and Management

- **notediscovery** (8800): Self-hosted Markdown notes, plugins, AI assistant integration. Data volume: `/app/data`.
- **homepage** (8888): Self-hosted dashboard (Homepage). Config volume: `/app/config`.
- **portainer** (9900): Docker management UI. Volumes: Docker socket, portainer_data.

### Monitoring & Observability

- **loki** (3110): Log aggregation (Grafana Loki). Data volume: `/loki`.
- **promtail**: Log shipping agent for Loki. Reads Docker logs.
- **redis-exporter** (9121): Redis Prometheus metrics exporter.
- **prometheus** (9090): Metrics collection and monitoring. Data volume: `/prometheus`.
- **grafana** (5007): Dashboards and visualization. Data volume: `/var/lib/grafana`.
- **cadvisor** (8080): Container metrics (cAdvisor). Reads Docker and system metrics.

### Databases

- **postgres** (55432): PostgreSQL 16 database. Data volume: `postgres_data`.
- **redis**: Redis 7 database. Data volume: `redis_data`.
# AETHERMOOR

Cross-platform 2D MMO RPG — Zelda-style exploration × D&D mechanics.
Runs on mobile, tablet, and web from a single application.

## Quick Start (Development)

```bash
cd infra
cp .env.example .env       # edit secrets
docker compose up --build
```

| Service           | URL                       |
|-------------------|---------------------------|
| Frontend          | http://localhost:3000     |
| API Gateway       | http://localhost:8000     |
| Grafana           | http://localhost:5007     |
| NoteDiscovery     | http://localhost:8800     |
## NoteDiscovery (Self-Hosted Notes)

NoteDiscovery is a lightweight, self-hosted Markdown note-taking app with AI assistant integration (MCP). It runs as a Docker service and is accessible at [http://localhost:8800](http://localhost:8800) (default port, see docker-compose for mapping).

- **Features:** Markdown notes, tags, search, plugins, graph view, AI assistant (Claude, Cursor, etc.)
- **Data:** All notes are stored as plain text in the container volume (`data/`)
- **Security:** Password protection and API key support (see NoteDiscovery docs)
- **MCP:** Can be used as a knowledge base for AI agents

**To enable/disable authentication or set an API key, see the NoteDiscovery documentation or set environment variables in the Compose file.**


## Production Deployment (Raspberry Pi)

### Prerequisites

- Raspberry Pi 4 (4 GB RAM recommended)
- Docker 24+ and Docker Compose v2
- USB SSD recommended for PostgreSQL data volume (SD card I/O is the bottleneck)
- Static local IP or dynamic DNS for the Pi

### 1. First-time Pi Setup

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Clone the repo
git clone <repo-url> ~/aethermoor
cd ~/aethermoor
```

### 2. Configure Secrets

```bash
cd infra
cp .env.example .env
```

Edit `.env` and set **all** values — never leave `change-me` in any field:

```bash
# Generate strong secrets:
openssl rand -hex 32   # → SERVICE_TOKEN
openssl rand -hex 64   # → JWT_SECRET
openssl rand -base64 24 | tr -d '=' # → POSTGRES_PASSWORD, REDIS_PASSWORD, GRAFANA_PASSWORD
```

### 3. (Optional) Move Data Volumes to USB SSD

```bash
# Mount your USB SSD at /data
sudo mkdir -p /data/aethermoor
sudo chown $USER:$USER /data/aethermoor

# Edit infra/docker-compose.prod.yml — replace volume paths:
# postgres_data → /data/aethermoor/postgres
# redis_data    → /data/aethermoor/redis
```

### 4. Deploy

```bash
cd infra
docker compose -f docker-compose.prod.yml up -d --build
```

Watch all services reach healthy state (~60–90 seconds on first boot):

```bash
docker compose -f docker-compose.prod.yml ps
# All services should show "healthy" or "Up"
```

### 5. DNS and Firewall

```bash
# Allow game ports on the Pi firewall
sudo ufw allow 3000/tcp   # Frontend
sudo ufw allow 8000/tcp   # API Gateway
sudo ufw allow 8010/tcp   # WebSocket Gateway
sudo ufw enable

# Point your domain's A record to the Pi's IP, then configure your router
# to port-forward 80/443 → Pi:3000 (or use a reverse proxy like Caddy).
```

### 6. Verify Deployment

```bash
# Health check
curl http://localhost:8000/health
# → {"status":"ok","service":"gateway"}

# All services status
curl http://localhost:8000/services/status

# Run E2E test suite (requires pytest + httpx)
cd ..
pip install pytest pytest-asyncio httpx anyio
GATEWAY_URL=http://localhost:8000 pytest tests/e2e/ -v
```

### 7. Monitoring (Grafana)

Grafana is bound to `127.0.0.1:3001` in production (not publicly exposed).
Access it via SSH tunnel:

```bash
ssh -L 3001:localhost:3001 pi@<pi-ip>
# Open http://localhost:3001 in your browser
# Login with GRAFANA_USER / GRAFANA_PASSWORD from .env
```

### 8. Updates

```bash
cd infra
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

---

## Services

| Service              | Port (dev) | Description |
|----------------------|------------|---------------------------------------------------------------|
| `gateway`            | 8000       | API gateway — single entry point, rate limiting, zero-trust token injection |
| `auth`               | 8001       | Authentication — register, login, JWT refresh |
| `character`          | 8002       | Player characters — create, stats, position, tutorial |
| `world`              | 8003       | Game world — zones, tilemaps, NPCs, presence WebSocket |
| `combat`             | 8004       | Turn-based combat — D&D 5e rules, Redis state |
| `chat`               | 8005       | Zone and party chat over Redis pub/sub |
| `inventory`          | 8006       | Item storage, equipment, loot distribution |
| `quest`              | 8007       | Quest catalogue, acceptance, progress, completion |
| `economy`            | 8008       | Gold balances, marketplace listings, transactions |
| `notification`       | 8009       | Push notifications and in-game alerts |
| `websocket-gateway`  | 8010       | Multiplayer WebSocket relay |
| `party`              | 8011       | Party formation, invites, group state |
| `social`             | 8012       | Friends list, blocks, social graph |
| `crafting`           | 8013       | Recipe catalogue, item crafting |
| `guild`              | 8014       | Guild management and features |
| `frontend`           | 3000       | React + Phaser.js game client (served by Nginx) |
| `notediscovery`      | 8800       | Self-hosted Markdown notes, plugins, AI assistant integration |
| `homepage`           | 8888       | Self-hosted dashboard (Homepage) |
| `portainer`          | 9900       | Docker management UI |
| `loki`               | 3110       | Log aggregation (Grafana Loki) |
| `promtail`           | —          | Log shipping agent for Loki |
| `redis-exporter`     | 9121       | Redis Prometheus metrics exporter |
| `prometheus`         | 9090       | Metrics collection and monitoring |
| `grafana`            | 5007       | Dashboards and visualization |
| `cadvisor`           | 8080       | Container metrics (cAdvisor) |
| `postgres`           | 55432      | PostgreSQL database (internal only) |
| `redis`              | —          | Redis database (internal only) |

In production (`docker-compose.prod.yml`) only ports **3000**, **8000**, and **8010** are exposed to the host. All other services communicate on the internal Docker network.

---

## Development (frontend hot-reload)

```bash
# Start backend services
cd infra && docker compose up -d

# Start frontend dev server (separate terminal)
cd frontend && npm install && npm run dev
# → http://localhost:5173 (Vite proxies /api/* → gateway on :8000)
```

---

## Running Tests

```bash
# Backend unit + integration tests (no live stack required)
pytest services/auth/tests/ -v
pytest services/character/tests/ -v
# ... (each service has its own test suite)

# Full E2E integration tests (requires live stack)
cd infra && docker compose up -d --build
cd ..
GATEWAY_URL=http://localhost:8000 pytest tests/e2e/ -v
```

---

## Stack

- **Backend:** Python FastAPI microservices, PostgreSQL 16, Redis 7
- **Frontend:** React 18 + TypeScript + Phaser.js 3 + Zustand + nipplejs
- **Infra:** Docker Compose on Raspberry Pi, Nginx, Prometheus + Grafana + Loki
- **Security:** Zero-trust HMAC service tokens between all microservices, JWT auth, rate limiting at gateway

---

## Performance

See [`docs/performance-report.md`](docs/performance-report.md) for Raspberry Pi benchmark targets, methodology, and escalation thresholds.
