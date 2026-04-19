# AETHERMOOR — World Map Specification v1.0

**Author:** Game Designer
**Date:** 2026-04-14
**Status:** Draft v1.0 — Overworld Map Milestone
**Source GDD:** v0.4 (RPGAA-2)

***

## Table of Contents

1. Overview & Design Intent
2. Zone Register — All Launch Zones
3. Overworld Map Diagram & Traversal Graph
4. Dungeon List
5. Town Directory
6. PvP Contested Territory Summary
7. Fast Travel Waypoint Network
8. MMO Considerations
9. Technical Notes for CTO
10. Open Questions

***

## 1. Overview & Design Intent

The AETHERMOOR world is divided into **8 Regions**, each composed of multiple named **Zones**. Zones are the atomic unit of the game world — the CTO seeds each zone as an entry in the Game World Service zone registry.

**Design intent:**

* Players start in Millhaven (Region 1) at Level 1 and organically push outward as they level
* The world is not gated by hard level locks — low-level players can enter high-level zones but will be killed by enemies; this creates danger-zone tension (Zelda-style "go here when you're ready")
* Dungeon entrances are located *inside* overworld zones — players discover them by exploring
* PvP zones are clearly signposted at their entry border; PvP flag is not active in non-PvP zones
* All zones are persistent and shared; dungeons are private instances spun on demand

**Progression flow (intended):**

```
Level 1–5:   Millhaven → City of Aethermoor → Ruins (Dungeon 1 & 2)
Level 5–15:  Darkwood Forest → Crystal Caves Approach
Level 7–13:  Crystal Caves → Goblin Wastelands
Level 9–15:  Frostpeak Mountains
Level 11–17: Ember Plains → Sunken Harbor
Level 13–18: Verdant Jungle
Level 15–20: Aether Wastes → Sky Archipelago
Level 18–20: Temple of the Deep (Raid Tier)
```

***

## 2. Zone Register — All Launch Zones

> **Format:** Each zone is a row in the CTO zone registry. `connections` lists zone IDs of directly adjacent/traversable zones.

### Region 1 — City of Aethermoor (Hub Region, Level 1–10)

| Zone ID                 | Zone Name          | Biome            | Level Range | Connections                                                                                                                             | Max Players/Shard       | Key POIs                                                                                                                                                            | Contested? |
| ----------------------- | ------------------ | ---------------- | ----------- | --------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| `millhaven-town`        | Millhaven          | Town             | 1–5         | `millhaven-fields`, `aethermoor-road-south`                                                                                             | 200 (persistent shared) | Inn, General Store, Blacksmith, Notice Board, Fishing: Millhaven Docks, Fast Travel Waypoint                                                                        | No         |
| `millhaven-fields`      | Millhaven Fields   | Forest/Grassland | 1–4         | `millhaven-town`, `darkwood-edge`, `aethermoor-road-south`                                                                              | 50                      | Forage nodes, Goblin Scouts (Level 1–3), Hidden cellar (secret)                                                                                                     | No         |
| `aethermoor-road-south` | Southern Road      | Grassland/Road   | 2–6         | `millhaven-town`, `millhaven-fields`, `aethermoor-city`                                                                                 | 50                      | Roadside inn (rest point), Wandering merchant, Bandit camp (Level 4–6)                                                                                              | No         |
| `aethermoor-city`       | City of Aethermoor | Town (Hub)       | 1–20        | `aethermoor-road-south`, `aethermoor-undercity`, `darkwood-edge`, `goblin-wastes-border`, `crystal-caves-approach`, `aether-road-east`  | 300 (persistent shared) | Inn, Blacksmith, Auction House, Guild Hall, Bank, All Class Trainers, Crafting Workshop, Faction Envoys, Housing Registrar, Lore Keeper, Fast Travel Waypoint       | No         |
| `aethermoor-undercity`  | Undercity Warrens  | Underground      | 4–8         | `aethermoor-city`, `ruins-entrance`, `crypts-entrance`                                                                                  | 50                      | Dungeon Entrance: Ruins of the First Aethermoor, Dungeon Entrance: Waterlogged Crypts, Black Market vendor (rotating stock), Secret passage (requires Shatter Rune) | No         |

***

### Region 2 — Darkwood Forest (Level 5–15)

> **Updated 2026-04-19:** Canonical zone name confirmed as **Darkwood Forest** (CEO decision, [RPG-73](/RPG/issues/RPG-73)). Earlier drafts referenced "Thornwood Forest" — that name is retired. See `game-design/world/darkwood-forest-zone2.md` for the full Zone 2 GDD.

| Zone ID                | Zone Name            | Biome           | Level Range | Connections                                                                              | Max Players/Shard | Key POIs                                                                                                                                                  | Contested?                              |
| ---------------------- | -------------------- | --------------- | ----------- | ---------------------------------------------------------------------------------------- | ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| `darkwood-edge`        | Darkwood Edge        | Forest          | 5–8         | `aethermoor-city`, `millhaven-fields`, `darkwood-heart`, `goblin-wastes-border`          | 50                | Greywood Crossing (village/respawn), Verdant Pact Envoy Camp, Mossglen Stream (fishing), Old Ranger's Watchtower (secret — lore scroll)                   | No                                      |
| `darkwood-heart`       | Darkwood Heart       | Forest (Dense)  | 8–12        | `darkwood-edge`, `darkwood-crossroads`, `blighted-vault-entrance`, `elder-root-approach` | 50                | Dungeon Entrance: Blighted Vault, Darkwood Sanctuary (hidden — Quest Q-1), Whispering Stones collectible (9 fragments), Sunken Glade (fishing — night only), Blight's Edge hazard zone | No                                      |
| `darkwood-crossroads`  | Darkwood Crossroads  | Forest/Clearing | 8–12        | `darkwood-heart`, `goblin-wastes-border`, `ember-plains-north`                           | 100               | **PvP Zone (Verdant Pact vs Aetheric Order)** — Lumber Mill control point, Herb Garden control point, Resource node: Darkwood Lumber (rare crafting mat)  | **Yes — Verdant Pact / Aetheric Order** |
| `darkwood-depths`      | Darkwood Depths      | Forest (Corrupted) | 11–15    | `darkwood-heart`, `goblin-wastes-border`, `blighted-vault-entrance`                      | 50                | Ravenswood Ruins, Root Altar (Blightbear mini-boss — 3hr respawn), Aetheric Order Outpost, Verdant Spring (secret — 9 Whispering Stones required)         | No                                      |
| `elder-root-approach`  | Elder Root Approach  | Ancient Forest  | 9–12        | `darkwood-heart`, `elder-root-vault-entrance`                                            | 50                | Dungeon Entrance: Elder Root Vault, Ancient Pact shrine (buff: +10% XP in zone for 1hr), Hidden underground passage (requires Tide Rune)                  | No                                      |

***

### Region 3 — Crystal Caves & Goblin Wastelands (Level 7–15)

