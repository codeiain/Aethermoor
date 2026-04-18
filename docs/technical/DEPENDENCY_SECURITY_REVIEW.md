# AETHERMOOR — Dependency Security Review

> Required gate before any new dependency is merged. Last updated: 2026-04-14.

## Backend (Python)

| Package | Version | License | Source | Risk | Notes |
|---|---|---|---|---|---|
| `fastapi` | 0.115.6 | MIT | PyPI / tiangolo | Low | Industry-standard async web framework; actively maintained; CVE history clean at review date |
| `uvicorn[standard]` | 0.32.1 | BSD-3 | PyPI / encode | Low | ASGI server; `[standard]` adds `httptools` + `websockets`; all widely audited |
| `pydantic` | 2.10.4 | MIT | PyPI / pydantic | Low | Data validation; v2 Rust core, no known critical CVEs |
| `httpx` | 0.28.1 | BSD-3 | PyPI / encode | Low | Async HTTP client (gateway outbound calls); no known critical CVEs |
| `ruff` | latest | MIT | PyPI / astral-sh | Low | Dev-only linter; not in production image |
| `pytest` + `pytest-asyncio` | latest | MIT | PyPI | Low | Dev/CI only; not in production image |

### Auth Service additions (RPGAA-7, reviewed 2026-04-14)

| Package | Version | License | Source | CVE Check | Maintenance | Risk | Notes |
|---|---|---|---|---|---|---|---|
| `PyJWT` | 2.9.0 | MIT | PyPI / jpadilla | NVD/GitHub: no critical CVEs at review date; CVE-2022-29217 (algorithm confusion) patched in 2.4.0 — we pin ≥2.9 and always pass `algorithms=` | Active; last commit 2024; 70M+ monthly downloads | Low | JWT encode/decode; we use HS256 and always specify algorithm list explicitly to prevent alg:none attacks |
| `bcrypt` | 4.2.1 | Apache-2.0 | PyPI / pyca | NVD: no critical CVEs; uses libsodium internals; widely audited | Active; maintained by Python Cryptographic Authority (pyca) | Low | Password hashing; bcrypt work factor default 12; pyca-maintained — same org as `cryptography` |
| `sqlalchemy[asyncio]` | 2.0.36 | MIT | PyPI / sqlalchemy | NVD: no critical CVEs for 2.x line; CVE-2019-7548 (1.x) irrelevant | Active; last release Jan 2025; 200M+ monthly downloads | Low | ORM; `[asyncio]` extra required for async engine support |
| `asyncpg` | 0.30.0 | Apache-2.0 | PyPI / MagicStack | NVD: no known CVEs | Active; maintained by MagicStack; last release 2024 | Low | Async PostgreSQL driver; used by SQLAlchemy async engine via `postgresql+asyncpg://` |
| `redis[asyncio]` | 5.2.1 | MIT | PyPI / redis-py | NVD/GitHub: no critical CVEs; `[asyncio]` extra adds `aioredis` shims | Active; official Redis client; last release Jan 2025 | Low | Async Redis client for token blacklisting and rate limiting |

**Approval decision:** All five packages pass the security gate. No CVEs block adoption. All are open source, actively maintained, and widely deployed in production Python services. Approved for use in `services/auth/requirements.txt`.

### Base image
- `python:3.12-slim` — official Docker Hub image, Debian slim base. Verified by digest in production.
  Runs as non-root (`appuser`). No shell entrypoint in final layer.

## Frontend (Node/npm)

| Package | Version | License | Risk | Notes |
|---|---|---|---|---|
| `react` + `react-dom` | 18.3.x | MIT | Low | Facebook / Meta; largest OSS ecosystem |
| `vite` | 6.x | MIT | Low | Build tool; dev-server only in production Docker multi-stage (not shipped) |
| `typescript` | 5.7.x | Apache-2.0 | Low | Dev only |
| `@vitejs/plugin-react` | 4.x | MIT | Low | Dev only |
| `eslint` + `@typescript-eslint/*` | latest | MIT | Low | Dev/CI only |
| `vitest` | 2.x | MIT | Low | Dev/CI only |

### Frontend additions (RPGAA-13, reviewed 2026-04-14)

Replaced `pixi.js` (dropped — focused purely on rendering, no scene management or input) with the following stack reviewed below.

| Package | Version | License | Source | CVE Check | Maintenance | Risk | Notes |
|---|---|---|---|---|---|---|---|
| `phaser` | 3.88.x | MIT | npm / photonstorm | NVD: no critical CVEs at review date; GitHub advisories: clean; Snyk: no high severity findings | Active; last release 2024; 40k+ GitHub stars; ~200k weekly npm downloads | Low | 2D game framework providing scene management, WebGL/Canvas rendering, physics, input. Widely deployed in browser games. MIT licence confirmed. |
| `zustand` | 5.0.x | MIT | npm / pmndrs | NVD: no CVEs; GitHub advisories: clean; Snyk: no findings | Active; maintained by Poimandres collective; 50k+ GitHub stars; 5M+ weekly downloads | Low | Minimal React state management; no external dependencies; well-audited; MIT licence confirmed. |
| `nipplejs` | 0.10.x | MIT | npm / yoannmoinet | NVD: no CVEs; GitHub advisories: clean; no server-side execution so attack surface is purely UI | Active; last release 2023; widely used in mobile web games; 500k+ monthly downloads | Low | Virtual joystick for touch input. Pure JS, no native bindings, minimal dependency tree. MIT licence confirmed. |

**Approval decision:** All three packages pass the security gate. No CVEs block adoption. All are open source with MIT licences, actively maintained, and widely deployed in production browser applications. Approved for use in `frontend/package.json`.

### Base images (frontend)
- `node:22-alpine` — build stage only; not shipped to production.
- `nginx:1.27-alpine` — production stage; minimal attack surface, no app runtime.

## Infrastructure images

| Image | Version | Notes |
|---|---|---|
| `postgres:16-alpine` | 16-alpine | Official; data encrypted at rest via volume; no public port exposed |
| `redis:7-alpine` | 7-alpine | Official; password-protected; `appendonly yes`; no public port exposed |

## Decisions & Constraints

1. **All packages are open source** — no proprietary or source-available licenses.
2. **No new dependency may be added without updating this file and getting CTO sign-off.**
3. `npm ci --ignore-scripts` used throughout to block malicious install scripts.
4. Production Python images install only `requirements.txt`; no dev deps.
5. `setuptools` pin in `shared/pyproject.toml` prevents build-system exploit vectors.

## Next review
Schedule a quarterly review or on any high-severity CVE disclosure for the above packages.
