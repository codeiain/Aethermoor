---
tags:
  - inventory
  - items
  - equipment
---

# Inventory Service

**Port:** 8006  
**Language:** Python 3.12 / FastAPI  
**Database:** PostgreSQL 16

Manages player inventory, equipment, and loot distribution. Handles item storage, transfers, and equipment slots.

## Responsibilities

- Store and retrieve player inventory
- Manage equipment slots (weapons, armor, etc.)
- Handle loot drops and item pickups
- Enforce inventory limits
- Support for future item trading

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/inventory/{characterId}` | Get inventory for a character |
| `POST` | `/inventory/{characterId}/add` | Add item to inventory |
| `POST` | `/inventory/{characterId}/remove` | Remove item from inventory |
| `POST` | `/inventory/{characterId}/equip` | Equip an item |
| `POST` | `/inventory/{characterId}/unequip` | Unequip an item |
| `GET` | `/health` | Liveness probe |

## Notes
- Requires JWT for user actions; X-Service-Token for internal service calls.
