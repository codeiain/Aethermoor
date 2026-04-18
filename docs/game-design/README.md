# AETHERMOOR — Game Design Documentation

**Project:** Project AETHERMOOR
**Last updated:** 2026-04-14

This directory contains all Game Design Documents (GDDs) for Project AETHERMOOR.
Documents are maintained by the Game Designer and sourced from Paperclip issues.

---

## Document Index

| File | Paperclip Source | Description |
|---|---|---|
| [GDD.md](./GDD.md) | RPGAA-2 | Core Game Design Document — world vision, systems overview, all pillars |
| [combat/combat-system.md](./combat/combat-system.md) | RPGAA-14 | Full combat spec — D&D mechanics, attack resolution, spells, enemies, PvP |
| [world/overworld-map.md](./world/overworld-map.md) | RPGAA-11 | Overworld map and zone design — all biomes, towns, dungeons |
| [world/npc-quest-system.md](./world/npc-quest-system.md) | RPGAA-21 | NPC archetypes, dialogue system, quest types, D&D skill checks in quests |
| [ui/wireframes.md](./ui/wireframes.md) | RPGAA-12 | UI wireframes and HUD specification — all screens, mobile-first |
| [ui/style-guide.md](./ui/style-guide.md) | RPGAA-12 | Visual component style guide |

---

## Directory Structure

```
game-design/
  README.md                   ← This file
  GDD.md                      ← Master Game Design Document
  combat/
    combat-system.md           ← D&D combat mechanics and enemy design
  world/
    overworld-map.md           ← World map, biomes, zones, dungeons
    npc-quest-system.md        ← NPCs, quests, dialogue, reputation
  ui/
    wireframes.md              ← All UI wireframes (HUD, menus, inventory)
    style-guide.md             ← UI component and visual style guide
```

---

## Update Policy

All documents are the authoritative source of truth for the CTO to implement from.
When documents are updated in Paperclip, they should be re-synced to this directory.
