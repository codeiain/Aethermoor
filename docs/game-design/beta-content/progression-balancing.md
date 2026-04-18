# Progression Balancing — Project AETHERMOOR

**Document:** progression-balancing.md
**Milestone:** Beta
**Version:** 1.0
**Date:** 2026-04-15
**Author:** Game Designer

---

## 1. Overview

This document defines the full progression balance for AETHERMOOR across levels 1–20. It covers:

- XP curve: total XP required per level and typical time-to-level
- Gold economy: item costs, vendor prices, reward amounts, inflation guards
- Combat balance: expected DPS/effective damage per class per tier
- Death penalty calibration: 10% durability loss impact analysis

**Design intent:** Players should feel meaningful growth every session. Early levels are fast (30–60 min each) to hook new players. Mid-game slows moderately. Endgame (16–20) requires sustained engagement without feeling like a grind wall.

---

## 2. Design Goals

| Goal | Rule |
|---|---|
| Regular forward progress | Players should level at least once per 2-hour session through level 15 |
| Gold stays meaningful | Gold should be worth spending at every level — never trivially flush |
| Class identity | Each class should feel meaningfully different in combat output |
| Death has consequence | Durability loss hurts but never destroys a casual player's session |
| Inflation resistance | Gold sinks must absorb at least 60% of gold entering the economy |

---

## 3. XP Curve — Levels 1–20

### 3.1 Formula

XP required to reach level N:

```
XP_to_level(N) = base * N^exponent
base = 100
exponent = 1.65
```

Resulting in a progressive curve that steepens at mid-game and plateaus slightly at endgame.

### 3.2 XP Table

| Level | XP to Reach Level | Cumulative XP | Target Time-to-Level | Typical Activities at This Level |
|---|---|---|---|---|
| 1 | 0 (start) | 0 | — | Character creation, Millhaven intro quests |
| 2 | 100 | 100 | 10–15 min | First goblin encounters, Lila's Flowers quest |
| 3 | 192 | 292 | 15–20 min | Whispering Forest edge, escort quests |
| 4 | 298 | 590 | 20–25 min | Sunken Crypt B1 first run |
| 5 | 420 | 1,010 | 25–35 min | Crypt full clear, goblin chief boss |
| 6 | 558 | 1,568 | 35–45 min | Return quests, gear upgrades in Millhaven |
| 7 | 714 | 2,282 | 40–55 min | Crossroads (Beta town) arrival |
| 8 | 886 | 3,168 | 45–60 min | Thornback Wastes exploration |
| 9 | 1,076 | 4,244 | 50–65 min | Thornback elite encounters |
| 10 | 1,283 | 5,527 | 60–75 min | Ashenveil Dungeon first clear, subclass unlock |
| 11 | 1,508 | 7,035 | 65–80 min | Ashenveil B2 access (future), Crossroads guild hall |
| 12 | 1,751 | 8,786 | 70–90 min | Thornback named enemies, rare loot |
| 13 | 2,012 | 10,798 | 80–100 min | Faction alignment quests begin |
| 14 | 2,291 | 13,089 | 85–105 min | World event participation |
| 15 | 2,588 | 15,677 | 90–110 min | Ashenveil boss challenge mode |
| 16 | 2,904 | 18,581 | 100–120 min | PvP zones accessible |
| 17 | 3,237 | 21,818 | 105–130 min | Guild raid entry tier |
| 18 | 3,589 | 25,407 | 115–140 min | Endgame gear chase begins |
| 19 | 3,959 | 29,366 | 120–150 min | World boss participation |
| 20 | 4,347 | 33,713 | 130–160 min | Level cap — prestige system opens |

**Total time to max level (level 1→20):** ~25–35 hours of active play

### 3.3 XP Sources

| Source | XP per Instance | Notes |
|---|---|---|
| Quest completion (main) | 200–800 XP | Scales with quest tier; see quest log |
| Quest completion (side) | 75–350 XP | Optional content, per quest |
| Monster kill | 15–120 XP | Based on monster tier (see table below) |
| Dungeon boss kill | 300–1,200 XP | First clear bonus +50% |
| Daily quest | 150–400 XP | Capped at 3 dailies per day |
| Party bonus | +15% XP | Applied when in a party of 2–4 |
| Rested XP (Inn/Home) | +25% for 30 min | Stacks with party bonus |
| World event | 500–2,000 XP | Shared pool, proportional contribution |

### 3.4 Monster XP by Tier

| Monster Tier | Level Range | XP per Kill |
|---|---|---|
| T1 — Minion | 1–5 | 15–30 XP |
| T2 — Standard | 6–10 | 40–70 XP |
| T3 — Elite | 11–15 | 80–120 XP |
| T4 — Named | 16–19 | 130–200 XP |
| T5 — Boss | Any | 300–1,200 XP |