| Zone ID                  | Zone Name            | Biome                     | Level Range | Connections                                                                                                 | Max Players/Shard | Key POIs                                                                                                                                                                                        | Contested? |
| ------------------------ | -------------------- | ------------------------- | ----------- | ----------------------------------------------------------------------------------------------------------- | ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| `goblin-wastes-border`   | Goblin Wastes Border | Badlands                  | 7–10        | `aethermoor-city`, `darkwood-edge`, `darkwood-crossroads`, `goblin-wastes-deep`, `crystal-caves-approach`   | 50                | Goblin raider camps (Level 7–9), Resource: Iron Ore veins, Abandoned watchtower (scout point)                                                                                                   | No         |
| `goblin-wastes-deep`     | Goblin Wastelands    | Badlands/Wasteland        | 9–13        | `goblin-wastes-border`, `crystal-caves-approach`, `ember-plains-north`                                      | 50                | Goblin Chieftain spawn (world mini-boss, 2hr respawn), Resource: Gold veins, Hidden cave (Uncommon gear chest), Fast Travel Waypoint                                                            | No         |
| `crystal-caves-approach` | Crystal Approach     | Underground Entrance      | 7–11        | `aethermoor-city`, `goblin-wastes-border`, `goblin-wastes-deep`, `crystal-caves-main`                       | 50                | Fishing: Crystal Lake (night only, 18:00–06:00 game time), Crystal merchant NPC, Cave entrance (Dungeon 5 approach)                                                                             | No         |
| `crystal-caves-main`     | Crystal Caves        | Underground/Cave          | 9–13        | `crystal-caves-approach`, `crystal-caves-deep`, `resonance-chamber-entrance`                                | 50                | Dungeon Entrance: Resonance Chamber, Resource: Crystal Ore (Rare), Crystal Golem mini-boss (4hr respawn), Hidden shrine: Silence Rune cache                                                     | No         |
| `crystal-caves-deep`     | Crystal Spire Depths | Underground/Vertical Cave | 11–15       | `crystal-caves-main`, `fractured-spire-entrance`, `frostpeak-footpath`                                      | 50                | Dungeon Entrance: Fractured Spire, Resource: Void Crystal (Epic crafting mat), Extreme verticality puzzles (hookshot required after Dungeon 6), Aetherhook Gadget required for full exploration | No         |

***

### Region 4 — Frostpeak Mountains (Level 9–17)

| Zone ID               | Zone Name           | Biome                    | Level Range | Connections                                                                             | Max Players/Shard | Key POIs                                                                                                                                                                                                   | Contested?                              |
| --------------------- | ------------------- | ------------------------ | ----------- | --------------------------------------------------------------------------------------- | ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| `frostpeak-footpath`  | Frostpeak Footpath  | Mountain/Snow            | 9–12        | `crystal-caves-deep`, `frostpeak-town`, `frosthold-pass`                                | 50                | Cold weather gear check (Fur Cloak required for deep zones), Avalanche event zone (random world event), Resource: Froststone Ore                                                                           | No                                      |
| `frostpeak-town`      | Frosthold           | Town                     | 9–20        | `frostpeak-footpath`, `frosthold-pass`, `frostpeak-summit`                              | 200 (persistent)  | Inn, Blacksmith (specialises in Cold-resistance gear), Fur Cloak vendor, Guild Hall, Fast Travel Waypoint, Aetheric Order stronghold                                                                       | No                                      |
| `frosthold-pass`      | Frosthold Pass      | Mountain Pass            | 11–15       | `frostpeak-town`, `frostpeak-summit`, `frost-tomb-entrance`, `sky-bridge-approach`      | 50                | Dungeon Entrance: Frost Tomb, Fishing: Frostpeak Glacier (requires Cold Weather gear), Giant's Footprint (secret POI — lore scroll), Patrol of Frost Revenants (Level 12–14)                               | No                                      |
| `frostpeak-summit`    | Frostpeak Summit    | Mountain/Glacier         | 13–17       | `frosthold-pass`, `sky-bridge-approach`, `crystal-summit-pvp`                           | 50                | **Leads to PvP zone**, Rare ore veins, World Event spawn point: Frost Giant Incursion (weekly), Hidden cave: frozen NPC (quest: The Frozen General)                                                        | No                                      |
| `crystal-summit-pvp`  | Crystal Summit      | Mountain/Crystal Outcrop | 13–17       | `frostpeak-summit`, `sky-bridge-approach`, `aether-wastes-border`                       | 100               | **PvP Zone (Aetheric Order vs Verdant Pact)** — 3 Crystal Mine control points, Resource: Aether Crystal (top-tier crafting mat, 50% bonus yield to controlling faction), Scenic overlook (screenshot spot) | **Yes — Aetheric Order / Verdant Pact** |
| `sky-bridge-approach` | Sky Bridge Approach | Clifftop/Outdoor         | 14–17       | `frosthold-pass`, `frostpeak-summit`, `crystal-summit-pvp`, `sky-bridge-ruins-entrance` | 50                | Dungeon Entrance: Sky Bridge Ruins, Wind hazard overworld segments (prelude to dungeon mechanic), Storm Drake sighting event (pre-dungeon flavour)                                                         | No                                      |

***

### Region 5 — Ember Plains & Sunken Harbor (Level 11–18)

| Zone ID              | Zone Name          | Biome              | Level Range | Connections                                                                                     | Max Players/Shard | Key POIs                                                                                                                                                                                                         | Contested?                              |
| -------------------- | ------------------ | ------------------ | ----------- | ----------------------------------------------------------------------------------------------- | ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| `ember-plains-north` | Ember Plains North | Plains/Volcanic    | 11–14       | `goblin-wastes-deep`, `darkwood-crossroads`, `ember-plains-south`, `emberton-town`              | 50                | Resource: Emberstone, Ember Tribe patrol camps, Lava fissure mini-hazards, Route to Sunken Harbor                                                                                                                | No                                      |
| `emberton-town`      | Emberton           | Town               | 11–20       | `ember-plains-north`, `ember-plains-south`, `ashen-road`                                        | 200 (persistent)  | Inn, Blacksmith (fire-resistance gear), Alchemy vendor, Guild Hall, Notice Board, Fast Travel Waypoint, Aetheric Order faction HQ (Ember Plains)                                                                 | No                                      |
| `ember-plains-south` | Ember Plains South | Plains/Volcanic    | 13–17       | `ember-plains-north`, `emberton-town`, `ashen-road`, `ember-forge-entrance`, `sunken-docks-pvp` | 50                | Dungeon Entrance: Ember Forge, Portal to Sunken Docks PvP zone, Resource: Volcanic Ash (crafting), World Event: Ember Tide (weekly lava surge)                                                                   | No                                      |
| `sunken-docks-pvp`   | Sunken Docks       | Coastal/Industrial | 13–18       | `ember-plains-south`, `sunken-harbor-town`                                                      | 100               | **PvP Zone (Aetheric Order vs Verdant Pact)** — Fishing: Sunken Docks (Uncommon/Rare fish; +20% rare yield to controlling faction), 2 Dock Control Points, Black Market (only accessible to controlling faction) | **Yes — Aetheric Order / Verdant Pact** |
| `sunken-harbor-town` | Sunken Harbor      | Town (Coastal)     | 11–20       | `sunken-docks-pvp`, `aether-road-east`, `verdant-jungle-approach`                               | 150 (persistent)  | Inn, Fishing Supply vendor, Ship charter (fast travel to Sky Archipelago: unlocks at Level 15), Shipwright (housing: boat decoration), Fast Travel Waypoint                                                      | No                                      |
| `ashen-road`         | Ashen Road         | Road/Wasteland     | 14–18       | `emberton-town`, `ember-plains-south`, `ashen-catacombs-entrance`, `verdant-jungle-approach`    | 50                | Dungeon Entrance: Ashen Catacombs, Ash cloud environmental hazard zones (prelude to dungeon mechanic), Resource: Cinder Bark (alchemy mat)                                                                       | No                                      |

