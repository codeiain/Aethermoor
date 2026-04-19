# Aethermoor — Operations Runbook

**Audience:** On-call operator (solo engineer)
**Infra:** Raspberry Pi, Docker Compose, self-hosted

---

## 1. Stack Access

| Tool | Access |
|---|---|
| Grafana | `ssh -L 3001:127.0.0.1:3001 pi@<host>` then `http://localhost:3001` |
| Prometheus | `ssh -L 9090:prometheus:9090 pi@<host>` (or via Grafana datasource) |
| Alertmanager | `ssh -L 9093:alertmanager:9093 pi@<host>` then `http://localhost:9093` |
| Loki logs | Via Grafana → Explore → Loki datasource |
| Services | All internal; SSH into Pi and use `docker logs <container>` |

Grafana credentials: `GRAFANA_USER` / `GRAFANA_PASSWORD` from `infra/.env`.

---

## 2. Alert Definitions & Initial Response

### GatewayHighErrorRate (critical)
**Condition:** Gateway 5xx error rate > 5% over 5 minutes.

1. Open Grafana → **Aethermoor — Services Overview** → **5xx Error Rate** panel.
2. Identify which service is erroring (check per-service error rate rows).
3. Check container logs: `docker logs <service> --tail 100`
4. Check if the database or Redis is the root cause:
   - `docker exec postgres pg_isready`
   - `docker exec redis redis-cli -a $REDIS_PASSWORD ping`
5. If a specific service: restart it → `docker compose -f infra/docker-compose.prod.yml restart <service>`
6. If systemic: check Pi load → `htop`, `df -h`, `free -h`
7. Escalate: if not resolved in 15 minutes, initiate rollback (§4).

### GatewayHighLatency (warning)
**Condition:** Gateway p99 latency > 500ms over 5 minutes.

1. Open Grafana → **Per-Service p99 Latency** panel — identify slow service.
2. Check cAdvisor dashboard for CPU/memory pressure on the Pi.
3. Check active connections: `docker exec redis redis-cli -a $REDIS_PASSWORD info clients`
4. Check DB: `docker exec postgres psql -U $POSTGRES_USER -d aethermoor -c "SELECT count(*) FROM pg_stat_activity;"`
5. Reduce load if needed: disable non-critical services temporarily.
6. If Redis memory > 80%: `docker exec redis redis-cli -a $REDIS_PASSWORD info memory`

### AuthFailureSpike (warning) / AuthFailureCritical (critical)
**Condition:** Auth 401 rate > 5/s (warning) or > 20/s (critical).

1. Open Grafana → **Auth Failures (401/s)** panel — confirm spike.
2. Check Loki logs for the auth service: `{service="auth"} |= "401"` — identify source IPs.
3. If brute-force suspected:
   - Block source IP at Pi firewall: `sudo iptables -A INPUT -s <ip> -j DROP`
   - Or configure rate limiting in nginx/upstream proxy if present.
4. Check for compromised client: look for unusual user agents or patterns in logs.
5. If attack is ongoing at critical level: temporarily disable public gateway port.
   - `docker compose -f infra/docker-compose.prod.yml stop gateway`
   - Notify users via any out-of-band channel.

### ServiceDown (critical)
**Condition:** Prometheus cannot scrape a service for >1 minute.

1. `docker ps --filter "name=<service>"` — check if container is running.
2. If not running: `docker compose -f infra/docker-compose.prod.yml start <service>`
3. If crashing: check logs → `docker logs <service> --tail 200`
4. Common causes:
   - DB not yet healthy: wait for postgres healthcheck, then restart
   - Port conflict: `ss -tlnp | grep <port>`
   - OOM: `dmesg | grep -i "killed process"` — increase or reduce container memory
5. If cannot restart: initiate rollback (§4).

### ContainerCpuThrottled / ContainerHighMemory (warning)
**Condition:** Container CPU throttled >50% or memory >85% of limit.

1. Identify container from alert label.
2. Check what it's doing: `docker stats <container>`
3. If a game service spike: likely a burst of player activity — monitor and let it resolve.
4. If sustained: consider reducing `uvicorn` worker concurrency or scaling down non-essential services.
5. Pi RAM is ~4 GB total. Reduce Redis `maxmemory` headroom if needed.

### RedisHighMemory (warning)
**Condition:** Redis memory > 80% of 96 MB cap.