**Anti-farming rule:** Monster XP applies a per-session diminishing return. After 100 kills of the same monster type in a single session: -25% XP. Resets after 30 min offline. This prevents zone-farming and encourages content variety.

---

## 4. Gold Economy

### 4.1 Design Intent

Gold enters the game through quests, mob drops, and activities. It exits through vendor purchases, repairs, crafting, housing, and listing fees. The goal is a steady-state economy where gold has value at all levels.

**Target net gold sink:** 60–70% of all gold entering the economy should exit each week.

### 4.2 Gold Sources

| Source | Gold Range | Notes |
|---|---|---|
| Quest reward (main) | 50–2,000g | Scales: 50g at L1, 2,000g at L20 main quest |
| Quest reward (side) | 20–500g | Optional content, smaller rewards |
| Daily quest | 25–100g | Hard cap per day to prevent farming |
| Monster drop | 1–50g per kill | Base rate; diminishing returns after 50 kills/session |
| Dungeon chest | 50–800g | Scales with dungeon tier |
| World event | 200–1,500g | Shared pool, proportional contribution |
| Player trade | Variable | No gold injection — wealth redistribution only |
| Vendor sell (items) | 10–40% item value | Players selling loot to vendors |

### 4.3 Gold Sinks

| Sink | Cost Range | Tier |
|---|---|---|
| Equipment repair | 5–300g per item | All levels |
| Vendor purchases (consumables) | 10–500g each | All levels |
| Vendor purchases (equipment) | 50–5,000g | L1–20 |
| Inn stay (Rested XP) | 10–50g per night | All levels |
| Crafting material cost | 20–2,000g | All levels |
| Housing purchase (plot deed) | 500–5,000g | Unlocked L5+ |
| Housing furniture | 50–10,000g | Ongoing long-term sink |
| Auction House listing fee | 5% of sale price | Economy fee |
| Fast travel (between zones) | 15–80g per trip | Convenience |
| Respawn at dungeon checkpoint | 20–150g | Scales with dungeon tier |
| Guild bank deposit / upgrades | 1,000–10,000g | Collective sink |

### 4.4 Gold per Hour by Play Style

| Play Style | Levels | Target Gold/hr | Primary Sinks |
|---|---|---|---|
| Casual questing | 1–10 | 80–150g/hr | Repairs, consumables, inn |
| Dungeon runner | 10–20 | 300–600g/hr | Repairs, AH fees, housing |
| Crafter / fisher | Any | 100–400g/hr | Materials, listing fees |
| Endgame raider | 16–20 | 800–1,500g/hr | High-end repairs, consumables, AH |

### 4.5 Vendor Price Reference

| Item Category | Level Range | Price Range |
|---|---|---|
| Health Potion (Minor) | 1–5 | 15g |
| Health Potion (Standard) | 6–12 | 45g |
| Health Potion (Major) | 13–20 | 120g |
| Mana Potion (Minor) | 1–5 | 20g |
| Mana Potion (Standard) | 6–12 | 55g |
| Mana Potion (Major) | 13–20 | 140g |
| Antidote | Any | 30g |
| Common weapon (vendor) | 1–5 | 60–150g |
| Uncommon weapon (vendor) | 6–10 | 200–600g |
| Rare weapon (AH only) | 11–15 | 1,000–3,000g |
| Epic weapon (AH/drop only) | 16–20 | 5,000–15,000g |
| Dungeon key (consumable) | Varies | 25–75g |

### 4.6 Inflation Guards

- **Daily gold caps:** Daily quests cap at 100g/day per player
- **Diminishing returns:** Monster gold drops decay -10% per 50 kills/session
- **Auction House fee:** 5% non-refundable listing fee removes gold on all transactions
- **Repair costs scale with gear tier:** High-end players face high-end repair bills — this is intentional
- **Season reset:** Each seasonal reset (every ~3 months) introduces a new gold sink (seasonal event store) and adjusts vendor prices by ±5–15% based on economy data

---

## 5. Combat Balance — Per Class Per Tier

### 5.1 Framework

Combat balance is expressed as **expected output per 10-second combat window** across four tiers. "Output" covers:
- **DPS Class:** Total damage dealt to a single target (burst + sustained)
- **Support Class:** Healing/buffing effectiveness (not DPS)
- **Tank Class:** Effective HP (actual HP × damage reduction factor)

All values assume:
- Full ability rotation for the class
- No party bonuses (solo baseline)
- Enemy AC = 14 (standard encounter AC)
- Stat scores at class archetype peak (STR 18 for Knight at cap, etc.)

### 5.2 Tier 1 — Levels 1–5 (Early Game)

At this tier, all classes feel approachable. Variance is low. The goal is teaching the core loop.