***

### Region 6 — Verdant Jungle (Level 13–20)

| Zone ID                   | Zone Name        | Biome                  | Level Range | Connections                                                                                    | Max Players/Shard | Key POIs                                                                                                                                                                                   | Contested?                              |
| ------------------------- | ---------------- | ---------------------- | ----------- | ---------------------------------------------------------------------------------------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------- |
| `verdant-jungle-approach` | Jungle Approach  | Jungle/Coastal         | 13–16       | `sunken-harbor-town`, `ashen-road`, `verdant-jungle-canopy`, `verdant-pass-pvp`                | 50                | Verdant Pact outpost (quest hub), Resource: Jungle Hardwood, Rare herb nodes, Path to PvP zone                                                                                             | No                                      |
| `verdant-pass-pvp`        | Verdant Pass     | Jungle/Mountain Pass   | 14–18       | `verdant-jungle-approach`, `verdant-jungle-canopy`, `aether-wastes-border`                     | 100               | **PvP Zone (Verdant Pact vs Aetheric Order)** — Spice Road control point (trade route), Poison Flower Garden (rare alchemy mat source), 1 capture flag each side                           | **Yes — Verdant Pact / Aetheric Order** |
| `verdant-jungle-canopy`   | Verdant Canopy   | Jungle (Treetop)       | 14–18       | `verdant-jungle-approach`, `verdant-pass-pvp`, `verdant-jungle-deep`, `bloom-sanctum-entrance` | 50                | Dungeon Entrance: Bloom Sanctum, Verdant Canopy Village (town — see Town Directory), Resource: Dragonvine (Epic alchemy mat), Treeline puzzles (Zelda-style — require Aetherhook Gadget)   | No                                      |
| `verdant-jungle-deep`     | Jungle Depths    | Jungle (Underground)   | 16–20       | `verdant-jungle-canopy`, `sunken-archives-entrance`, `temple-of-deep-approach`                 | 50                | Dungeon Entrance: Sunken Archives (requires Tide Rune for lower wing), Ancient ruins (lore scroll chain), World mini-boss: Rootbinder Herald (4hr respawn, Level 18), Fast Travel Waypoint | No                                      |
| `temple-of-deep-approach` | Path of the Deep | Underground/Underwater | 17–20       | `verdant-jungle-deep`, `aether-wastes-border`, `temple-of-deep-entrance`                       | 50                | Dungeon Entrance: Temple of the First Root (16-player Raid — Act 4 climax), Abyssal shrine (buff: +5% all stats while in Temple zone), Requires: Tide Rune + Level 18                      | No                                      |

***

### Region 7 — Aether Wastes & Sky Archipelago (Level 15–20)

| Zone ID                   | Zone Name            | Biome                   | Level Range | Connections                                                                                                   | Max Players/Shard | Key POIs                                                                                                                                                                                                                                  | Contested?                              |
| ------------------------- | -------------------- | ----------------------- | ----------- | ------------------------------------------------------------------------------------------------------------- | ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| `aether-road-east`        | Eastern Aether Road  | Wasteland/Road          | 12–16       | `aethermoor-city`, `sunken-harbor-town`, `aether-wastes-border`                                               | 50                | Transitional zone, Aether construct patrols (Level 13–15), Resource: Aetherstone dust, Ruined waystation (collectible lore)                                                                                                               | No                                      |
| `aether-wastes-border`    | Aether Wastes Border | Wasteland               | 15–18       | `aether-road-east`, `crystal-summit-pvp`, `verdant-pass-pvp`, `temple-of-deep-approach`, `aether-wastes-deep` | 50                | Warning signs (environmental storytelling), Rift energy hazard zones (prelude mechanic), Resource: Void Shard (Epic crafting mat)                                                                                                         | No                                      |
| `aether-wastes-deep`      | Aether Wastes        | Wasteland/Dimensional   | 16–20       | `aether-wastes-border`, `aether-nexus-pvp`, `rift-delve-entrance`, `sky-archipelago-docks`                    | 50                | Dungeon Entrance: Aether Rift Delve, Fishing: Abyssal Vent (Epic/Legendary fish — Level 18+ only), World Event: Rift Incursion (semi-random, large-scale), Fast Travel Waypoint                                                           | No                                      |
| `aether-nexus-pvp`        | Aether Nexus         | Wasteland/Ruins         | 17–20       | `aether-wastes-deep`, `sky-archipelago-docks`                                                                 | 100               | **PvP Zone (Aetheric Order vs Verdant Pact)** — Aether Siphon control structures (3 nodes), Controlling faction gains: +5% all stats server-wide bonus, Endgame PvP battleground                                                          | **Yes — Aetheric Order / Verdant Pact** |
| `sky-archipelago-docks`   | Sky Docks            | Town/Coastal (Elevated) | 15–20       | `aether-wastes-deep`, `aether-nexus-pvp`, `sky-archipelago-islands`                                           | 150 (persistent)  | Inn, Epic gear vendor (gold only, no AH), Ship and Sky Charter hub, Fast Travel Waypoint, Sky Station town (see Town Directory)                                                                                                           | No                                      |
| `sky-archipelago-islands` | Sky Archipelago      | Island/Aerial           | 17–20       | `sky-archipelago-docks`, `shattered-observatory-entrance`                                                     | 50                | Dungeon Entrance: Shattered Observatory (Season 4 unlock), Crystal lens puzzles (overworld), Resource: Sky Aether Crystal (Legendary crafting mat), Hidden Grotto entrance (Fishing: Legendary fish — discoverable via World Lore scroll) | No                                      |

***

### Region 8 — Temple of the Deep / Raid Tier (Level 18–20)

| Zone ID                   | Zone Name                | Biome            | Level Range | Connections                                          | Max Players/Shard          | Key POIs                                                                                                                           | Contested? |
| ------------------------- | ------------------------ | ---------------- | ----------- | ---------------------------------------------------- | -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| `temple-of-deep-entrance` | Temple Antechamber       | Underwater/Stone | 18–20       | `temple-of-deep-approach`, `temple-of-deep-interior` | 16 (raid lobby)            | Raid entry (16-player — Temple of the First Root), Raid readiness NPC, Buff shrine (+10 to all stats, 1hr, consumed on raid entry) | No         |
| `temple-of-deep-interior` | Temple of the First Root | Raid Zone        | 18–20       | `temple-of-deep-entrance`                            | 16 (private raid instance) | 5 raid wings, Final boss: The Rootbinder (Awakened), Three-choice Act 4 ending, Legendary class-specific loot, "Worldshaper" title | No         |

