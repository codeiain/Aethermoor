# AETHERMOOR — Tutorial & Onboarding Flow Design v1.0
## First-Time User Experience (FTUE)

**Author:** Game Designer
**Date:** 2026-04-15
**Status:** Draft v1.0
**Reference:** GDD v0.4 (RPGAA-2), UI Wireframes v1.0 (RPGAA-12), World Map (RPGAA-11)
**Task:** RPGAA-31

---

## Table of Contents

1. Overview
2. Design Goals
3. FTUE Flow — Step by Step
4. Tutorial Quests
5. HUD Tooltip Specifications
6. Tutorial Overlay Annotations
7. Skip & Dismiss Behaviour
8. Death & Respawn Tutorial
9. MMO Considerations
10. Technical Notes for CTO
11. Open Questions
12. Version History

---

## 1. Overview

The Tutorial & Onboarding Flow is the complete first-time player experience from the moment they launch AETHERMOOR for the first time through their first combat victory. It teaches the game's core loop — movement, NPC interaction, inventory, and combat — through guided play rather than static text walls.

The experience is designed around a fictional mentor NPC named **Elder Mira of Ashfen**, who greets new players in a safe "starter" area called **the Ashfen Refuge** — a small village at the edge of the Thornwood Forest. This area is not the main game world; it's a compact, scripted tutorial zone that players graduate from after completing three short quests.

Once completed (or skipped), players are teleported to the main starter zone: **Thornwood Village**, the true game entry point for all players.

---

## 2. Design Goals

| Goal | Description |
|------|-------------|
| **Teach by doing** | Every mechanic is introduced through a quest action, never a lecture screen |
| **Respect veterans** | Experienced players can skip the entire FTUE in under 3 taps/clicks |
| **Mobile-first** | All tutorial UI works on 375px-wide screens with touch controls |
| **Non-blocking** | Tutorial overlays never prevent player interaction; they guide, not gate |
| **Memorable introduction** | Elder Mira gives the world personality from the very first moment |
| **Short session-friendly** | The full FTUE completes in 8–12 minutes; veterans skip to world in 30 seconds |

---

## 3. FTUE Flow — Step by Step

The FTUE is triggered once per character on first world entry. It is **not** shown again after the character leaves Ashfen Refuge.

### 3.1 Flow Overview

```
App Launch
    │
    ▼
[Screen 1] Login / Register
    │
    ▼
[Screen 2] Character Select (empty slots)
    │
    ▼
[Screen 3] Character Creation → Class, Race, Name, Stats
    │
    ▼
[Loading] "Arriving in Ashfen Refuge…"
    │
    ▼
[FTUE Step 1] Welcome Overlay (Skip available)
    │
    ▼
[FTUE Step 2] Movement Tutorial
    │
    ▼
[FTUE Step 3] Talk to Elder Mira → Tutorial Quest 1 accepted
    │
    ▼
[FTUE Step 4] Tutorial Quest 1: Movement + NPC Interaction
    │
    ▼
[FTUE Step 5] Tutorial Quest 2: First Combat Encounter
    │
    ▼
[FTUE Step 6] Tutorial Quest 3: Inventory + Equip Item
    │
    ▼
[FTUE Step 7] Graduation Overlay → "You are ready, adventurer."
    │
    ▼
[Teleport] Thornwood Village — main game begins
```

---

### 3.2 Screen-by-Screen Detail

#### Step 1 — Welcome Overlay (triggered on first world entry)

**Trigger:** Character enters game world for the first time (server flag: `character.ftueComplete = false`).

**Overlay content:**
```
┌──────────────────────────────────────────┐
│  ★  Welcome to AETHERMOOR  ★             │
│                                          │
│  You've arrived in Ashfen Refuge.        │
│  Elder Mira will guide you through       │
│  your first steps as an adventurer.      │
│                                          │
│  [Begin Tutorial]    [Skip Tutorial]     │
└──────────────────────────────────────────┘
```

- **Begin Tutorial** → proceeds to Step 2
- **Skip Tutorial** → shows confirmation: "Skip the tutorial and go straight to the world?" → [Yes, skip] / [No, keep going] → on confirm: grants starter equipment, marks `ftueComplete = true`, teleports to Thornwood Village

**Platform notes:**
- Both buttons are minimum 44×44px touch targets
- Overlay dims the background but does NOT pause server-side movement (other players still visible in tutorial zone for social signal)

---