| Class | Role | Damage/10s | Effective HP | Notes |
|---|---|---|---|---|
| **Knight** | Tank/Melee DPS | 45–60 | 85–120 | Power Strike, basic auto-attacks |
| **Archmage** | Magic DPS | 55–70 | 45–60 | Frost Bolt primary; fragile |
| **Shadowblade** | Burst DPS | 60–80 | 55–75 | Sneak Attack procs; gap in cooldowns |
| **Warden** | Healer | 15–25 dmg / 40–60 healing | 65–85 | Focus is on keeping self and party alive |
| **Ranger** | Ranged DPS | 50–65 | 60–80 | Consistent ranged output; kiting strength |
| **Bard** | Support | 20–35 dmg / +10% party buff | 60–80 | Buffs not yet impactful at this tier |

### 5.3 Tier 2 — Levels 6–10 (Mid-Game Entry)

Classes diverge meaningfully. Subclass begins to feel anticipated (unlocks at L10).

| Class | Role | Damage/10s | Effective HP | Notes |
|---|---|---|---|---|
| **Knight** | Tank/Melee DPS | 90–130 | 160–220 | Cleave + Extra Attack; tanking via Second Wind |
| **Archmage** | Magic DPS | 130–175 | 70–90 | Chain Lightning spike damage; fragile glass cannon |
| **Shadowblade** | Burst DPS | 150–200 (burst) / 80–100 sustained | 90–120 | Shadow Step + Sneak Attack spike; vulnerable after burst window |
| **Warden** | Healer | 25–45 dmg / 80–120 healing | 100–140 | Mass Cure Word begins to enable party play |
| **Ranger** | Ranged DPS | 110–150 | 110–140 | Multi-arrow AoE; consistent safe-range output |
| **Bard** | Support | 40–60 dmg / +15–20% party buff | 100–130 | Bardic Inspiration meaningfully raises party ceiling |

### 5.4 Tier 3 — Levels 11–15 (Mid-Game Peak)

Full ability rotations. Subclass abilities online. Party synergies become defining.

| Class | Role | Damage/10s | Effective HP | Notes |
|---|---|---|---|---|
| **Knight (Guardian)** | Tank | 110–150 | 280–360 | Aura of Protection + high AC — raid/dungeon anchor |
| **Knight (Berserker)** | Melee DPS | 200–270 | 180–240 | Frenzy rotation; risky but highest melee burst |
| **Archmage** | Magic DPS | 280–380 | 90–110 | Arcane Storm burst; still fragile — needs protection |
| **Shadowblade** | Burst DPS | 300–420 (burst) / 120–160 sustained | 110–140 | Shadow Chain combos; dominates single target |
| **Warden** | Healer | 50–75 dmg / 160–220 healing | 140–180 | Resurrection online at L11; party lifeline |
| **Ranger** | Ranged DPS | 180–240 | 150–190 | Eagle Eye crit builds come online |
| **Bard** | Support | 70–100 dmg / +25–30% party buff | 140–170 | Countercharm + Symphony of War enable spike-damage windows for whole party |

### 5.5 Tier 4 — Levels 16–20 (Endgame)

Max expression of each class. Designed for group content — true solo viability reduced for DPS classes.

| Class | Role | Damage/10s | Effective HP | Notes |
|---|---|---|---|---|
| **Knight (Guardian)** | Tank | 160–220 | 450–600 | Immovable Object + Iron Will — unkillable anchor in raids |
| **Knight (Berserker)** | Melee DPS | 380–520 | 250–320 | Warlord's Strike finisher; high execution ceiling |
| **Archmage** | Magic DPS | 550–750 | 110–130 | Reality Fracture — highest burst in game; zero survivability |
| **Shadowblade** | Burst DPS | 600–800 (burst) / 180–240 sustained | 140–170 | Perfect Execution opener; dominates all single-target content |
| **Warden** | Healer | 80–120 dmg / 300–450 healing | 170–220 | Divine Intervention clutch save; mandatory in raids |
| **Ranger** | Ranged DPS | 320–440 | 190–240 | Storm of Arrows AoE — zone-clearing specialist |
| **Bard** | Support | 100–150 dmg / +35–40% party buff | 170–210 | Epic Ballad at L16 — highest party multiplier in game |

### 5.6 Balance Intent

- **No class should feel mandatory or useless.** All classes must be viable in group content.
- **Warden should never be forced.** Group content should be clearable without a healer (just slower/riskier).
- **DPS ceiling:** Shadowblade > Archmage > Knight(Berserker) > Ranger > Bard > Knight(Guardian) > Warden for single target.
- **Raid utility ceiling:** Warden > Bard > Knight(Guardian) > Ranger > Knight(Berserker) > Archmage > Shadowblade.