***

### Special Zones

| Zone ID                      | Zone Name     | Biome              | Level Range | Connections                                      | Max Players/Shard  | Key POIs                                                                                                           | Contested? |
| ---------------------------- | ------------- | ------------------ | ----------- | ------------------------------------------------ | ------------------ | ------------------------------------------------------------------------------------------------------------------ | ---------- |
| `hidden-grotto`              | Hidden Grotto | Cave/Waterfall     | Any         | `sky-archipelago-islands` (hidden entrance only) | 8                  | Fishing: Hidden Grotto (Legendary fish only), discoverable via World Lore scroll chain, peaceful zone — no enemies | No         |
| `housing-district-[plot-id]` | Housing Plot  | Instanced Personal | Any         | Accessed via Housing Registrar in any town       | Owner + 8 visitors | Player home customisation, aquarium, crafting stations, guest visitors                                             | No         |

***

## 3. Overworld Map Diagram & Traversal Graph

```
AETHERMOOR — OVERWORLD TRAVERSAL MAP (v1.0)
═══════════════════════════════════════════════════════════════════

                    ┌───────────────────┐
                    │  SKY ARCHIPELAGO  │ LV 17–20
                    │ sky-archipelago-  │ [Shattered Observatory]
                    │    islands 🏝️     │ ★ Hidden Grotto
                    └────────┬──────────┘
                             │ (ship charter)
                    ┌────────┴──────────┐        ┌──────────────────┐
                    │   SKY DOCKS 🏙️   │────────│  AETHER NEXUS   │ PvP⚔️
                    │ sky-archipelago-  │        │  aether-nexus-   │ LV 17–20
                    │    docks          │        │     pvp           │
                    └────────┬──────────┘        └────────┬─────────┘
                             │                            │
       ┌─────────────────────┴──────────────────────────────────────────────┐
       │                   AETHER WASTES LV 15–20                           │
       │          aether-wastes-border ───── aether-wastes-deep 🎣          │
       │               (Rift Delve🏰)   (Abyssal Vent fishing)              │
       └──────────┬──────────────────────────────┬──────────────────────────┘
                  │                              │
    ┌─────────────┴──────┐           ┌──────────┴─────────┐
    │  CRYSTAL SUMMIT    │ PvP⚔️     │   VERDANT PASS     │ PvP⚔️
    │ crystal-summit-pvp │           │ verdant-pass-pvp    │
    │   LV 13–17         │           │   LV 14–18          │
    └─────────────┬──────┘           └──────────┬──────────┘
                  │                              │
    ┌─────────────┴──────────┐    ┌─────────────┴─────────────┐
    │  FROSTPEAK MOUNTAINS   │    │     VERDANT JUNGLE         │
    │  LV 9–17               │    │     LV 13–20               │
    │  frostpeak-town 🏙️★   │    │  verdant-jungle-canopy     │
    │  frosthold-pass        │    │  [Bloom Sanctum🏰]         │
    │  [Frost Tomb🏰]        │    │  verdant-jungle-deep       │
    │  sky-bridge-approach   │    │  [Sunken Archives🏰]       │
    │  [Sky Bridge Ruins🏰] │    │  verdant-canopy-village 🏙️ │
    │  frostpeak-summit      │    │  temple-of-deep-approach   │
    └─────────────┬──────────┘    └─────────────┬─────────────┘
                  │                              │
    ┌─────────────┴──────────┐    ┌─────────────┴─────────────┐
    │   CRYSTAL CAVES        │    │   EMBER PLAINS &           │
    │   LV 7–15              │    │   SUNKEN HARBOR LV 11–18   │
    │  crystal-caves-approach│    │  emberton-town 🏙️★        │
    │  🎣 Crystal Lake       │    │  ember-plains-south        │
    │  crystal-caves-main    │    │  [Ember Forge🏰]           │
    │  [Resonance Chamber🏰]│    │  [Ashen Catacombs🏰]       │
    │  crystal-caves-deep    │    │  ashen-road                │
    │  [Fractured Spire🏰]  │    │  sunken-harbor-town 🏙️★   │
    └─────────────┬──────────┘    │  sunken-docks-pvp ⚔️🎣    │
                  │               └─────────────┬─────────────┘
    ┌─────────────┴──────────────────────────────┴─────────────┐
    │              GOBLIN WASTELANDS LV 7–13                    │
    │         goblin-wastes-border ─── goblin-wastes-deep       │
    └─────────────┬──────────────────────────────┬─────────────┘
                  │                              │
    ┌─────────────┴──────────────────────────────┴─────────────┐
    │            DARKWOOD FOREST LV 5–15                        │
    │  darkwood-edge ─── darkwood-heart ─── darkwood-depths     │
    │  [Blighted Vault🏰]   darkwood-crossroads ⚔️             │
    │  elder-root-approach ─── [Elder Root Vault🏰]            │
    └─────────────────────────────┬────────────────────────────┘
                                  │
    ┌─────────────────────────────┴────────────────────────────┐
    │         CITY OF AETHERMOOR HUB LV 1–20                   │
    │   ████████████████████████████████████████████████████   │
    │   ★ aethermoor-city (MAIN HUB — all services)  🏙️      │
    │   aethermoor-road-south                                   │
    │   aethermoor-undercity                                    │
    │     [Ruins of First Aethermoor🏰][Waterlogged Crypts🏰]  │
    │   ─────────────────────────────────                       │
    │   aether-road-east ────────────► AETHER WASTES           │
    └─────────────────────────────┬────────────────────────────┘
                                  │
    ┌─────────────────────────────┴────────────────────────────┐
    │           MILLHAVEN STARTER REGION LV 1–5                │
    │   millhaven-town ★🏙️🎣  ──  millhaven-fields             │
    │   aethermoor-road-south (connects north to City)         │
    └──────────────────────────────────────────────────────────┘

LEGEND:
  🏙️ = Town (services, Inn, respawn)    ★ = Fast Travel Waypoint
  🏰 = Dungeon Entrance                 ⚔️ = PvP Contested Zone
  🎣 = Fishing Location                 ─ = Zone Connection
```

### Zone Flow — New Player Start Point

**Spawn:** `millhaven-town` (default for all new characters)
Players receive a starter quest that walks them from Millhaven → City of Aethermoor → Undercity → Ruins of the First Aethermoor (Dungeon 1).

***

## 4. Dungeon List

> All dungeons: 1–4 players, private instance. Weekly first-clear bonus. Challenge Mode for Level 15+ (timed, +1 loot tier).

