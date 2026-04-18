# AETHERMOOR Auth Service

Handles all user authentication and provides zero-trust token verification for other AETHERMOOR microservices.

## Responsibilities

- User registration, login, logout
- JWT access token + refresh token issuance and rotation
- Token blacklisting (logout / refresh rotation) via Redis
- Rate limiting on sensitive endpoints (brute-force protection)
- Internal endpoint for other services to verify user JWTs without holding `JWT_SECRET`

## Stack

| Component | Technology |
|---|---|
| Framework | FastAPI 0.115 |
| Database | PostgreSQL 16 (SQLAlchemy async + asyncpg) |
| Cache | Redis 7 (redis-py asyncio) |
| Token signing | PyJWT 2.9, HS256 |
| Password hashing | bcrypt 4.2 (pyca), work factor 12 |

## API Endpoints

### Public (user-facing)

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/register` | Create a new user account |
| `POST` | `/auth/login` | Authenticate and receive tokens |
| `POST` | `/auth/refresh` | Rotate refresh token and issue new access token |
| `POST` | `/auth/logout` | Revoke the refresh token |
| `GET` | `/auth/me` | Validate current access token and return user info |
| `GET` | `/health` | Liveness probe |

### Internal (zero-trust, requires `X-Service-Token`)

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/verify-service-token` | Validate a user JWT on behalf of another service |

## Authentication Flow

```
Client → POST /auth/login → { access_token (15 min), refresh_token (7 days) }
Client → GET /auth/me  (Bearer <access_token>) → user info
Client → POST /auth/refresh (refresh_token) → new token pair (old refresh revoked)
Client → POST /auth/logout (refresh_token) → refresh token revoked
```

Access tokens are verified locally by each service using the `verify-service-token` endpoint (for services that do not hold `JWT_SECRET`) or by decoding directly (for services that do — currently only auth holds it).

## Zero-Trust Architecture

All service-to-service calls must include `X-Service-Token: <ts>:<hmac>` (HMAC-SHA256 over the current 60-second epoch bucket using the shared `SERVICE_TOKEN` secret). This prevents any compromise of one container from freely calling internal-only endpoints on other containers.

The `zero_trust.py` module in this service implements `require_service_token` as a FastAPI dependency. Other services include the same logic (from `shared/aethermoor_shared/auth.py`).

> **Note:** `zero_trust.py` is a local copy of `shared/aethermoor_shared/auth.py`. This is intentional — the Docker build context for each service only includes its own directory. When the build pipeline supports multi-directory contexts, this duplication should be resolved.

## Security Decisions

| Decision | Rationale |
|---|---|
| HS256 for JWT | Sufficient for a single-issuer system; algorithm is always passed explicitly to `jwt.decode()` to prevent alg:none attacks |
| Refresh token stored in Redis | Enables instant revocation on logout without waiting for expiry |
| Refresh token rotation | Each use of a refresh token issues a new one and invalidates the old — prevents replay attacks |
| Rate limiting via Redis | Sliding window counter on login (10 req/min) and register (5 req/min) per client IP |
| bcrypt work factor 12 | Default gensalt — adequate for current hardware; increase if Raspberry Pi benchmarks allow |
| Timing-safe login | `verify_password` always called even on unknown usernames to prevent username enumeration via timing |

## Configuration (Environment Variables)

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string (`postgresql://user:pass@host:5432/db`) |
| `REDIS_URL` | Redis connection string (`redis://:pass@host:6379/0`) |
| `JWT_SECRET` | HS256 signing secret — generate with `openssl rand -hex 64` |
| `SERVICE_TOKEN` | Shared inter-service HMAC secret — generate with `openssl rand -hex 32` |

## Running Tests

### Unit tests (no infrastructure required)

```bash
cd services/auth
pip install -r requirements.txt pytest pytest-asyncio
pytest tests/test_unit.py -v
```

### Integration tests (requires Postgres + Redis)

```bash
# Via docker-compose (recommended)
docker-compose -f infra/docker-compose.yml run --rm auth \
  sh -c "pip install pytest pytest-asyncio httpx && pytest tests/test_integration.py -v"

# Or locally with services running on default ports
TEST_DATABASE_URL=postgresql+asyncpg://aethermoor:pass@localhost:5432/aethermoor \
TEST_REDIS_URL=redis://:pass@localhost:6379/1 \
pytest tests/test_integration.py -v
```

## Database

Schema is created automatically on startup via `Base.metadata.create_all()`. This is intentional for the current early stage. A migration tool (Alembic) is tracked for a future ticket once schema stabilises.

### Tables

**`users`**

| Column | Type | Notes |
|---|---|---|
| `id` | VARCHAR(36) | UUID primary key |
| `username` | VARCHAR(64) | Unique, indexed |
| `email` | VARCHAR(255) | Unique, indexed, stored lowercase |
| `password_hash` | VARCHAR(255) | bcrypt hash |
| `is_active` | BOOLEAN | Soft-disable accounts |
| `created_at` | TIMESTAMPTZ | Server default |
| `updated_at` | TIMESTAMPTZ | Auto-updated |