**CTO note:** Track per-class kill counts in dungeon telemetry. If one class contributes <50% expected share in boss kills post-launch, flag for balance review. Balance patches should be ±10–15% adjustments — not sweeping reworks.

---

## 6. Death Penalty Calibration

### 6.1 System Summary

On death, a player loses **10% durability** on all equipped items. Durability loss accumulates until items reach 0%, at which point they break and become unusable until repaired.

Items have the following durability pools:

| Item Rarity | Max Durability |
|---|---|
| Common | 50 |
| Uncommon | 75 |
| Rare | 100 |
| Epic | 150 |

### 6.2 Death Cost Analysis by Level

| Level | Avg Item Tier | Repair Cost per Item | Items Equipped | Total Repair per Death |
|---|---|---|---|---|
| 1–5 | Common | 5–15g per 10% loss | 3–4 slots | 20–60g per death |
| 6–10 | Uncommon | 15–40g per 10% loss | 4–5 slots | 60–200g per death |
| 11–15 | Rare | 40–100g per 10% loss | 6 slots | 240–600g per death |
| 16–20 | Epic | 100–250g per 10% loss | 6–7 slots | 600–1,750g per death |

### 6.3 Death Impact vs. Expected Gold/hr

| Level Range | Gold/hr (avg) | Gold per Death | Deaths to Lose 1hr Income |
|---|---|---|---|
| 1–5 | 80–150g | 20–60g | 2–7 deaths |
| 6–10 | 150–300g | 60–200g | 2–5 deaths |
| 11–15 | 300–500g | 240–600g | 1–2 deaths |
| 16–20 | 600–1,500g | 600–1,750g | 1 death |

### 6.4 Design Intent

- **Early game (1–5):** Death is cheap. Encourages experimentation. A new player dying 5–6 times costs less than 30 minutes of questing.
- **Mid-game (6–15):** Death becomes a real decision. Players start considering retreat. Dungeon wipes cost meaningful gold but don't break a session.
- **Endgame (16–20):** Death is expensive. 1–2 deaths can wipe a session's gold income. Raid wipes have genuine stakes. This is intentional — endgame should feel meaningful.

### 6.5 Edge Cases

| Case | Rule |
|---|---|
| Death in tutorial zone (levels 1–2) | No durability loss — player can respawn freely |
| PvP death | No durability loss (separate PvP system) |
| Death at 0% durability | Item becomes "broken" — unusable until repaired. Player can still respawn with broken items equipped (visual indicator: cracked item border) |
| Durability loss on off-hand item | Full 10% loss applies — off-hand is included in calculation |
| Death by environment (fall, water) | Full durability loss applies |

### 6.6 Respawn Options

| Option | Cost | Outcome |
|---|---|---|
| Respawn at graveyard | Free | Spawn at nearest graveyard/shrine; 10% durability lost |
| Respawn at dungeon checkpoint | 20–150g | Spawn inside dungeon near last checkpoint; 10% durability lost |
| Resurrection by Warden | Free (Warden uses ability) | Spawn in place at 50% HP; no durability loss |
| Respawn at Inn | Free | Spawn at last-used Inn; full HP; 10% durability lost |

**CTO note:** Track respawn choice distribution. If >80% of players choose checkpoint respawn at endgame, checkpoint costs may need adjusting. If <5% choose resurrection, Warden utility needs buffing elsewhere.

---

## 7. MMO Considerations

- XP and gold values are server-authoritative — never trust client-side claimed XP
- Anti-farming systems (diminishing returns) must reset correctly between sessions; track per-account per-zone
- Repair costs are sunk at the moment of repair — no refunds
- Durability state must persist across sessions and sync to all clients showing the item

---

## 8. Technical Notes

- XP and gold flows emit to analytics pipeline for real-time economy monitoring
- Durability stored as integer (0–max) per item instance in PostgreSQL
- Item break state (0% durability) requires equipment unequip validation server-side on equip attempt
- Death events should fire a `player_death` analytics event with: zone, level, class, cause, equipped durability levels

---

## 9. Open Questions

| # | Question | Owner |
|---|---|---|
| 1 | Should XP diminishing returns apply to identical quest types (e.g. daily quest spam) in addition to monster kills? | CEO |
| 2 | Should there be a "Repair All" button at vendors, or require item-by-item repair? (UX trade-off) | CEO |
| 3 | Is a 25–35 hour time-to-max acceptable for the target audience, or should we compress to 15–20 hours? | CEO |
| 4 | Should durability loss apply to stored (non-equipped) items on death? Recommend: No. | CEO to confirm |

---

## 10. Version History

| Version | Date | Summary |
|---|---|---|
| 1.0 | 2026-04-15 | Initial Beta progression balancing spec |
