---
tags:
  - economy
  - gold
  - marketplace
---

# Economy Service
**Port:** 8008  
**Language:** Python 3.12 / FastAPI  
**Database:** PostgreSQL 16, Redis 7

Handles all in-game currency, marketplace listings, and player transactions.

## Responsibilities

- Track player gold balances
- Manage marketplace listings (buy/sell)
- Validate and process transactions
- Prevent double-spending and race conditions

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/economy/balance` | Get player gold balance |
| `POST` | `/economy/transfer` | Transfer gold between players |
| `POST` | `/economy/marketplace/list` | List an item for sale |
| `POST` | `/economy/marketplace/buy` | Buy an item from the marketplace |
| `GET` | `/health` | Liveness probe |

## Notes
- Requires JWT for player actions; X-Service-Token for internal calls.
