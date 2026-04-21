---
tags:
  - crafting
  - recipes
---

# Crafting Service
**Port:** 8013  
**Language:** Python 3.12 / FastAPI  
**Database:** PostgreSQL 16

Manages item crafting, recipe catalogue, and crafting actions for players.

## Responsibilities

- Store and retrieve crafting recipes
- Validate crafting requirements and consume ingredients
- Create crafted items and add to inventory
- Support for future crafting skill progression

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/crafting/recipes` | List all available recipes |
| `POST` | `/crafting/craft` | Craft an item |
| `GET` | `/health` | Liveness probe |

## Notes
- Requires JWT for player actions; X-Service-Token for internal calls.
