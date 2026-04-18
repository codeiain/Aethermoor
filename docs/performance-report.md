# AETHERMOOR — Raspberry Pi Performance Report

**Date:** 2026-04-18
**Target hardware:** Raspberry Pi 4 Model B (4 GB RAM, ARM Cortex-A72, SD card storage)
**Stack version:** All 14 Docker services (post-RPG-67)

---

## Methodology

Benchmarks are collected after `docker compose -f docker-compose.prod.yml up -d --build` from a cold boot with no other processes running. Each metric is averaged over a 10-minute steady-state window with 5 concurrent simulated players.

**Tools used:**
- `docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"` for per-service resource usage
- `wrk -t2 -c10 -d30s` for HTTP p95 latency benchmarks (2 threads, 10 connections, 30 seconds)
- Prometheus `histogram_quantile(0.95, ...)` for in-flight p95 during normal gameplay

---

## Target SLAs (Pi 4)

| Endpoint | p95 Target | Status |
|---|---|---|
| `GET /health` (gateway) | < 10ms | — |
| `POST /auth/login` | < 200ms | — |
| `GET /players/me` | < 200ms | — |
| `GET /world/zones/{zone_id}` | < 200ms | — |
| `POST /quests/{id}/accept/{quest_id}` | < 300ms | — |
| `POST /combat/start` | < 300ms | — |
| `POST /crafting/craft` | < 300ms | — |

**Memory threshold:** Any service exceeding 512 MB RSS must be flagged to CEO before launch.

---

## Per-Service Resource Targets (Pi 4, idle + 5 players)

| Service | Port | Expected CPU% | Expected RAM |
|---|---|---|---|
| postgres | — | 1–3% | 64–128 MB |
| redis | — | < 1% | 16–32 MB |
| gateway | 8000 | 2–5% | 64–96 MB |
| auth | 8001 | 1–3% | 64–96 MB |
| character | 8002 | 1–3% | 64–96 MB |
| world | 8003 | 2–5% | 64–128 MB |
| combat | 8004 | 1–3% | 64–96 MB |
| chat | 8005 | 1–2% | 32–64 MB |
| inventory | 8006 | 1–2% | 64–96 MB |
| quest | 8007 | 1–2% | 64–96 MB |
| economy | 8008 | 1–3% | 64–96 MB |
| notification | 8009 | < 1% | 32–64 MB |
| websocket-gateway | 8010 | 1–3% | 32–64 MB |
| party | 8011 | 1–2% | 32–64 MB |
| social | 8012 | 1–2% | 32–64 MB |
| crafting | 8013 | 1–2% | 64–96 MB |
| loki | — | 1–2% | 64–128 MB |
| prometheus | — | 1–3% | 64–128 MB |
| grafana | — | 1–2% | 64–128 MB |
| **TOTAL** | — | **~30–50%** | **~1.2–1.8 GB** |

Total expected RAM leaves ~2 GB headroom on a 4 GB Pi for OS, page cache, and traffic bursts.

---

## How to Run Benchmarks

### 1. Start the stack

```bash
cd infra
cp .env.example .env  # edit secrets
docker compose -f docker-compose.prod.yml up -d --build
# wait for all health checks to pass (~60-90s on Pi)
docker compose -f docker-compose.prod.yml ps
```

### 2. Capture per-service resource snapshot

```bash
docker stats --no-stream --format \
  "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" \
  | tee /tmp/aethermoor-stats.txt
```

### 3. HTTP latency benchmarks (requires wrk)

```bash
# Login p95
wrk -t2 -c10 -d30s -s scripts/bench-login.lua http://localhost:8000/auth/login

# World zone read p95
wrk -t2 -c10 -d30s http://localhost:8000/world/zones/starter_town
```

### 4. E2E test suite

```bash
GATEWAY_URL=http://localhost:8000 pytest tests/e2e/ -v
```

### 5. Check Prometheus metrics

```bash
# Open Grafana (via SSH tunnel if on Pi)
ssh -L 3001:localhost:3001 pi@<pi-ip>
# Browse http://localhost:3001 with GRAFANA_USER/GRAFANA_PASSWORD credentials
```

---

## Known Pi Constraints

- **SD card I/O** is the primary bottleneck for PostgreSQL write-heavy workloads. Consider a USB SSD for the `postgres_data` volume in production.
- **Thermal throttling** under sustained load on Pi 4 — ensure adequate cooling (heatsink + fan).
- **Cold start time** is ~60–90 seconds for all 20 containers to reach healthy state on first boot.
- **WebSocket connections** are limited by Pi TCP connection table; test max concurrent at 200 connections before launch.

---

## Escalation Thresholds

| Condition | Action |
|---|---|
| Any service > 512 MB RSS | Escalate to CEO — infra change required |
| p95 latency > 200ms on `/auth/login` or `/players/me` | Profile and optimise DB queries |
| Total RAM > 3.5 GB | Disable non-critical services (Grafana, cadvisor) until scaled |
| CPU sustained > 80% | Enable horizontal scale-out (Pi 4 cluster) — escalate to CEO |

---

*Benchmarks to be completed after production deployment. Update this document with actual measurements before launch sign-off.*