#### Step 2 — Movement Tutorial

**Trigger:** Player clicks "Begin Tutorial" on welcome overlay.

**Action:** A pulsing arrow appears over the joystick area (mobile) or a keyboard hint appears (desktop: WASD / arrow keys).

**Overlay:**
```
[Mobile]                          [Desktop]
┌──────────────────────────┐      ┌──────────────────────────┐
│  Use the joystick to     │      │  Use WASD or arrow keys  │
│  move your character.    │      │  to move your character. │
│                          │      │                          │
│  [↓ joystick pulsing]   │      │  [WASD key graphic]      │
└──────────────────────────┘      └──────────────────────────┘
```

**Completion trigger:** Player moves 3 tiles in any direction. Overlay dismisses automatically.

**Transition:** A dialogue bubble appears above Elder Mira's sprite: *"Over here, young one!"* with a pulsing waypoint arrow.

---

#### Step 3 — NPC Interaction Hint

**Trigger:** Player is within 5 tiles of Elder Mira.

**Overlay:**
```
[Mobile] Tap Elder Mira to speak with her.  [tap icon]
[Desktop] Press E or click Elder Mira to speak with her.
```

**Completion trigger:** Player opens Elder Mira's dialogue. Overlay dismisses.

---

#### Steps 4–6 — Tutorial Quests

See **Section 4: Tutorial Quests** for full quest design.

---

#### Step 7 — Graduation Overlay

**Trigger:** Tutorial Quest 3 marked complete.