| #  | Dungeon Name                  | Zone                | Zone ID                   | Level Range | Bosses                              | Run Time               | Loot Tier                       | Notes                                                   |
| -- | ----------------------------- | ------------------- | ------------------------- | ----------- | ----------------------------------- | ---------------------- | ------------------------------- | ------------------------------------------------------- |
| 1  | Ruins of the First Aethermoor | Undercity Warrens   | `aethermoor-undercity`    | 1–5         | The Hollow Knight                   | Short (15–20 min)      | Common/Uncommon                 | Tutorial dungeon — teaches glyph mechanic               |
| 2  | The Waterlogged Crypts        | Undercity Warrens   | `aethermoor-undercity`    | 3–7         | Waterkeeper Maldren                 | Medium (20–30 min)     | Uncommon/Rare                   | Drops **Tide Rune** (traversal unlock)                  |
| 3  | The Blighted Vault            | Darkwood Heart/Depths | `darkwood-heart`        | 8–13        | TBD (Zone 2 dungeon — spec pending) | Medium–Long (30–45 min) | Uncommon/Rare (upper); Rare/Epic (lower wing) | Lower wing requires Druid's Seal (Quest Q-3); full spec in follow-up ticket |
| 3a | The Elder Root Vault          | Elder Root Approach | `elder-root-approach`     | 8–12        | Root Warden Kaeseth                 | Long (35–50 min)       | Rare/Epic                       | Light beam puzzle boss                                  |
| 5  | The Resonance Chamber         | Crystal Caves Main  | `crystal-caves-main`      | 7–10        | Resonance Wraith Olveth             | Medium (20–30 min)     | Rare                            | Drops **Silence Rune**; requires 4-player coordination  |
| 6  | The Fractured Spire           | Crystal Caves Deep  | `crystal-caves-deep`      | 10–14       | The Spire Guardian (3 forms)        | Long (40–55 min)       | Rare/Epic                       | Drops **Aetherhook Gadget** (traversal unlock)          |
| 7  | The Frost Tomb                | Frosthold Pass      | `frosthold-pass`          | 9–13        | General Hroth the Frozen            | Medium (30–40 min)     | Rare/Epic                       | Ice slide mechanic; Cold gear required                  |
| 8  | The Sky Bridge Ruins          | Sky Bridge Approach | `sky-bridge-approach`     | 12–16       | Storm Drake Vethran                 | Medium (25–35 min)     | Rare/Epic                       | Outdoor dungeon — wind gust mechanic                    |
| 9  | The Ember Forge               | Ember Plains South  | `ember-plains-south`      | 11–15       | Forgemaiden Scorra                  | Medium (25–35 min)     | Rare/Epic                       | Lava floor mechanic                                     |
| 10 | The Ashen Catacombs           | Ashen Road          | `ashen-road`              | 14–18       | The Ashen Archon                    | Long (40–55 min)       | Epic/Legendary                  | Combustion mechanic — fire spells forbidden             |
| 11 | The Bloom Sanctum             | Verdant Canopy      | `verdant-jungle-canopy`   | 13–17       | The First Bloom                     | Long (35–50 min)       | Epic                            | Aggression score mechanic — dialogue skip option        |
| 12 | The Sunken Archives           | Verdant Deep        | `verdant-jungle-deep`     | 15–18       | Archivist Prime                     | Long (40–55 min)       | Epic/Legendary                  | Requires **Tide Rune** for lower wing access            |
| 13 | The Aether Rift Delve         | Aether Wastes Deep  | `aether-wastes-deep`      | 17–20       | Rift Sovereign (rotating pool)      | Long (45–60 min)       | Legendary                       | Weekly endgame; randomised room effects                 |
| 14 | Temple of the First Root      | Temple (Raid)       | `temple-of-deep-interior` | 18–20       | The Rootbinder (Awakened) — 4-phase | Very Long (90–120 min) | Legendary (class-specific)      | **16-player raid**, Act 4 story climax, 3-choice ending |
| 15 | The Shattered Observatory     | Sky Archipelago     | `sky-archipelago-islands` | 19–20       | The Weaver's Echo                   | Very Long (90–120 min) | Legendary (Ascendant cosmetics) | **16-player raid**, Season 4 unlock only                |

### Boss Quick Reference

| Dungeon | Boss                      | Concept                                                                    |
| ------- | ------------------------- | -------------------------------------------------------------------------- |
| 1       | The Hollow Knight         | Armoured spectral guardian; glyph plate phase mechanic                     |
| 2       | Waterkeeper Maldren       | Undead flood controller; drain 3 levers in Phase 2                         |
| 3       | The Thornmother           | Immobile vine controller; burn all 6 tendrils simultaneously               |
| 4       | Root Warden Kaeseth       | Ancient treant; redirect light beam to hit 3 glowing knots                 |
| 5       | Resonance Wraith Olveth   | Phase through music; 4 players on dampener pads simultaneously             |
| 6       | The Spire Guardian        | 3 gravity forms: floor → ceiling → walls                                   |
| 7       | General Hroth the Frozen  | Ice-floor giant; 4 heat crystals create safe zones                         |
| 8       | Storm Drake Vethran       | Flying drake; land windows + doubled gusts in Phase 2                      |
| 9       | Forgemaiden Scorra        | Ember champion; lava expands each phase; bellows jets in Phase 3           |
| 10      | The Ashen Archon          | Undead fire colossus; fire immunity, cold vulnerability; ash cloud Phase 3 |
| 11      | The First Bloom           | Aggression-adaptive boss; peaceful or rage form based on player behaviour  |
| 12      | Archivist Prime           | Knowledge construct; rewinds player positions in Phase 3                   |
| 13      | Rift Sovereign            | Rotating pool of 5 remixed prior bosses; ensures replay variety            |
| 14      | The Rootbinder (Awakened) | Split then combined 16-player fight; 3-choice Act 4 resolution             |
| 15      | The Weaver's Echo         | 4 simultaneous crystal lens puzzles while tanks hold aggro                 |

***

## 5. Town Directory

### Millhaven

| Field        | Value                                                                                                                                                                                                                                  |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Zone ID      | `millhaven-town`                                                                                                                                                                                                                       |
| Region       | Millhaven Starter Region                                                                                                                                                                                                               |
| Biome        | Coastal Town                                                                                                                                                                                                                           |
| Level Range  | 1–5 (entry)                                                                                                                                                                                                                            |
| Faction      | Neutral                                                                                                                                                                                                                                |
| Fast Travel  | Yes                                                                                                                                                                                                                                    |
| **Key NPCs** | Elder Rowan (Quest: Tutorial chain), Mira the Fisherman (Fishing vendor, Driftwood Rod 50g), Guildmaster Aldric (Guild introduction quest), Tom the Innkeeper (respawn point), Wandering Merchant Cressida (rotating stock, 1hr cycle) |
| **Services** | Inn/Respawn, General Store, Blacksmith (Level 1–5 gear), Notice Board, Fishing Dock (Millhaven Docks — Common/Uncommon fish), Basic Crafting Table                                                                                     |
| **Lore**     | Millhaven is the quiet coastal village where the player character arrives by boat. Once a prosperous fishing town, it now struggles since the Aether Wastes began spreading. It is the unofficial "first chapter" of the game's story. |

