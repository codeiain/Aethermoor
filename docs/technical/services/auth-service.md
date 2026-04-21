---
tags:
  - auth
  - jwt
  - users
---

# Auth Service

**Port:** 8001  
**Language:** Python 3.12 / FastAPI  
**Databases:** PostgreSQL 16 (users), Redis 7 (token blacklist + rate limiting)

Handles all user authentication and provides zero-trust JWT verification for other AETHERMOOR microservices.

## Responsibilities

- User registration and login
- JWT access token (15 min) + refresh token (7 days) issuance and rotation
- Token blacklisting on logout and refresh rotation (via Redis)
- Rate limiting on sensitive endpoints (brute-force protection)
- Internal `verify-service-token` endpoint so other services can validate user JWTs without holding `JWT_SECRET`

## API Endpoints

### Public (user-facing)

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/register` | Create a new user account |
| `POST` | `/auth/login` | Authenticate — returns `{ access_token, refresh_token }` |
| `POST` | `/auth/refresh` | Rotate refresh token, issue new access token |
| `POST` | `/auth/logout` | Revoke the refresh token |
| `GET` | `/auth/me` | Validate access token, return `{ user_id, username }` |
| `GET` | `/health` | Liveness probe |

### Internal (zero-trust, requires `X-Service-Token`)

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/verify-service-token` | Verify a user JWT on behalf of another service |

## Authentication Flow

```
Client  →  POST /auth/login { email, password }
        ←  { access_token (15min), refresh_token (7d) }

Client  →  GET /api/* Authorization: Bearer <access_token>
        ←  proxied by gateway to upstream service

Service →  POST /auth/verify-service-token X-Service-Token: <hmac>
        ←  { user_id, username, is_valid }

Client  →  POST /auth/refresh { refresh_token }
        ←  { new access_token, new refresh_token }   (old refresh revoked)

Client  →  POST /auth/logout { refresh_token }
        ←  204 No Content   (refresh token blacklisted)
```

## Security Decisions

| Decision | Rationale |
|---|---|
| HS256 JWT | Single-issuer system; algorithm always passed explicitly to `jwt.decode()` to prevent `alg:none` attacks |
| Refresh token in Redis | Enables instant revocation on logout without waiting for token expiry |
| Refresh rotation | Each use issues a new token and revokes the old — prevents replay |
| Rate limiting (Redis sliding window) | 10 req/min login, 5 req/min register per client IP |
| bcrypt work factor 12 | Adequate for current hardware; increase if Pi benchmarks allow |
| Timing-safe login | `verify_password` always called even for unknown usernames — prevents enumeration via timing |

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL DSN (`postgresql://user:pass@host:5432/db`) |
| `REDIS_URL` | Redis DSN (`redis://:pass@host:6379/0`) |
| `JWT_SECRET` | HS256 signing secret — `openssl rand -hex 64` |
| `SERVICE_TOKEN` | Shared inter-service HMAC secret — `openssl rand -hex 32` |

## Database Schema

**`users`**

| Column | Type | Notes |
|---|---|---|
| `id` | VARCHAR(36) | UUID PK |
| `username` | VARCHAR(64) | Unique, indexed |
| `email` | VARCHAR(255) | Unique, lowercase, indexed |
| `password_hash` | VARCHAR(255) | bcrypt hash |
| `is_active` | BOOLEAN | Soft-disable |
| `created_at` | TIMESTAMPTZ | Server default |
| `updated_at` | TIMESTAMPTZ | Auto-updated |

Schema created automatically on startup. Alembic migrations planned once schema stabilises.

## Running Tests

```bash
# Unit tests (no infra)
cd services/auth
pytest tests/test_unit.py -v

# Integration tests (requires Postgres + Redis)
TEST_DATABASE_URL=postgresql+asyncpg://aethermoor:pass@localhost:5432/aethermoor \
TEST_REDIS_URL=redis://:pass@localhost:6379/1 \
pytest tests/test_integration.py -v