**Full-screen overlay:**
```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│     ✦  You are ready, adventurer.  ✦                    │
│                                                          │
│  Elder Mira smiles as the mist parts. Beyond lies       │
│  Thornwood Village — and beyond that, all of            │
│  AETHERMOOR awaits.                                     │
│                                                          │
│  Your journey begins now.                               │
│                                                          │
│              [Enter the World]                           │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**On confirm:** Server sets `character.ftueComplete = true`, plays a portal animation, teleports player to Thornwood Village spawn point. Grants any unclaimed starter rewards.

---

## 4. Tutorial Quests

### 4.1 Quest 1 — "A Messenger's Errand"

**Design intent:** Teach movement and NPC interaction. No combat. Low cognitive load. Builds world context.

| Field | Detail |
|-------|--------|
| **Quest Name** | A Messenger's Errand |
| **Quest Giver** | Elder Mira (Ashfen Refuge, town square) |
| **Level** | Tutorial — no level requirement |
| **Type** | FTUE, non-repeatable |
| **Estimated time** | 2–3 minutes |

**Objective:**
Deliver Elder Mira's letter to **Innkeeper Brom** in the Ashfen Inn (north end of the village).

**Quest Steps:**
1. Speak to Elder Mira → receive quest + Letter item auto-added to inventory
2. Walk to Ashfen Inn (waypoint arrow shown on minimap)
3. Speak to Innkeeper Brom → dialogue plays → quest complete

**Elder Mira — Quest Accept Dialogue:**
> *"Ah, a new face! Welcome to Ashfen Refuge. I've been expecting someone with your look about them.*
> *Before you venture into the wilds, perhaps you could do an old woman a small favour? My friend Brom at the inn is waiting for this letter. It's just north of here — you can't miss the sign. Speak to him for me, would you?"*
> [Accept] [Decline]

**Innkeeper Brom — Quest Complete Dialogue:**
> *"A letter from Elder Mira? Oh, wonderful! She always did have perfect timing. Here — take this for your trouble. You've got the look of someone who'll need it before long."*

**Reward:**
- 50 XP
- 10 gold
- 1× Adventurer's Satchel (small bag, +4 inventory slots) — auto-equipped

**Tutorial overlays during quest:**
- On quest accept: brief minimap tooltip (see Section 6)
- On Innkeeper Brom approach: interact prompt tutorial (if player hasn't interacted yet)

---

### 4.2 Quest 2 — "The Thornwood Threat"

**Design intent:** Teach combat — attack, defending, ability use. Introduce D&D dice roll feedback. Controlled, safe encounter.

| Field | Detail |
|-------|--------|
| **Quest Name** | The Thornwood Threat |
| **Quest Giver** | Innkeeper Brom (at quest 1 completion) |
| **Level** | Tutorial — no level requirement |
| **Type** | FTUE, non-repeatable |
| **Estimated time** | 3–4 minutes |

**Objective:**
Defeat **3 Thornwood Sprites** that have wandered into the village outskirts.

**Quest Steps:**
1. Speak to Innkeeper Brom → quest accepted
2. Walk to village outskirts (south gate) — 3 Thornwood Sprite enemies are visible
3. Engage first sprite → combat tutorial overlay activates (see below)
4. Defeat all 3 sprites → return to Elder Mira

**Innkeeper Brom — Quest Accept Dialogue:**
> *"Before you head back to Mira, there's a spot of trouble. Little Thornwood Sprites have been darting about near the south gate — harmless alone, but they've been nipping at travellers. Would you deal with them? Elder Mira trained you well enough for that, I'd wager."*

**Thornwood Sprite — Enemy Stats:**

| Stat | Value |
|------|-------|
| HP | 10 |
| AC | 8 (very easy to hit) |
| Attack | +0 to hit, 1d4 damage |
| Behaviour | Passive until approached within 2 tiles, then attacks |
| XP | 15 each |

**Combat Tutorial Overlay (first encounter only):**

Triggered when player engages first sprite. A highlight box appears over the hotbar:

```
┌─────────────────────────────────────────────────────┐
│  ⚔️  Combat!                                         │
│                                                      │
│  Tap an ability on your hotbar to act.              │
│  AETHERMOOR uses D&D-style dice rolls:              │
│  your Attack Roll is shown on screen each turn.     │
│                                                      │
│  Hit the Thornwood Sprite to defeat it!             │
│                               [Got it — dismiss]    │
└─────────────────────────────────────────────────────┘
```

**Dice roll feedback UI (tutorial mode):**
- On every attack: a small floating dice graphic animates above the character (e.g., "d20: 14 + 3 = 17 vs AC 8 — HIT!")
- On damage: floating damage number in red above enemy
- In normal play this is a compact log entry; in tutorial mode it's enlarged for 3 seconds per roll

**Elder Mira — Quest Complete Dialogue:**
> *"You've handled yourself well! Those sprites have been a nuisance all week. You have good instincts — and a little luck with the dice, I suspect. Now, one last lesson before you leave Ashfen…"*

**Reward:**
- 100 XP
- 25 gold
- 1× Rusty Sword (or class-appropriate weapon: Staff for Mage, Shortbow for Ranger, etc.)

---

### 4.3 Quest 3 — "Properly Equipped"

**Design intent:** Teach inventory management, equipping items, and stat changes. Reinforce the character sheet.

| Field | Detail |
|-------|--------|
| **Quest Name** | Properly Equipped |
| **Quest Giver** | Elder Mira (returned to after Quest 2) |
| **Level** | Tutorial — no level requirement |
| **Type** | FTUE, non-repeatable |
| **Estimated time** | 2–3 minutes |

**Objective:**
Equip the weapon received in Quest 2 and open the Character Sheet to confirm your stats.

**Quest Steps:**
1. Accept quest from Elder Mira
2. Open Inventory (hotbar inventory button or I key)
3. Equip the weapon item → tutorial overlay highlights drag-to-slot or tap-to-equip action
4. Open Character Sheet (hotbar or C key) → tutorial overlay highlights STR/DEX and the equipped weapon slot
5. Close Character Sheet → quest complete, graduation overlay begins

**Elder Mira — Quest Accept Dialogue:**
> *"A weapon means nothing on your belt, adventurer. Let me show you how to make it truly yours. Open your pack — that bag on your belt — and put that blade where it belongs."*

**Inventory Tutorial Overlay (mobile):**
```
┌───────────────────────────────────────────────────────┐
│  🎒 Inventory                                          │
│                                                        │
│  Tap the [weapon icon] then tap [Weapon Slot] above   │
│  your character portrait to equip it.                 │
│                              [Got it — dismiss]       │
└───────────────────────────────────────────────────────┘
```

**Inventory Tutorial Overlay (desktop):**
```
┌───────────────────────────────────────────────────────┐
│  🎒 Inventory                                          │
│                                                        │
│  Drag [weapon icon] to the Weapon Slot on the left    │
│  side of the inventory panel, or right-click → Equip. │
│                              [Got it — dismiss]       │
└───────────────────────────────────────────────────────┘
```

**Character Sheet Tutorial Overlay:**
```
┌───────────────────────────────────────────────────────┐
│  📋 Character Sheet                                    │
│                                                        │
│  This shows all your stats, class, level, and gear.  │
│                                                        │
│  STR: affects melee damage and carrying capacity      │
│  DEX: affects ranged attacks and armour class         │
│  INT: affects spell power (Mage class)               │
│  WIS: affects healing and perception                  │
│  CON: affects max HP                                  │
│  CHA: affects NPC reactions and social skills         │
│                                                        │
│  Your equipped weapon now shows in the gear panel.   │
│                              [Got it — dismiss]       │
└───────────────────────────────────────────────────────┘
```

**Reward:**
- 150 XP (triggers Level 2)
- 50 gold
- 1× Ashfen Traveller's Cloak (Light Armour, +1 AC) — auto-added to inventory

**Elder Mira — Quest Complete Dialogue (plays before Graduation Overlay):**
> *"Look at you. Not the lost soul who stumbled in here an hour ago. You're an adventurer now. AETHERMOOR is vast and full of danger — and wonder. I believe you're ready. Go. And… do try to stay alive out there."*

---

## 5. HUD Tooltip Specifications

These tooltips appear as persistent overlays during FTUE steps, dismissed per-element as each is introduced. After FTUE, all tooltips are accessible via a "?" toggle button in the HUD for returning players who need a reminder.

### 5.1 Tooltip System Rules

- Each tooltip appears **once per character** during FTUE, sequenced to match the quest flow
- Tooltip dismissal is per-element and stored server-side in `character.tutorialFlags`
- Players can re-enable all tooltips from Settings → Tutorial → Reset Tutorial Tips
- Tooltips do **not** appear during combat (focus mode) except for the first combat encounter overlay
- Tooltip max width: 280px (mobile), 320px (desktop)
- Tooltip arrow points to the relevant HUD element

### 5.2 HUD Element Tooltips

| HUD Element | Tooltip Text | Trigger Moment |
|---|---|---|
| **HP Bar** (red) | "Health Points — if this reaches zero, you die and respawn at the nearest waystone." | First world entry |
| **MP Bar** (blue) | "Mana — spent when you use abilities and spells. It regenerates over time when you're out of combat." | First world entry |
| **Avatar Portrait** | "Your character. Tap to open your Character Sheet." | First world entry |
| **Minimap** | "Minimap — shows your surroundings. Quest markers (yellow !) and enemies (red dots) appear here. Tap to open the full map." | Quest 1 accept |
| **Quest Tracker (top-right)** | "Active quest objectives. Tap a quest to highlight the target on your map." | Quest 1 accept |
| **Hotbar Slot 1** | "Your basic attack. Tap to use in combat, or drag abilities here from your spellbook." | First combat encounter |
| **Hotbar Slot 2–4** | "Ability slots. Open your Spellbook (⚗ icon) to assign abilities." | First combat encounter |
| **Inventory Button** | "Your bag. Tap to open inventory and manage your items." | Quest 3 trigger |
| **Menu Button (≡)** | "Menu. Access your Character Sheet, Quest Journal, Map, Social Panel, Settings, and more." | Quest 3 complete |
| **Zone Name (top-left)** | "Current zone and level range. Head to higher-level zones as you grow stronger." | Graduation overlay |
| **Chat Bar (bottom)** | "Chat with nearby players, your party, or your guild. AETHERMOOR is a living world — say hello!" | Graduation overlay |

### 5.3 Mobile-Only Tooltip

| HUD Element | Tooltip Text | Trigger Moment |
|---|---|---|
| **Virtual Joystick** | "Move your character by dragging the joystick. The joystick appears wherever you press and hold on the left side of the screen." | Step 2 (movement) |
| **Interact Button (right side)** | "Tap the ✦ button to interact with NPCs, pick up items, and open doors when you're near them." | Step 3 (NPC interaction) |

---

## 6. Tutorial Overlay Annotations (HUD Wireframe)

The following annotates the HUD wireframe from RPGAA-12 with tutorial overlay positions and z-index layers.

```
┌─────────────────────────────────────────────────────┐
│ [A] Zone Name ←──── TIP-07: Zone tooltip             │  ← TOP BAR
│ (Ashfen Refuge, Lv. 1–3)          [B] Quest Tracker ←── TIP-05: Quest tracker tooltip │
├──────────────────────────────────────────────────────┤
│                                                      │
│                                                      │
│                  PHASER CANVAS                       │
│                                                      │
│  ┌────────────────────────────────────┐              │
│  │  WELCOME OVERLAY (Step 1)          │              │  ← z-index: 900
│  │  or QUEST TUTORIAL OVERLAY         │              │
│  └────────────────────────────────────┘              │
│                                                      │
│  [F] Joystick ←── TIP-M01: Mobile joystick tooltip  │
│                                                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│ [C] HP/MP + Avatar                                   │
│  ├── TIP-01: HP bar tooltip                          │  ← BOTTOM BAR
│  ├── TIP-02: MP bar tooltip                          │
│  └── TIP-03: Avatar/character sheet tooltip         │
│                                                      │
│          [D] Hotbar                                  │
│           ├── TIP-06: Slot 1 combat tooltip          │
│           └── TIP-09: Inventory button tooltip       │
│                                                      │
│                             [E] Minimap              │
│                              └── TIP-04: Minimap     │
└──────────────────────────────────────────────────────┘
```

### 6.1 Overlay Z-Index Layers

| Layer | Z-Index | Content |
|-------|---------|---------|
| Phaser canvas | 0 | Game world |
| React HUD base | 100 | HP/MP bars, hotbar, minimap |
| HUD tooltips | 200 | Individual element tooltips |
| Tutorial panel overlays | 500 | "Combat!" banner, quest intro panels |
| Modal overlays (welcome, graduation) | 900 | Full-screen overlays |
| Loading screen | 1000 | Transition loading screens |

---

## 7. Skip & Dismiss Behaviour

### 7.1 Skipping the Full Tutorial

| Action | Behaviour |
|--------|-----------|
| "Skip Tutorial" on Welcome Overlay | Confirmation modal → on confirm: grants starter kit, teleports to Thornwood Village, sets `ftueComplete = true` |
| Character created but never launched | Tutorial triggers fresh on first world entry |
| Tutorial already complete | Never re-triggered, even on death or re-login |

**Starter kit granted on skip:**
- Adventurer's Satchel (+4 bag slots)
- Class-appropriate starting weapon (same items as quest rewards)
- Ashfen Traveller's Cloak (+1 AC)
- 85 gold (equivalent to completing all 3 quests)
- 300 XP (enough to reach Level 2 like tutorial completers)

**Design intent:** Skipping should not disadvantage players. Veterans should reach Thornwood Village at parity with tutorial completers.

### 7.2 Dismissing Individual Tooltips

| Trigger | Behaviour |
|---------|-----------|
| Tap/click [×] or "Got it" on tooltip | Dismisses that specific tooltip; never shown again on this character |
| Tap/click outside tooltip | Does NOT dismiss (accidental touch avoidance) |
| Tutorial flag reset (Settings) | All tooltip flags cleared; tooltips re-appear from start |
| Completing FTUE | Remaining unseen tooltips dismissed and flagged as seen |

### 7.3 Overlay Dismiss Rules

| Overlay Type | Dismiss Method |
|---|---|
| Welcome overlay | Button tap only ("Begin" or "Skip") |
| Step overlays (movement hint, etc.) | Auto-dismiss on action completion OR "Got it" button |
| Combat tutorial banner | "Got it" button |
| Quest complete panel | Button tap or 5-second auto-dismiss |
| Graduation overlay | Button tap only |

---

## 8. Death & Respawn Tutorial

**Context:** Players cannot die during Tutorial Quests 1 and 2 — the Thornwood Sprites are tuned so low that death is nearly impossible. However, if a player somehow reaches 0 HP (Edge case: they stand still during all three sprite attacks), the Death Screen appears.

**First Death Overlay (FTUE-specific):**
```
┌───────────────────────────────────────────────────┐
│  💀  You have fallen.                             │
│                                                   │
│  In AETHERMOOR, death is not the end.            │
│  You will respawn at the nearest Waystone        │
│  with a brief debuff.                            │
│                                                   │
│  Resurrection Sickness: -10% to all stats        │
│  for 2 minutes. It fades — press on.            │
│                                                   │
│              [Rise Again]                         │
└───────────────────────────────────────────────────┘
```

**Respawn behaviour (tutorial zone):**
- Player respawns at Ashfen Refuge waystone (single waystone in tutorial zone)
- Resurrection Sickness applied (standard, 2 min, -10% all stats)
- Tutorial quest progress is NOT reset — defeated sprites remain defeated
- Elder Mira adds a sympathetic dialogue line if player speaks to her: *"Ah. You've tasted defeat. Good. Every adventurer must. Now get up."*

**Respawn tutorial flags:** Set `character.tutorialFlags.deathSeen = true`. If this is the player's first death (in or out of tutorial), the Death Screen overlay shows the extended explanation. Subsequent deaths show the standard Death Screen.

---

## 9. MMO Considerations

| Concern | Design Solution |
|---------|----------------|
| **Tutorial zone congestion** | Ashfen Refuge is a shared zone (not instanced) — seeing other new players is a feature, not a bug. It signals a living world. Cap the zone at 50 concurrent players; overflow goes to a duplicate shard with identical layout |
| **Tutorial spawn griefing** | Ashfen Refuge is a PvP-disabled zone. All players have `pvpEnabled = false` while `ftueComplete = false` |
| **Tutorial NPC contention** | Elder Mira and Innkeeper Brom are "multi-talker" NPCs — many players can interact simultaneously; dialogue runs per-player client-side |
| **Tutorial sprite kill-stealing** | Sprites are tagged to the player who first attacked them; tagged sprites can only be killed (for quest credit) by that player. Other players can still attack for XP |
| **New player visibility** | New players show a ★ icon above their name in tutorial zone to signal they're learning |
| **High new player traffic** | Tutorial zone is lightweight (small map, few assets). Shard creation cost is low. Auto-shard on threshold |
| **Skipped tutorial players in world** | Players who skip arrive at Thornwood Village at Level 2 — same as completers. No balancing gap |

---

## 10. Technical Notes for CTO

| Area | Note |
|------|------|
| **FTUE flag** | `character.ftueComplete: boolean` and `character.tutorialFlags: object` on character record. Server-authoritative — client cannot self-report completion |
| **Tutorial zone** | Ashfen Refuge is a standard game zone with a `isTutorialZone: true` flag. PvP disabled zone-wide for this flag. Sprite spawns are scripted, not procedural |
| **Tutorial quest engine** | Quests 1–3 use the standard quest system with an additional `isTutorialQuest: true` flag. Tutorial quests are excluded from quest log archive when complete |
| **Overlay system** | Tutorial overlays are React components rendered in the HUD layer (z-index 200–900). They read from a `tutorialFlags` state store synced from server |
| **Tooltip triggers** | Each tooltip has a trigger condition checked client-side (proximity, inventory opened, etc.). Dismissal is posted to server: `PATCH /characters/:id/tutorial-flags` |
| **Sprite tagging** | When a player attacks a tutorial sprite, the server tags it: `sprite.taggedPlayerId`. Kill credit checks the tag before awarding quest progress |
| **Graduation teleport** | On `ftueComplete` set to `true`, server sends a `TELEPORT` event to client with destination: Thornwood Village spawn point. Client plays portal animation then loads new zone |
| **Skip reward grant** | On skip confirm, server runs the same reward grants as quest completions. No client-side reward logic |
| **Multi-shard tutorial zones** | Zone manager tracks player count per Ashfen Refuge shard. On threshold (50 players), spins up a new shard using the same zone template |

---

## 11. Open Questions

| # | Question | Owner | Priority |
|---|----------|-------|----------|
| 1 | Should Ashfen Refuge be partially instanced (each player sees only their own Sprites but shared NPC/environment) or fully shared? Shared is more social but needs tagging; instanced is simpler. **Current design:** fully shared with tagging. | CEO decision | Medium |
| 2 | Should skipping the tutorial still play a brief cinematic intro (15 seconds, lore-setting) before teleporting? Or straight to Thornwood Village? | CEO decision | Low |
| 3 | What is the art style for tutorial overlay panels? Should they use an in-world "enchanted parchment" aesthetic or a clean modern UI panel? Impacts mobile readability. | CEO decision | Medium |
| 4 | Should Elder Mira appear again later in the main world (as a recurring NPC) or remain exclusive to the tutorial zone? Strong narrative case for both. | Game Designer (resolve next heartbeat) | Low |
| 5 | CTO: Is a `PATCH /characters/:id/tutorial-flags` endpoint feasible as a lightweight per-element server call, or should flags be batched and sent on session end? | CTO | High |
| 6 | CTO: Can the tutorial zone auto-shard at 50 players, or is there a fixed shard architecture constraint from the current prototype? | CTO | High |

---

## 12. Version History

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 1.0 | 2026-04-15 | Game Designer | Initial draft — full FTUE flow, 3 tutorial quests, HUD tooltips, overlay annotations, skip/dismiss system, death/respawn tutorial, MMO considerations |
