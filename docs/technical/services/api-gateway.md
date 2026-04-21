---
tags:
  - gateway
  - proxy
  - security
---

# API Gateway

**Port:** 8000  
**Language:** Python 3.12 / FastAPI  
**Networks:** `public` (exposed to host) + `internal` (reaches backend services)

The gateway is the single entry point for all browser/client requests. It handles CORS, rate limiting, zero-trust token injection, and request proxying.

## Responsibilities

- Reverse-proxy all `/api/*` requests to the appropriate backend service
- Strip `/api/` prefix before forwarding (frontend sends `/api/auth/*`; gateway forwards `/auth/*`)
- Inject `X-Service-Token` HMAC on every upstream request (zero-trust boundary)
- CORS headers for browser clients (dev: `localhost:5173`; prod: same-origin via Nginx)
- In-memory sliding-window rate limiting (no extra Redis dependency)
- Health check aggregation: `GET /services/status` polls all service `/health` endpoints
- OpenAPI aggregation: `GET /openapi-master.json` + `GET /docs-master` Swagger UI

## Route Table

| Client path | Upstream service | Port |
|---|---|---|
| `/auth/*` | auth | 8001 |
| `/players/*` | character | 8002 |
| `/world/*` | world | 8003 |
| `/combat/*` | combat | 8004 |
| `/chat/*` | chat | 8005 |
| `/inventory/*` | inventory | 8006 |
| `/quest/*` | quest | 8007 |
| `/economy/*` | economy | 8008 |
| `/notification/*` | notification | 8009 |

## Zero-Trust Token Injection

The gateway generates a fresh HMAC-SHA256 `X-Service-Token` for every upstream request:

```python
ts = int(time.time()) // 60  # 60-second bucket
token = hmac.new(SECRET.encode(), str(ts).encode(), sha256).hexdigest()
header = f"{ts}:{token}"
```

Backend services verify the token using the same algorithm (`zero_trust.py`). One previous bucket is accepted to tolerate clock skew between containers.

**Why gateway injects the token (not the browser):** The `SERVICE_TOKEN` secret is never exposed to the browser. The gateway is the trust boundary — it holds the secret and vouches for every forwarded request.

## CORS

CORS is only required for the Vite dev server (the browser and the gateway run on different ports during development). In production, the frontend and gateway are served behind Nginx on the same origin — no CORS headers needed.

Allowed origins:
- `http://localhost:3000` (prod Docker frontend)
- `http://localhost:5173` (Vite dev server)
- `http://127.0.0.1:3000`, `http://127.0.0.1:5173`

## Frontend Architecture

The React + Phaser.js SPA is served by Nginx as static files on port 3000.

| Component | Technology |
|---|---|
| Screen router | Zustand state (`"login"` → `"character-select"` → `"character-create"` → `"game"`) |
| Game engine | Phaser.js 3 — `RESIZE` scale mode, `pixelArt: true`, touch input enabled |
| Camera system | Fixed viewport camera — player centered, world scrolls (see [rendering-camera-system.md](../rendering-camera-system.md)) |
| Tile textures | Generated programmatically via `Phaser.Graphics.generateTexture()` — no PNG tileset required for prototype |
| Movement | WASD + arrow keys (desktop) + nipplejs virtual joystick (touch devices) |
| Mobile detection | `window.matchMedia("(pointer: coarse)")` — joystick only renders on touch screens |
| JWT storage | Memory only (Zustand store) — never written to `localStorage`. Session ends on page close. |

**ADR — Phaser.js over PixiJS:** CEO decision. Phaser.js includes scene management, input, cameras, and tweens out of the box, removing the need for separate libraries. PixiJS is a pure renderer and would require significant additional wiring for the same result.

**ADR — Synthetic textures for prototype:** Rather than blocking on the art pipeline for a tileset PNG, PreloadScene generates `tile_grass`, `tile_wall`, `tile_town`, `player`, and `npc_dot` textures via `Phaser.Graphics.generateTexture()`. Real art assets replace these in a future sprint.

## Vite Dev Proxy

During development, Vite proxies `/api/*` → `http://localhost:8000` with path rewrite:

```typescript
"/api": {
  target: "http://localhost:8000",
  changeOrigin: true,
  rewrite: (path) => path.replace(/^\/api/, ""),
}
```

The rewrite is critical: the gateway listens at `/auth/*` (not `/api/auth/*`). Without the rewrite, all requests 404.

## Operations Endpoints

| Path | Description |
|---|---|
| `GET /health` | Gateway liveness probe |
| `GET /services/status` | Polls all downstream service `/health` endpoints, returns combined status |
| `GET /metrics` | Prometheus metrics |
| `GET /openapi-master.json` | Aggregated OpenAPI spec from all services |
| `GET /docs-master` | Swagger UI HTML pointing at aggregated spec |

## Environment Variables

| Variable | Description |
|---|---|
| `SERVICE_TOKEN` | Shared HMAC secret injected on every upstream request |
| `AUTH_SERVICE_URL` | `http://auth:8001` |
| `CHARACTER_SERVICE_URL` | `http://character:8002` |
| `WORLD_SERVICE_URL` | `http://world:8003` |
| `COMBAT_SERVICE_URL` | `http://combat:8004` |
| `CHAT_SERVICE_URL` | `http://chat:8005` |
| `INVENTORY_SERVICE_URL` | `http://inventory:8006` |
| `QUEST_SERVICE_URL` | `http://quest:8007` |
| `ECONOMY_SERVICE_URL` | `http://economy:8008` |
| `NOTIFICATION_SERVICE_URL` | `http://notification:8009` |