***

### City of Aethermoor

| Field        | Value                                                                                                                                                                                                                                                                                                        |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Zone ID      | `aethermoor-city`                                                                                                                                                                                                                                                                                            |
| Region       | City of Aethermoor Hub                                                                                                                                                                                                                                                                                       |
| Biome        | Walled City                                                                                                                                                                                                                                                                                                  |
| Level Range  | 1–20 (all-purpose hub)                                                                                                                                                                                                                                                                                       |
| Faction      | Neutral (both factions have envoys; no territory control)                                                                                                                                                                                                                                                    |
| Fast Travel  | Yes (main hub — all routes converge here)                                                                                                                                                                                                                                                                    |
| **Key NPCs** | Grand Archivist Selemeth (main story quest giver — Acts 1–4), Faction Envoy: Commander Vael (Aetheric Order), Faction Envoy: Sylvara Dawnbloom (Verdant Pact), Auctioneer Brenn (AH), Banker Hollis, Housing Registrar Petra, Lore Keeper Oswin, All 6 Class Trainers (one per class), Crafting Guild Master |
| **Services** | Inn/Respawn, General Store, Blacksmith, Crafting Workshop (all professions), Auction House, Bank, Guild Hall (create/manage guilds), Housing Registrar, Notice Board, Faction Envoys (both), All Class Trainers, Lore Keeper, Fast Travel Hub                                                                |
| **Lore**     | The ancient capital of AETHERMOOR — once the seat of the First Root civilisation, now a bustling multicultural city. The Grand Archive beneath the city is where players discover the truth about the Rootbinder.                                                                                            |

***

### Thornhaven

| Field          | Value                                                                                                                                                                                                               |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Zone ID        | (within `darkwood-edge` — town sits at the zone border)                                                                                                                                                             |
| Zone ID (town) | `thornhaven-village` *(sub-zone of darkwood-edge)*                                                                                                                                                                  |
| Region         | Darkwood Forest                                                                                                                                                                                                     |
| Biome          | Forest Village                                                                                                                                                                                                      |
| Level Range    | 5–15                                                                                                                                                                                                                |
| Faction        | Verdant Pact (stronghold)                                                                                                                                                                                           |
| Fast Travel    | No (encourages exploration)                                                                                                                                                                                         |
| **Key NPCs**   | Elder Sylvan Kor (Verdant Pact quest chain), Herbalist Menna (rare herb vendor), Ranger Captain Dusk (PvP faction quests), Woodcrafter Aldis (crafting recipes: Darkwood set), Treant Watcher NPC (Blighted Vault lore) |
| **Services**   | Inn/Respawn, Herbalist (Uncommon alchemy mats), Woodcrafter Workshop, Notice Board, Verdant Pact Quartermaster (faction gear)                                                                                       |
| **Lore**       | Deep in the forest, Thornhaven is the Verdant Pact's ancestral home. The treants have protected it for centuries. The Blighted Vault story hooks originate here.                                                    |

***

### Frosthold

| Field        | Value                                                                                                                                                                                                                                                                                        |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Zone ID      | `frostpeak-town`                                                                                                                                                                                                                                                                             |
| Region       | Frostpeak Mountains                                                                                                                                                                                                                                                                          |
| Biome        | Mountain Fortress Town                                                                                                                                                                                                                                                                       |
| Level Range  | 9–20                                                                                                                                                                                                                                                                                         |
| Faction      | Aetheric Order (primary stronghold)                                                                                                                                                                                                                                                          |
| Fast Travel  | Yes                                                                                                                                                                                                                                                                                          |
| **Key NPCs** | Commander Iorn (Aetheric Order quest chain — Frostpeak arc), Armourer Gretha (Cold-resistance gear, Fur Cloak vendor), Fur Trader Voss (Cold Weather gear — required for glacier zones), Dungeon Scout Halverd (hints for Dungeon 7 and 8), Ice Sage Mirova (lore: The Frozen General quest) |
| **Services** | Inn/Respawn, Blacksmith (Cold-resistance & Frostplate gear), Fur/Cold Weather gear vendor, Notice Board, Aetheric Order Quartermaster, Fast Travel                                                                                                                                           |
| **Lore**     | Carved into the mountainside generations ago, Frosthold is the Order's northernmost garrison. The discovery of the Frost Tomb has made it strategically vital.                                                                                                                               |

***

### Emberton

| Field        | Value                                                                                                                                                                                                                                                                     |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Zone ID      | `emberton-town`                                                                                                                                                                                                                                                           |
| Region       | Ember Plains                                                                                                                                                                                                                                                              |
| Biome        | Industrial Fortress Town                                                                                                                                                                                                                                                  |
| Level Range  | 11–20                                                                                                                                                                                                                                                                     |
| Faction      | Aetheric Order (secondary stronghold)                                                                                                                                                                                                                                     |
| Fast Travel  | Yes                                                                                                                                                                                                                                                                       |
| **Key NPCs** | Warlord Caena (Ember Plains quest chain — Ember Tribe conflict), Alchemist Dunn (Alchemy vendor + rare bait), Forgemaster Orin (Epic crafting services), Sunken Docks Quartermaster (PvP: Sunken Docks faction rewards), Fishing Vendor Salia (fishing gear, Shrimp bait) |
| **Services** | Inn/Respawn, Blacksmith (Fire-resistance gear), Alchemy vendor, Crafting Workshop, Notice Board, Aetheric Order Quartermaster, Fishing supplies vendor, Fast Travel                                                                                                       |
| **Lore**     | Built on the bones of an older Ember Tribe settlement, Emberton is the industrial heart of Aetheric Order expansion. The Ember Forge dungeon quest chain starts here.                                                                                                     |

***

### Sunken Harbor

| Field        | Value                                                                                                                                                                                                                                                                                                              |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Zone ID      | `sunken-harbor-town`                                                                                                                                                                                                                                                                                               |
| Region       | Ember Plains & Sunken Harbor                                                                                                                                                                                                                                                                                       |
| Biome        | Coastal Port Town                                                                                                                                                                                                                                                                                                  |
| Level Range  | 11–20                                                                                                                                                                                                                                                                                                              |
| Faction      | Neutral (factions compete for the adjacent Docks, not the town itself)                                                                                                                                                                                                                                             |
| Fast Travel  | Yes                                                                                                                                                                                                                                                                                                                |
| **Key NPCs** | Harbormaster Dred (shipping/trade quests), Charter Captain Yenna (fast travel: ship to Sky Docks, Level 15+ unlock), Fishing Supply merchant Rael (Rare bait, Crystal Rod vendor), Sunken Docks Scout NPC (real-time PvP territory status report), Black Market rumour NPC (hints at Sunken Docks faction rewards) |
| **Services** | Inn/Respawn, Fishing Supply vendor, Ship charter (Sky Archipelago fast travel), Shipwright (housing: boat items), Notice Board, General Store, Fast Travel                                                                                                                                                         |
| **Lore**     | A port town that has always remained neutral — too valuable to either faction to risk burning. The contested Sunken Docks lie just outside the town's limits.                                                                                                                                                      |

