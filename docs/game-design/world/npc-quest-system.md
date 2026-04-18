# NPC & Quest System Design — Project AETHERMOOR
**Document Key:** `npc-quest-spec`
**Issue:** [RPGAA-21](/RPGAA/issues/RPGAA-21)
**Version:** 1.0
**Date:** 2026-04-14
**Author:** Game Designer
**Related:** [RPGAA-14 — Combat Spec](/RPGAA/issues/RPGAA-14#document-combat-spec) | [RPGAA-2 — GDD](/RPGAA/issues/RPGAA-2)

---

## Overview

This document defines the full NPC and Quest system for Project AETHERMOOR. NPCs are the living fabric of the world — merchants, quest-givers, guards, and enemies give Aethermoor its sense of a society with history and stakes. The Quest system drives player motivation, narrative progression, and the daily loop that keeps MMO players returning.

Both systems are built on D&D foundations: NPC alignments, skill checks in quest resolution, and branching outcomes create the mechanical depth D&D players expect within a persistent MMO world.

---

## Design Goals

| Goal | Description |
|---|---|
| Living world | NPCs feel like inhabitants, not bulletin boards |
| Narrative depth | Quests tell stories worth caring about |
| D&D integration | Skill checks and alignment make quests feel mechanical, not just narrative |
| MMO compatibility | Quest and NPC state scales to hundreds of concurrent players |
| Mobile-first | All NPC and quest UI is tap-friendly and readable on small screens |

---

## Part 1: NPC System

### 1.1 NPC Archetypes

Every NPC in AETHERMOOR belongs to one of eight archetypes. Each archetype governs their default behaviour, interaction options, and spawning rules.

| Archetype | Role | Interactable | Hostile | Example |
|---|---|---|---|---|
| **Quest Giver** | Assigns main or side quests | Yes | No | Elder Maren of Thornwick |
| **Merchant** | Buys and sells items | Yes | No | Gregor the Blacksmith |
| **Innkeeper** | Sells Long Rest (inn room) and rumours | Yes | No | Midge of the Copper Flagon |
| **Guard** | Patrols safe zones; attacks PvP-flagged players | Yes (info) | Conditional | Captain Aldric |
| **Trainer** | Teaches class abilities for gold | Yes | No | Swordmaster Rin |
| **Lorekeeper** | Provides world lore and map reveals | Yes | No | Archivist Thorn |
| **Enemy** | Hostile creature or NPC; attacked on sight or on aggro | No (in combat) | Yes | Goblin Raider |
| **Boss** | Named elite enemy with scripted mechanics | No | Yes | The Rot Lord |

### 1.2 D&D Alignment System for NPCs

NPCs carry a D&D alignment along two axes:

| Axis | Values |
|---|---|
| Moral | Good, Neutral, Evil |
| Order | Lawful, Neutral, Chaotic |

Combined alignment grid:

|  | Lawful | Neutral | Chaotic |
|---|---|---|---|
| **Good** | Lawful Good | Neutral Good | Chaotic Good |
| **Neutral** | Lawful Neutral | True Neutral | Chaotic Neutral |
| **Evil** | Lawful Evil | Neutral Evil | Chaotic Evil |

**How alignment affects gameplay:**

- **Quest availability:** Some quests are only offered by aligned NPCs (e.g. a Lawful Good guard won't offer a theft quest; a Chaotic Evil crime lord will).
- **Reaction rolls:** Player CHA checks against NPCs of opposing alignment have disadvantage. Matching or adjacent alignments grant advantage on persuasion.
- **Merchant prices:** Neutral and Good merchants offer base prices; Evil-aligned merchants charge 10% above base but may stock restricted items (poison, forbidden scrolls).
- **Reputation system:** As players earn Reputation in a region, NPC attitudes shift (see Section 1.6).

### 1.3 NPC Dialogue System

#### 1.3.1 Dialogue Architecture

AETHERMOOR uses a **node-based dialogue tree** with conditional branches:

```
[Dialogue Node]
  ├── Speaker text (NPC line)
  ├── Player response options (up to 4)
  │     ├── Option A → Node B
  │     ├── Option B → Node C (requires: Quest "Stolen Relic" active)
  │     ├── Option C → Node D (requires: CHA ≥ 14 or Persuasion check DC 12)
  │     └── Option D → Exit dialogue
  └── Flags: sets/clears quest flags, updates reputation, triggers events
```

#### 1.3.2 Skill Checks in Dialogue

Players can attempt D&D-style skill checks mid-conversation:

| Skill | Ability | Example Use |
|---|---|---|
| Persuasion | CHA | Negotiate a lower price; talk a guard down |
| Intimidation | STR or CHA | Extract information by force of will |
| Deception | CHA | Lie about your identity or purpose |
| Insight | WIS | Detect if an NPC is lying |
| History | INT | Recognise a crest or ancient name |
| Investigation | INT | Notice a hidden item in a shop |

**Roll mechanic:** Same as combat — `d20 + ability modifier ≥ DC`. The dialogue node sets the DC.

- Success → unlocks a dialogue branch or bonus outcome.
- Failure → default branch; some NPCs become hostile or close conversation on a critical failure (natural 1 on Intimidation or Deception).

#### 1.3.3 Dialogue UI

- **Mobile/Tablet:** Full-screen overlay with NPC portrait (top), text (middle), response buttons (bottom, max 4 rows of 72px tap targets).
- **Web/Desktop:** Smaller overlay panel (bottom-right), non-blocking.
- NPC portrait animates between idle, happy, suspicious, and hostile expressions based on dialogue path.
- Text appears word-by-word at configurable speed (tap anywhere to instant-complete).
- Skill check prompts show: skill name, your bonus, the DC if known (some DCs are hidden for tension).

### 1.4 NPC Behaviour States

Each NPC runs a simple state machine server-side:

```
[Idle] ──(player approaches)──▶ [Greeting]
  │                                  │
  │ (combat trigger)                 │ (player interacts)
  ▼                                  ▼
[Combat] ──(health < 20%)──▶ [Flee]   [Dialogue]
  │
  │ (player leaves zone or dies)
  ▼
[Reset] ──▶ [Idle]
```

| State | Behaviour |
|---|---|
| **Idle** | NPC plays ambient animation (sharpening sword, sweeping, reading). Follows a patrol path if defined. |
| **Greeting** | NPC faces player, plays greeting emote. Dialogue prompt appears. |
| **Dialogue** | NPC is locked to conversation. Cannot be attacked during dialogue (PvE zones). |
| **Combat** | Enters combat using stat block. Uses the combat system from [RPGAA-14](/RPGAA/issues/RPGAA-14#document-combat-spec). |
| **Flee** | NPC moves away from player at max speed; calls for guard NPCs if any in range. |
| **Reset** | NPC walks back to spawn point; HP and inventory restore fully after 60 seconds. |

#### 1.4.1 Patrol Paths

Quest-giver and guard NPCs can follow waypoint patrol paths defined in the Zone tilemap data:

- Up to 8 waypoints per NPC.
- Waypoints are tile coordinates stored in zone config.
- NPC moves at 50% of normal speed while patrolling.
- Patrol pauses at each waypoint for 2–5 seconds (randomised idle duration).
- Patrol resumes after dialogue/combat ends and reset completes.

### 1.5 NPC Inventory and Trading System

#### 1.5.1 Merchant Inventory

Merchants have two inventory categories:

| Category | Description |
|---|---|
| **Static stock** | Always-available items defined in NPC data (consumables, common gear) |
| **Rotating stock** | 3–5 items that cycle every 24 hours (real time); seeded by zone and date |

**Pricing:**

| Item Rarity | Base Price (Gold) |
|---|---|
| Common | 5–50 |
| Uncommon | 50–500 |
| Rare | 500–2,000 |
| Very Rare | 2,000–10,000 |
| Legendary | 10,000+ (may require quest completion) |

- **Sell price:** 50% of buy price (standard). Barter skill (CHA Persuasion DC 15) raises sell to 60%.
- **Bulk discount:** Buying 10+ of same consumable grants 10% discount.
- **Reputation discount:** Friendly reputation tier grants 5% off; Honoured grants 10% off; Revered grants 15% off.

#### 1.5.2 Trade UI

- Grid-based shop panel (same visual language as player inventory).
- Left pane: merchant stock. Right pane: player inventory and gold.
- Drag-and-drop on desktop; tap-to-select + confirm button on mobile.
- Gold balance visible at top of panel at all times.
- Insufficient gold highlights item in red; tap shows tooltip "Need X more gold."

### 1.6 NPC Reputation System

Players build Reputation with each major region (town/faction), which shifts NPC attitudes:

| Tier | Points Required | NPC Attitude | Effect |
|---|---|---|---|
| Hostile | < 0 | NPCs attack on sight | Guards aggro immediately |
| Unfriendly | 0–99 | Short dialogue; no quests | Some shops closed |
| Neutral | 100–499 | Standard interaction | Full shop access |
| Friendly | 500–999 | Warm dialogue; bonus quests | 5% shop discount |
| Honoured | 1,000–2,499 | Unlocks elite quests | 10% discount; access to rare stock |
| Revered | 2,500–4,999 | NPC personal dialogue | 15% discount; unique cosmetic rewards |
| Exalted | 5,000+ | Faction story conclusion | 20% discount; title + mount reward |

**Reputation sources:**
- Completing quests for the region: +50 to +500 per quest
- Killing faction enemies: +5 per kill
- Donating gold to faction: +1 per 10 gold donated
- Negative actions (theft, attacking NPCs): −200 per incident

---

## Part 2: Quest System

### 2.1 Quest Types

| Type | Description | Repeat | Party | Example |
|---|---|---|---|---|
| **Main Story** | Narrative arc of AETHERMOOR; sequential chapters | No | Optional | "The Aethermoor Prophecy — Chapter 1" |
| **Side Quest** | Optional story tied to an NPC or location | No | Optional | "The Blacksmith's Lost Hammer" |
| **Daily Quest** | Refreshes every 24 hours; short objectives | Yes (daily) | No | "Collect 10 Stormfern Herbs" |
| **Guild Quest** | Available only to guild members; may require group | Yes (weekly) | Yes | "Defend the Guild Outpost" |
| **World Event** | Community-wide quest; all players contribute | Yes (seasonal) | Yes | "The Blight of Vaelmoss" |
| **Dynamic Quest** | Procedurally generated from templates; fills the world | Yes | Optional | "A Farmer's Plea" (rat-clearing, escort, etc.) |

### 2.2 Quest Structure

Every quest in AETHERMOOR follows this data structure:

```
Quest {
  id: string
  title: string
  type: main | side | daily | guild | world | dynamic
  giver: NPC_id
  prerequisites: Quest_id[] | level_requirement | reputation_requirement
  objectives: Objective[]
  rewards: Reward
  failConditions: FailCondition[]
  branches: Branch[]
  expiresAt: timestamp (daily/event quests only)
  flags: string[] (set on completion; used by other quests as prerequisites)
}

Objective {
  id: string
  type: kill | collect | deliver | escort | explore | talk | skill_check | survive
  target: entity_id | item_id | location_id
  quantity: number
  current: number (per-player, tracked server-side)
  description: string
  optional: boolean
}

Reward {
  xp: number
  gold: number
  items: LootTableEntry[]
  reputation: { regionId: string, amount: number }[]
  title?: string
  unlocks?: Quest_id[]
}
```

### 2.3 Quest Types — Detailed Specification

#### 2.3.1 Main Story Quests

AETHERMOOR's main narrative is structured in **Chapters**, each with 5–8 quests:

**Chapter 1: The Awakening**
1. "A World in Shadow" — Tutorial quest; introduces movement, combat basics
2. "The Seer's Vision" — Visit the Lorekeeper in Thornwick; learn of the Aethermoor Prophecy
3. "Shadows at the Gate" — Defend Thornwick from goblin raid (combat encounter)
4. "Into the Wilds" — Explore the first dungeon (Vaelmoss Ruins)
5. "The Rot Lord Falls" — Boss encounter: defeat the Rot Lord
6. "The Fractured Seal" — Story conclusion; revelation; unlocks Chapter 2 and first major region

Main story quests are **instanced** per player for story integrity — even in an MMO, each player experiences the narrative personally. Group members can join a party member's instance but the quest flag is tracked individually.

#### 2.3.2 Side Quests

Side quests are tied to specific NPCs or locations and tell self-contained stories:

**Example: "The Blacksmith's Lost Hammer" (Thornwick)**
- **Giver:** Gregor the Blacksmith (Merchant NPC, Thornwick)
- **Prerequisite:** Neutral reputation with Thornwick
- **Objectives:**
  1. Talk to Gregor (opens quest)
  2. Investigate the forge (Exploration — Thornwick tilemap)
  3. Skill check: Investigation DC 12 to find the hidden tunnel
  4. Kill 3 Goblin Thieves in the tunnel
  5. Retrieve the hammer (item pickup)
  6. Return hammer to Gregor
- **Branch:** If player fails Investigation check, Gregor provides a clue (Insight DC 10 to notice his nervousness — leads to alternate objective: follow Gregor at night)
- **Reward:** 200 XP, 50 gold, +100 Thornwick reputation, unlocks Gregor's rare stock

#### 2.3.3 Daily Quests

Daily quests reset at **00:00 UTC** each day. Three daily quests are available per major town, drawn from a pool of ~20 templates per town. Players see a random 3 each day.

**Daily Quest Templates (Thornwick examples):**

| Title | Objectives | Reward |
|---|---|---|
| "Forest Clearing" | Kill 8 Giant Rats or Goblin Scouts in Thornwick Forest | 100 XP, 25 gold, +50 rep |
| "Herb Run" | Collect 10 Stormfern Herbs (gatherable nodes in forest) | 80 XP, 30 gold, 1 healing potion |
| "Safe Passage" | Escort Merchant NPC from Thornwick to Millhaven (adjacent zone) | 150 XP, 40 gold, +75 rep |
| "Dungeon Dive" | Complete 1 run of the Vaelmoss Ruins dungeon | 300 XP, 100 gold, +100 rep |
| "Reputation Patrol" | Speak to 3 named NPCs in Thornwick (dialogue check) | 50 XP, 20 gold, +50 rep |

#### 2.3.4 Guild Quests

Available only through the Guild Hall interface (unlocked at Guild rank 1). Refreshes weekly (Monday 00:00 UTC).

Guild quests require **2–5 party members** and are designed around group objectives:

**Example: "Defend the Eastern Outpost"**
- **Type:** Survive
- **Objectives:** Hold a point for 10 waves of enemies (escalating difficulty)
- **Party requirement:** 3–5 players
- **Reward (per player):** 500 XP, 200 gold, Guild Token ×2 (guild currency), +200 guild rep

Guild Tokens are spent at the Guild Hall merchant for exclusive cosmetics, mounts, and housing items.

#### 2.3.5 World Events

World Events are server-wide, limited-time community quests. All players on the server contribute to a shared progress bar.

**Example: "The Blight of Vaelmoss" (monthly event)**
- **Duration:** 7 days
- **Mechanics:** Players kill Blight enemies (special spawns in all zones); each kill contributes 1 Blight Point to the server total
- **Milestones:**
  - 50,000 Blight Points: All players receive bonus XP weekend (+25%)
  - 100,000 Blight Points: Special loot chest available in all towns
  - 250,000 Blight Points: Boss event unlocks — Vaelmoss World Boss spawns
- **Individual rewards:** Based on personal contribution rank (Bronze/Silver/Gold/Platinum tier)
- **World Boss:** Spawns in the Vaelmoss zone centre; requires community effort to defeat (not instanced); drops legendary loot

### 2.4 Quest Objectives — All Types

| Objective Type | Description | Tracked By |
|---|---|---|
| **Kill** | Eliminate N enemies of specified type | Server kill event |
| **Collect** | Pick up N of a specified item (from drops or nodes) | Inventory add event |
| **Deliver** | Carry a quest item to a location or NPC | Player enters zone + has item |
| **Escort** | Keep an NPC alive as they travel a path | NPC health event |
| **Explore** | Enter a specific map zone or tile | Player position event |
| **Talk** | Complete a dialogue with a specific NPC | Dialogue completion flag |
| **Skill Check** | Pass a D&D skill check (any skill) | Roll result event |
| **Survive** | Stay alive for N seconds in a combat scenario | Timer + alive check |
| **Craft** | Craft a specified item | Crafting completion event |
| **Group** | Complete an objective with N party members present | Party membership check at event time |

**Partial progress** is tracked and displayed in the Quest Journal. Server saves progress every 30 seconds and on zone transition.

### 2.5 Quest Branching — Player Choices

AETHERMOOR quests support up to 3 branch points per quest. Branches are triggered by:

1. **Dialogue choices** — player selects a response in NPC dialogue
2. **Skill check results** — pass/fail changes available objectives
3. **Quest flags** — state of previous quests changes NPC behaviour

**Branch rules:**
- Branches must converge at a final objective (all paths lead to completion)
- OR branches can lead to mutually exclusive outcomes (e.g. you can save the prisoner OR take the reward from the kidnapper — not both)
- Branch choices are **permanent** per character on story quests; repeatable on side quests

**Example Branch (Side Quest: "The Merchant's Secret"):**

```
[Start] Merchant asks you to deliver a package

  ├─ Investigate package (Investigation DC 13)
  │   ├─ PASS: Discover it contains stolen goods
  │   │   ├─ Report to Guard Captain → Merchant arrested, +200 guard rep, -100 merchant rep
  │   │   └─ Confront merchant (Intimidation DC 14)
  │   │       ├─ PASS: Merchant pays you double to stay silent
  │   │       └─ FAIL: Merchant attacks you; kill or flee
  │   └─ FAIL: Deliver the package unknowingly → standard reward, no branch
  │
  └─ Deliver without investigating → standard reward; later NPC mentions corruption
```

### 2.6 D&D Skill Checks in Quest Resolution

Skill checks are first-class quest mechanics, not just dialogue flavour:

| Quest Situation | Skill | DC | Success | Failure |
|---|---|---|---|---|
| Finding a hidden passage | Investigation | 12–16 | Shortcut to objective | Must use long route (+2 objectives) |
| Negotiating with a hostile NPC | Persuasion | 13–18 | Skip combat encounter | Must fight |
| Lying to a guard | Deception | 14–17 | Guard lets you pass | Combat triggered |
| Identifying a cursed item | Arcana | 12–15 | Safe identification | Item curses player (Disadvantage on next 3 rolls) |
| Tracking enemy footprints | Survival | 11–14 | Find enemy location revealed | Must explore full area |
| Reading ancient text | History | 13–16 | Unlock lore and bonus reward | Miss bonus only; quest continues |
| Treating a wounded NPC | Medicine | 12–15 | NPC survives; bonus rep | NPC dies; quest fails |

**Critical success (natural 20):** Unlocks a hidden reward — bonus gold, extra lore, or a unique item not available elsewhere.

**Critical failure (natural 1):** Worst possible outcome — NPC turns hostile, objective fails, or a condition is applied to the player.

### 2.7 Quest Tracking and Journal

#### 2.7.1 Quest Journal UI

The Quest Journal is accessible from the main menu and the HUD minimap button.

**Journal structure:**
- **Active Quests** (in-progress, sorted by type: Main Story first)
- **Completed Quests** (searchable history)
- **Failed Quests** (with reason shown)

Each quest entry shows:
- Quest name and giver NPC name
- Objective list with progress bars (e.g. "Goblin Scouts: 4/8")
- Current zone hint ("Find the hidden tunnel — Vaelmoss Ruins")
- Rewards preview (XP, gold, notable items)
- "Track" toggle — tracked quest objectives appear on HUD minimap as yellow markers

#### 2.7.2 HUD Quest Tracker (Mobile)

- Shows 1–3 active tracked quests
- One objective per quest visible at a time (current active objective)
- Swipe left/right to cycle if multiple tracked quests
- Objective text auto-updates on progress events
- Completion triggers a brief full-screen flash and fanfare sound

#### 2.7.3 Objective Markers on Map

| Marker Type | Colour | Meaning |
|---|---|---|
| Quest giver (available) | Yellow `!` | NPC has a quest you can pick up |
| Quest giver (in-progress) | Yellow `?` | Return to this NPC to advance/complete |
| Objective location | Yellow diamond | Go here to advance objective |
| Optional objective | White diamond | Optional — bonus reward |
| Escort NPC | Green arrow | Follow/lead this character |

Markers appear on: the full world map, the zone minimap, and above NPC heads at short range (< 15 tiles).

---

## Part 3: Integration Notes

### 3.1 Integration with Zone/Tile System (Game World Service)

NPCs are entities within zone data, loaded alongside the tilemap:

```json
// Zone config excerpt
{
  "zoneId": "thornwick-town",
  "npcs": [
    {
      "npcId": "gregor-blacksmith",
      "archetype": "merchant",
      "spawnTile": { "x": 24, "y": 18 },
      "patrol": [{ "x": 24, "y": 18 }, { "x": 24, "y": 22 }],
      "alignment": "neutral-good",
      "dialogueTreeId": "gregor-default",
      "inventoryTemplateId": "blacksmith-shop",
      "questIds": ["blacksmiths-lost-hammer"]
    }
  ]
}
```

- NPC positions are authoritative server-side; broadcast to clients in zone delta packets.
- NPC state (idle/combat/dialogue) is part of the zone state model.
- When a player enters dialogue, the NPC is "locked" server-side — other players see the NPC busy but can queue for interaction.
- Respawn timers for enemy NPCs are managed by the Zone Service.

### 3.2 Integration with Combat System ([RPGAA-14](/RPGAA/issues/RPGAA-14#document-combat-spec))

Quest objectives that require combat use the existing Combat Service without modification:

- Kill objectives subscribe to the `entity_killed` event from the Combat Service, filtered by entity type and zone.
- Escort quests use the NPC's combat stat block; if NPC HP reaches 0, the quest enters FailCondition state.
- Skill checks in quests use the same `d20 + modifier ≥ DC` formula as combat saving throws, server-rolled.
- Quest-triggered boss encounters spawn into the Combat Service as standard entities with boss-tier stat blocks.

### 3.3 Quest State and MMO Persistence

All quest state is server-side, per-character:

- **Progress flags** stored in `character_quest_state` table (questId, objectiveId, currentCount, status, branchTaken).
- **Active objectives** broadcast to client on login and on state change events.
- **Daily quest reset** runs as a server cron job at 00:00 UTC; clears daily quest completions and regenerates offerings.
- **World event progress** stored in a shared `world_event_state` table, updated on each qualifying kill/action from any player.

### 3.4 Multi-Player Quest Considerations

| Scenario | Behaviour |
|---|---|
| Two players at same quest-giver | Each player gets their own dialogue session; NPC can handle 1 active dialogue and queue others |
| Kill objectives in a party | Credit shared: all party members in zone get kill credit |
| Collect objectives | Items are personal; each player must pick up their own |
| Escort objectives | Escort NPC is shared — if one party member is on it, group members get credit on arrival |
| Main story (instanced) | Each player in their own instance; party leader can invite others into their instance |
| Daily quest competition | No exclusivity — infinite players can complete the same daily quest |

---

## Open Questions (CEO/CTO Input Needed)

| # | Question | Urgency |
|---|---|---|
| OQ-1 | Should dialogue skill check DCs be visible to the player, or hidden for tension? Recommend: hidden (more D&D-authentic), but this is a UX decision for CEO. | High |
| OQ-2 | Main story quest instancing: should party members share progress flags when inside a shared instance, or remain strictly individual? | High |
| OQ-3 | Dynamic quests: should we implement procedural quest generation in MVP, or launch with only hand-authored quests and add dynamic system post-launch? | Medium |
| OQ-4 | World Event cadence: monthly confirmed in this spec. Does CEO want a seasonal calendar defined now (e.g. Spring Festival, Halloween event equivalents)? | Low |
| OQ-5 | NPC dialogue queuing: if 5 players try to talk to the same NPC simultaneously, should we show a "queue position" indicator, or simply prevent interaction while NPC is busy? | Medium |
| OQ-6 | Reputation system: should negative reputation (Hostile tier) be recoverable, or permanently lock the player out of a town? Recommend: recoverable via a specific "Redemption" quest chain. | Medium |

---

## Version History

| Version | Date | Summary |
|---|---|---|
| 1.0 | 2026-04-14 | Initial complete draft — NPC system, Quest system, integration notes. |

