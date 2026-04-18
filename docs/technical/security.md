# AETHERMOOR — Security Architecture

> Last updated: 2026-04-14

## Threat Model

AETHERMOOR runs on a Raspberry Pi connected to the internet. The primary threats are:

1. **Unauthorised API access** — players calling internal endpoints directly
2. **Service compromise spreading** — one container being used to call other containers
3. **Account takeover** — brute-force login, stolen JWT, credential stuffing
4. **Game integrity attacks** — player position spoofing, stat manipulation

## Zero-Trust Service-to-Service Authentication

All internal service-to-service calls carry an `X-Service-Token` header. The gateway generates this token on every proxied request; backend services verify it before handling internal endpoints.

### Token Format

```
X-Service-Token: {epoch_bucket}:{hmac_digest}
```

- `epoch_bucket` = `int(time.time()) // 60` — rotates every 60 seconds
- `hmac_digest` = `HMAC-SHA256(SERVICE_TOKEN, str(epoch_bucket))`

### Verification

```python
def require_service_token(x_service_token: str = Header(...)):
    ts_str, provided_digest = x_service_token.split(":", 1)
    ts = int(ts_str)
    now_bucket = int(time.time()) // 60
    # Accept current and previous bucket to tolerate clock skew
    valid = any(
        hmac.compare_digest(
            hmac.new(SECRET.encode(), str(bucket).encode(), sha256).hexdigest(),
            provided_digest
        )
        for bucket in [now_bucket, now_bucket - 1]
    )
    if not valid:
        raise HTTPException(status_code=401)
```

`hmac.compare_digest` is used throughout to prevent timing attacks.

### Why HMAC Over mTLS (ADR)

mTLS is the gold standard for zero-trust but adds significant operational complexity: certificate rotation, a CA, and per-service certs. For the prototype on a single Raspberry Pi with a small founding team, HMAC tokens provide strong mutual authentication with far less operational overhead. mTLS is the target for production once the team scales and the deployment pipeline is established.

## JWT Authentication (User-Facing)

### Access Tokens

- Algorithm: HS256 (`jwt.decode()` always called with `algorithms=["HS256"]` — prevents `alg:none` attacks)
- Lifetime: 15 minutes
- Payload: `{ user_id, username, exp }`
- Verified by: `POST /auth/verify-service-token` (all services except auth)

### Refresh Tokens

- Stored in Redis with a 7-day TTL
- Rotation on every use (old token blacklisted, new token issued)
- Revoked immediately on logout
- Prevents replay: a stolen refresh token used by an attacker invalidates the legitimate user's session, triggering re-login

### Token Storage (Client)

JWT is stored in Zustand (React memory) only. It is **never** written to `localStorage` or `sessionStorage`. The session ends when the user closes the browser tab. This prevents XSS token theft at the cost of requiring re-login on page refresh — acceptable at prototype stage.

## Password Security

- bcrypt with work factor 12 (via `pyca/bcrypt`)
- `verify_password()` always called even for unknown usernames — prevents username enumeration via timing side-channel
- Minimum password length enforced by Pydantic schema

## Rate Limiting

Redis sliding-window counters protect sensitive endpoints:

| Endpoint | Limit | Window |
|---|---|---|
| `POST /auth/login` | 10 requests | 60 seconds per IP |
| `POST /auth/register` | 5 requests | 60 seconds per IP |

The gateway also implements in-memory rate limiting as a second layer. The in-memory layer resets on container restart; the Redis layer persists across restarts.

## Network Isolation

Two Docker networks prevent direct access to backend services:

- **`public`**: `gateway` + `frontend` + monitoring only. Exposed to the host.
- **`internal`**: all backend services. `internal: true` in Compose prevents any external host from routing to these containers directly.

A compromised frontend container cannot reach the database directly — it can only call the gateway on the public network, which enforces service tokens before forwarding.

## Secrets Management

All secrets are environment variables injected at runtime via `infra/.env` (not committed to version control). Required secrets:

| Variable | Generation | Rotation |
|---|---|---|
| `JWT_SECRET` | `openssl rand -hex 64` | Manual; requires restart of auth service |
| `SERVICE_TOKEN` | `openssl rand -hex 32` | Manual; requires restart of all services simultaneously |
| `POSTGRES_PASSWORD` | `openssl rand -hex 32` | Manual; requires DB re-init |
| `REDIS_PASSWORD` | `openssl rand -hex 32` | Manual; requires restart of Redis + all consumers |

`.env.example` is committed with placeholder values. `.env` is `.gitignore`d.

## Dependency Security Policy

All dependencies must be open source (MIT, Apache 2.0, GPL, or equivalent). Every new dependency requires a security review documented in `infra/DEPENDENCY_SECURITY_REVIEW.md`:

1. Check NVD, GitHub Advisories, Snyk for known CVEs
2. Verify maintenance status and last commit date
3. Confirm licence compatibility
4. Check download stats and community trust signals
5. Document outcome before merging

No exceptions. A failed review blocks adoption; an alternative must be proposed.

## Known Gaps (Prototype)

These are documented risks accepted for the prototype milestone. Each requires a ticket before production:

| Gap | Risk | Mitigation |
|---|---|---|
| mTLS not implemented | Service token compromise allows full internal access | Deploy to private network; mTLS in future sprint |
| No HTTPS (HTTP only) | Tokens visible in transit on local network | Add TLS termination at Nginx in production |
| Schema migrations via `create_all()` | Schema drift risk on upgrades | Alembic migration system tracked for future ticket |
| Rate limiting is per-instance | Distributed rate limit bypass if replicated | Acceptable for single-Pi deployment |
| No admin authentication on config endpoints | Any service with `SERVICE_TOKEN` can change live config | Future: admin JWT scope required |