***

### Verdant Canopy Village

| Field          | Value                                                                                                                                                                                                                                                     |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Zone ID        | (within `verdant-jungle-canopy`)                                                                                                                                                                                                                          |
| Zone ID (town) | `verdant-canopy-village` *(sub-zone of verdant-jungle-canopy)*                                                                                                                                                                                            |
| Region         | Verdant Jungle                                                                                                                                                                                                                                            |
| Biome          | Treetop Village                                                                                                                                                                                                                                           |
| Level Range    | 13–20                                                                                                                                                                                                                                                     |
| Faction        | Verdant Pact (deep stronghold)                                                                                                                                                                                                                            |
| Fast Travel    | Yes                                                                                                                                                                                                                                                       |
| **Key NPCs**   | High Rootkeeper Thessan (Verdant Pact — Act 3 story arc), Herbalist Lorn (Epic herb/alchemy mats), Bloom Scout Kael (Dungeon 11 quest chain — Bloom Sanctum), Craftmaster Sylvine (Epic Verdant crafting recipes), Sunken Archives Sage (Dungeon 12 lore) |
| **Services**   | Inn/Respawn, Alchemy Workshop (specialised: Epic nature mats), Verdant Pact Quartermaster (Epic faction gear), Crafting Workshop, Notice Board, Fast Travel                                                                                               |
| **Lore**       | Suspended among the oldest trees in the world, the Canopy Village is the spiritual heart of the Verdant Pact. Players arrive here during the Act 3 story arc to confront the truth about the First Bloom.                                                 |

***

### Sky Station

| Field        | Value                                                                                                                                                                                                                                    |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Zone ID      | `sky-archipelago-docks`                                                                                                                                                                                                                  |
| Region       | Sky Archipelago                                                                                                                                                                                                                          |
| Biome        | Elevated Port/Town                                                                                                                                                                                                                       |
| Level Range  | 15–20                                                                                                                                                                                                                                    |
| Faction      | Neutral                                                                                                                                                                                                                                  |
| Fast Travel  | Yes (endgame hub)                                                                                                                                                                                                                        |
| **Key NPCs** | Sky Scholar Evren (lore: Weaver myth — Season 4 setup), Epic Gear Vendor Maelon (gold-only, no AH bypass — curated epic pieces), Rift Expedition Scout (Dungeon 13 lore + hints), Legendary Fisher NPC (tracks server Leviathan catches) |
| **Services** | Inn/Respawn, Epic Gear vendor (gold only), Legendary crafting station, Notice Board, Ship/Sky Charter hub, Fast Travel                                                                                                                   |
| **Lore**     | A remote and ancient dock, Sky Station was built by the Weaver's followers centuries ago. It is the gateway to endgame content and the Season 4 story arc.                                                                               |

***

## 6. PvP Contested Territory Summary

> All PvP zones use the Aetheric Order vs. Verdant Pact faction system. Territory flips via capture-point control. Non-flagged players can enter but will not be attacked (PvP flag is opt-in except inside PvP zone boundaries).

| # | Zone ID                | Name                 | Level Range | Control Points                      | Reward (Controlling Faction)                                                            |
| - | ---------------------- | -------------------- | ----------- | ----------------------------------- | --------------------------------------------------------------------------------------- |
| 1 | `thornwood-crossroads` | Thornwood Crossroads | 8–12        | Lumber Mill, Herb Garden            | +20% Thornwood Lumber drop rate; Thornwood Quartermaster unlocked                       |
| 2 | `sunken-docks-pvp`     | Sunken Docks         | 13–18       | North Dock, South Dock              | +20% rare fish catch rate; Black Market vendor access                                   |
| 3 | `crystal-summit-pvp`   | Crystal Summit       | 13–17       | Mine North, Mine Centre, Mine South | +20% Aether Crystal yield; Crystal Quartermaster unlocked                               |
| 4 | `verdant-pass-pvp`     | Verdant Pass         | 14–18       | Spice Road flag, Poison Garden      | +20% rare herb drop rate; Verdant Pass Quartermaster unlocked                           |
| 5 | `aether-nexus-pvp`     | Aether Nexus         | 17–20       | Siphon A, Siphon B, Siphon C        | **+5% all stats server-wide** for all faction members; Endgame cosmetic vendor unlocked |

**Mechanics (shared across all PvP zones):**

* Capture progress: 3 minutes uncontested to capture a point
* Territory status is polled server-side every 30 seconds; all clients notified on flip
* Players who die in PvP zones respawn at the nearest friendly town (not inside the PvP zone)
* Kills grant faction standing points (Honored / Revered / Exalted tiers)

***

## 7. Fast Travel Waypoint Network

Fast travel is unlocked by visiting a waypoint for the first time. Travel between any two discovered waypoints costs gold (scaled by distance).

| Waypoint ID          | Location                          | Zone ID                  | Available From                                     |
| -------------------- | --------------------------------- | ------------------------ | -------------------------------------------------- |
| `wp-millhaven`       | Millhaven Town Square             | `millhaven-town`         | Level 1 (default)                                  |
| `wp-aethermoor-city` | City of Aethermoor, Central Plaza | `aethermoor-city`        | Discovered on first visit                          |
| `wp-frosthold`       | Frosthold Garrison Gate           | `frostpeak-town`         | Discovered on first visit                          |
| `wp-emberton`        | Emberton Market Square            | `emberton-town`          | Discovered on first visit                          |
| `wp-sunken-harbor`   | Sunken Harbor Dock                | `sunken-harbor-town`     | Discovered on first visit                          |
| `wp-verdant-village` | Verdant Canopy Village Platform   | `verdant-canopy-village` | Discovered on first visit                          |
| `wp-verdant-deep`    | Verdant Deep Ruins                | `verdant-jungle-deep`    | Discovered on first visit                          |
| `wp-aether-wastes`   | Aether Wastes Cairn               | `aether-wastes-deep`     | Discovered on first visit                          |
| `wp-sky-station`     | Sky Station Dock                  | `sky-archipelago-docks`  | Discovered on first visit (Level 15+ ship charter) |

**Gold costs (one-way, approximate):**

| From               | To                 | Cost |
| ------------------ | ------------------ | ---- |
| Millhaven          | City of Aethermoor | 5g   |
| City of Aethermoor | Frosthold          | 25g  |
| City of Aethermoor | Emberton           | 30g  |
| City of Aethermoor | Sunken Harbor      | 35g  |
| Emberton           | Sunken Harbor      | 10g  |
| Sunken Harbor      | Verdant Village    | 40g  |
| Verdant Village    | Aether Wastes      | 50g  |
| Aether Wastes      | Sky Station        | 60g  |

***

## 8. MMO Considerations