1. `docker exec redis redis-cli -a $REDIS_PASSWORD info memory`
2. Check which DB has most keys: `docker exec redis redis-cli -a $REDIS_PASSWORD info keyspace`
3. Flush expired sessions if safe: `docker exec redis redis-cli -a $REDIS_PASSWORD SELECT <db>; DBSIZE`
4. If not urgent: reduce TTLs in chat (DB 3) or world state (DB 1).

### DiskSpaceLow (critical)
**Condition:** Less than 15% free disk.

1. `df -h` on Pi — identify which mount.
2. Clean Prometheus data: `docker exec prometheus promtool tsdb list /prometheus`
   - Reduce retention: update `--storage.tsdb.retention.time=3d` in compose, restart.
3. Clean Loki chunks: `du -sh /var/lib/docker/volumes/infra_loki-data`
   - Reduce Loki retention in `loki/loki-config.yml` (`retention_period: 72h`), restart.
4. Prune Docker: `docker system prune -f` (does NOT remove running containers or volumes).
5. Check for large log files: `docker logs <container> | wc -c` — restart if logs are huge.

---

## 3. Log Investigation (Loki / Grafana)

### Query examples in Grafana Explore

```logql
# All errors from any service
{namespace="aethermoor"} |= "ERROR"

# Auth service 401s
{service="auth"} |= "401"

# Gateway 5xx
{service="gateway"} |~ "5[0-9][0-9]"

# All logs from a specific service in last 15 min
{service="world"}

# Exception tracebacks
{namespace="aethermoor"} |= "Traceback"
```

### Direct container logs

```bash
# Follow a service's logs live
docker logs -f <service> 2>&1

# Last 500 lines
docker logs --tail 500 <service> 2>&1 | grep -i error

# All services at once (noisy but useful)
docker compose -f infra/docker-compose.prod.yml logs --tail 50 --follow
```

---

## 4. Rollback Procedure

### Step 1 — Identify the bad deployment
```bash
git log --oneline -10
```

### Step 2 — Roll back to the previous image
```bash
# Tag the bad commit for reference
git tag bad-deploy/$(date +%Y%m%d-%H%M)

# Checkout previous known-good commit
git checkout <previous-commit-sha>
```

### Step 3 — Rebuild and restart the affected service(s)
```bash
cd infra
docker compose -f docker-compose.prod.yml build <service>
docker compose -f docker-compose.prod.yml up -d --no-deps <service>
```

### Step 4 — Verify recovery
```bash
# Health check
curl http://localhost:8000/health

# Watch metrics in Grafana — error rate should drop within 2 minutes
```

### Step 5 — Full restart if needed
```bash
docker compose -f infra/docker-compose.prod.yml up -d --build
```
Wait for all healthchecks to pass — postgres and redis must be healthy before services start.

---

## 5. Routine Health Checks

Run weekly or after any deployment:

```bash
# All containers healthy?
docker ps --format "table {{.Names}}\t{{.Status}}"

# Prometheus targets all UP?
# Open http://localhost:9090/targets (via SSH tunnel)

# Disk usage
df -h && du -sh /var/lib/docker

# Redis health
docker exec redis redis-cli -a $REDIS_PASSWORD ping
docker exec redis redis-cli -a $REDIS_PASSWORD info memory | grep used_memory_human

# Postgres health
docker exec postgres pg_isready -U $POSTGRES_USER
```

---

## 6. Alertmanager Configuration

Alertmanager is configured at `infra/alertmanager/alertmanager.yml`.
To enable notifications, set `ALERTMANAGER_WEBHOOK_URL` in `infra/.env` to a webhook receiver:

- **ntfy.sh (self-hosted):** `http://ntfy:80/aethermoor-alerts` — add `ntfy` service to compose
- **Email:** Uncomment SMTP block in `alertmanager.yml` and set `SMTP_*` env vars
- **Simple webhook:** Any HTTP endpoint that accepts POST JSON

To silence an alert during maintenance:
1. Open Alertmanager UI (port 9093 via SSH tunnel)
2. Click **Silences → New Silence**
3. Match on `alertname` or `job`, set duration

---

## 7. Emergency Contacts & Escalation

This is a solo-engineer project. If you are the engineer:
- Check `#aethermoor` channel or project notes for any recent deploy context.
- If data loss is suspected: **stop all writes first**, then investigate.
- Database dumps: `docker exec postgres pg_dump -U $POSTGRES_USER aethermoor > backup-$(date +%Y%m%d).sql`