| Concern                     | Design Decision                                                                                                                                                                     |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Zone capacity               | Overworld zones: 50 players per shard. Towns: 200–300 (persistent, shared). PvP zones: 100 (higher for faction balance). Dungeons: 1–4 (private). Raid zones: 16 (private).         |
| Shard overflow              | When a zone reaches capacity, new entrants are placed in a fresh shard. Players can manually switch to a friend's shard via the Party join option.                                  |
| Zone instancing             | Overworld zones are sharded (soft instances). Towns are fully persistent and shared. Dungeons/Raids are always private instances.                                                   |
| Player density balance      | 50-player cap on overworld prevents resource monopoly. Rare resource nodes have 10-minute server-side respawn; zone-wide respawn announced in zone chat.                            |
| PvP zone population         | Separate shard logic for PvP zones: balanced by faction count (matchmaker tries to keep within 10% of faction parity). Overflow creates a new shard, not a queue.                   |
| Night/day cycle             | Game-time day/night cycle (1 real hour \= 2 in-game hours). Affects: Crystal Lake fishing (night only), certain enemy spawns, NPC schedules. All clients sync via server broadcast. |
| World event synchronisation | World events (Rift Incursion, Frost Giant Incursion, Ember Tide) are broadcast server-wide via WebSocket. All shards of the affected zone activate simultaneously.                  |
| Fast travel cost            | Paid fast travel discourages excessive hub-hopping; encourages organic zone traversal and world discovery.                                                                          |

***

## 9. Technical Notes for CTO

> These notes are specific to implementing this world-map spec in the Game World Service (RPGAA-10).

| Item                           | Spec                                                                                                                                                                                                                                                                                                                     |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Zone registry schema           | Each zone row \= { zone\_id (slug), name, biome, level\_min, level\_max, max\_players, connections (array of zone\_id strings), pois (array), is\_pvp (bool), pvp\_factions (array or null), has\_fishing (bool), fishing\_tier (enum or null), has\_fast\_travel (bool), waypoint\_id (string or null), region (enum) } |
| `connections` field            | Bidirectional adjacency list. If zone A lists B in connections, B must also list A. CTO to enforce at seed time.                                                                                                                                                                                                         |
| Zone biome enum                | `town`, `grassland`, `forest`, `underground`, `cave`, `mountain`, `glacier`, `plains`, `volcanic`, `jungle`, `coastal`, `dimensional`, `island`, `aerial`, `raid`, `instanced`                                                                                                                                           |
| Sub-zones (towns within zones) | Millhaven-town and sky-archipelago-docks are standalone zone IDs. Thornhaven Village and Verdant Canopy Village are sub-zones of their parent overworld zone — implement as child zones with a `parentZoneId` field, or as standalone zones connected to their parent. Recommend standalone for simplicity.              |
| Dungeon entrance POIs          | Each dungeon entrance is a POI within its parent zone. POI record: { poi\_id, zone\_id, type: "dungeon\_entrance", dungeon\_id, display\_name, tile\_x, tile\_y }. Tile coordinates are placeholder (0,0) until tile maps are authored.                                                                                  |
| Fishing spot POIs              | POI type: `fishing_spot`. Include { fishing\_tier, time\_restriction (null or "night"), level\_requirement, player\_cap (8 per dock node), requires\_cold\_gear (bool) }.                                                                                                                                                |
| PvP zone entry                 | Entry to a PvP zone automatically flags the player for PvP. Zone entry event triggers a client-side warning modal (first time only; subsequent entries skip modal).                                                                                                                                                      |
| Fast travel                    | Waypoints stored separately from zone registry. Waypoint record: { waypoint\_id, zone\_id, display\_name, unlock\_requirement (null \= free, or { level: N } or { quest\_id: X }) }. Fast travel cost lookup table keyed by (origin\_waypoint\_id, dest\_waypoint\_id).                                                  |
| Night/day cycle                | Server-authoritative clock. Current time broadcast via WebSocket on connect and every 10 minutes. Clients derive in-game time locally from server timestamp. Crystal Lake fishing availability computed server-side (not client-trusting).                                                                               |
| Housing zones                  | Instanced dynamically on first housing purchase. housing-district-\[plot-id] is a template zone; each instance is a clone seeded at deed purchase time.                                                                                                                                                                  |
| Zone count                     | 28 named overworld/town zones + 2 raid zones + 1 hidden zone + housing template \= **\~32 zone registry entries** for seed. Dungeons are spawned as instance pods, not persistent zones — not in zone registry.                                                                                                          |

***

## 10. Open Questions

| #    | Question                                                                                                                                                                                                                                                                          | Priority | Owner                            |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | -------------------------------- |
| OQ-1 | Should Thornhaven Village and Verdant Canopy Village be standalone zone IDs or sub-zones of their parent overworld zone? Standalone is simpler but adds zone registry entries. Sub-zone requires a `parentZoneId` field in the schema.                                            | High     | CTO decision                     |
| OQ-2 | The GDD says "8 world regions" but the dungeon bestiary identifies 6 numbered regions. Sky Archipelago, Goblin Wastelands, and Sunken Harbor are treated as independent areas in this document. Should Sky Archipelago + Aether Wastes form one combined Region 7, or stay split? | Medium   | CEO sign-off                     |
| OQ-3 | Tile map coordinates are placeholder (0,0) for all dungeon entrance and fishing POIs. When does the tile map authoring begin, and who produces tilemap JSON — a level designer tool, hand-authored, or procedural? This blocks the CTO's ability to seed real tile positions.     | High     | CEO / CTO alignment              |
| OQ-4 | The Hidden Grotto is currently reachable only via a hidden entrance in `sky-archipelago-islands`. Should the hint mechanism (World Lore scroll) be a specific quest chain, or a random drop from exploration? This affects quest design and drop table design.                    | Medium   | CEO approval                     |
| OQ-5 | Fast travel gold costs are approximate. Should these be live-configurable from an admin panel (fits the GDD admin panel requirement) or hardcoded at launch? Recommend live-configurable.                                                                                         | Low      | CTO to confirm feasibility       |
| OQ-6 | The Temple of the Deep (Raid) is the Act 4 climax with a 3-choice narrative ending. Each ending changes the post-raid world state. This requires the CTO to support per-server "world state flags" that affect NPC dialogue and zone appearance. Is this in scope for launch?     | Critical | CEO decision — significant scope |

***

## Version History

| Version | Date       | Author        | Summary                                                                                                                                                                              |
| ------- | ---------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| v1.0    | 2026-04-14 | Game Designer | Initial draft — full zone register (28 zones), overworld traversal diagram, 15 dungeon entries, 8 town profiles, 5 PvP territory summaries, fast travel network, CTO technical notes |
| v1.1    | 2026-04-19 | Game Designer | Renamed Region 2 from "Thornwood Forest" to **Darkwood Forest** (CEO canonical decision — [RPG-73](/RPG/issues/RPG-73)). Updated all `thornwood-*` zone IDs to `darkwood-*`. Replaced placeholder Dungeon 3 (Bramble Maze) with Blighted Vault. Added `darkwood-depths` sub-zone. Updated all cross-zone connection references. |
