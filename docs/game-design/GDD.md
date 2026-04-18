# AETHERMOOR — Game Design Document v0.6
## Core Systems

**Author:** Game Designer
**Date:** 2026-04-16
**Status:** Draft — v0.6 (updates Crafting System with CEO design decisions: BOE, visible exceptional chance, GM quality guarantee)

**Subsystem Design Documents:**
| Document | Location |
|---|---|
| Combat System | `game-design/combat/combat-system.md` |
| Overworld Map | `game-design/world/overworld-map.md` |
| NPC & Quest System | `game-design/world/npc-quest-system.md` |
| UI Wireframes | `game-design/ui/wireframes.md` |
| UI Style Guide | `game-design/ui/style-guide.md` |
| Visual Style Guide | `game-design/art-direction/visual-style-guide.md` |
| Combat Spec | `game-design/combat/combat-system.md` |
| Alpha Content | `game-design/alpha-content/` |
| Beta Content | `game-design/beta-content/` |
| Tutorial Design | `game-design/tutorial/tutorial-onboarding-flow.md` |
| Crafting System | `game-design/crafting/crafting-system.md` |

---

## Table of Contents

1. Executive Summary
2. Vision & Pillars
3. Core Gameplay Loop
4. World Design
5. Character Classes & Ability Trees
6. Combat System
7. Progression & Advancement
8. Crafting System
9. Housing System
10. MMO Social Systems
11. PvP Factions
12. Seasonal Content
13. Dungeon Bestiary
14. UI/UX — Mobile, Tablet, Web
15. Technical Requirements for CTO
16. Fishing Mechanic
17. NPC Dialogue Trees (Sample)
18. Quest Scripts (Sample)
19. Economy Balancing Model
20. Open Questions

---

## 1. Executive Summary

AETHERMOOR is a 2D top-down pixel-art MMO RPG inspired by The Legend of Zelda's sense of exploration and mystery, powered under the hood by D&D 5e-adjacent mechanics. Players explore a vast, hand-crafted world of overworld zones, dungeons, towns, and hidden secrets — while sharing the world with hundreds of concurrent players.

The game is built on **Phaser.js** (confirmed by CEO) — TypeScript-native, WebGL/Canvas rendering, single codebase for mobile, tablet, and web.

**Genre:** 2D MMO Action-RPG
**Perspective:** Top-down, pixel art
**Art Style:** 16×16 or 32×32 tile-based pixel art (SNES/GBA era aesthetic)
**Rendering Engine:** Phaser.js (confirmed)
**Target Platforms:** Mobile (iOS/Android via WebView), Tablet, Web (desktop browser)
**Target CCU:** 500–2,000 concurrent players per server shard
**Session Length:** 10–30 minutes (mobile-friendly), up to multi-hour for desktop/tablet

---

## 2. Vision & Pillars

### Vision Statement
*"A living pixel world where every dungeon hides a secret, every stranger could become a party member, and every die roll matters."*

### Design Pillars

| Pillar | Description |
|--------|-------------|
| **Explore Everything** | Zelda-style overworld with secrets, environmental puzzles, hidden paths, and emergent discovery |
| **Roll with Consequence** | D&D dice mechanics create unpredictability and narrative tension in every fight |
| **Better Together** | MMO social systems that reward cooperation without requiring it |
| **Fit in Your Pocket** | Designed touch-first; every feature works on a phone screen |
| **A World That Breathes** | Shared world events, day/night cycles, weather, NPC routines |
| **Your Place in the World** | Housing gives players a persistent, personal stake in Aethermoor |

---

## 3. Core Gameplay Loop

### Primary Loop (Per Session — 10–30 min)

```
Spawn at Home / Inn → Accept Quest / Discover Zone → Explore Overworld
   → Enter Dungeon / Combat Encounter → Loot + XP
   → Return Home → Level Up / Upgrade Gear / Craft / Decorate → Repeat
```

### Secondary Loop (Per Week)

```
Guild Check-in → World Event Participation → Boss Raid
   → Dungeon Completion Reward → Character Build Refinement → Faction Standing
   → Housing: new furnishing placed or upgrade completed
```

### Macro Loop (Months)

```
Unlock New World Region → New Class Abilities → Seasonal Story Arc
   → Seasonal Crafting Recipes → Housing Seasonal Decor → Prestige System → Legacy Cosmetics
```

---

## 4. World Design

### 4.1 World Structure

The world is divided into **Regions** composed of **Zones**. Each zone is a single scrolling screen (or multiple connected screens) in the Zelda room-based tradition.

```
AETHERMOOR WORLD MAP
────────────────────────────────────────
 [Frostpeak Mountains]  [Sky Archipelago]
       │                       │
 [Crystal Caves]       [Aether Wastes]
       │                       │
 [Thornwood Forest] ── [CITY OF AETHERMOOR] ── [Sunken Harbor]
       │                       │
 [Goblin Wastelands]   [Temple of the Deep]
       │                       │
 [Ember Plains]        [Verdant Jungle]
────────────────────────────────────────
        [HOUSING DISTRICTS — instanced personal zones]
```

**Total planned regions at launch:** 6
**Zones per region:** 8–12 (overworld) + 2–3 dungeons
**Total dungeon count (launch):** 15–18

### 4.2 Zone Types

| Type | Description | Player Density |
|------|-------------|---------------|
| **Town** | Hub zone, no combat, NPC shops, quest board, bank | High (shared, persistent) |
| **Overworld** | Exploration zone, roaming enemies, secrets, resources | Medium (instance-capped at 50 players) |
| **Dungeon** | 5–10 room structured crawl, boss at end | Party (1–4 players, private instance) |
| **Raid Zone** | 8–16 player coordinated encounter | Guild/party invite |
| **PvP Zone** | Flagged combat area with resource rewards | Free-for-all or faction |
| **World Event** | Temporary zone-wide encounter, open to all | Up to 100 players |
| **Faction Territory** | Contested zone with resource control points | Faction-flagged players only |
| **Housing Plot** | Player's personal instanced space | Owner + visitors (up to 8) |

### 4.3 Zelda-Style Exploration Mechanics

- **Environmental Puzzles:** Push blocks, trigger pressure plates, light torches in sequence
- **Secrets:** Shatter Rune (bombable wall replacement), bush cutting, hidden floor tiles
- **Locked Doors:** Small Key / Dungeon Key system, one key per locked door per dungeon
- **Compass & Map Items:** Found in dungeons, reveal layout and chests (shared across party)
- **Boss Keys:** Mini-boss gate before final boss room
- **Overworld Gating:** Requires tools (Aetherhook Gadget for hookshot puzzles, Tide Rune to swim)
- **Shrines:** Mini-puzzles → reward Aether Fragments (upgrade currency)

### 4.4 Towns

Each town has: Inn/Respawn, General Store, Blacksmith, Crafting Workshop, Guild Hall, Notice Board, Bank, Market Stall, Lore Keeper NPC, Faction Envoy NPC, and a **Housing Registrar** (deed purchase and plot management).

### 4.5 Dungeons

See **Section 13 — Dungeon Bestiary** for full dungeon-by-dungeon design including rooms, mechanics, and boss details.

---

## 5. Character Classes & Ability Trees *(EXPANDED in v0.3)*

### 5.1 Class Overview

| Class | D&D Archetype | Role | Hit Die | Primary Stats |
|-------|--------------|------|---------|---------------|
| **Knight** | Fighter | Melee DPS / Tank | d10 | STR, CON |
| **Archmage** | Wizard | Ranged Magic DPS | d6 | INT, WIS |
| **Shadowblade** | Rogue | Burst DPS / Utility | d8 | DEX, INT |
| **Warden** | Cleric | Healer / Support | d8 | WIS, CHA |
| **Ranger** | Ranger | Ranged Physical DPS | d8 | DEX, WIS |
| **Bard** | Bard | Buff / Debuff / Support | d8 | CHA, DEX |

### 5.2 Ability Scores & Modifiers

| Score | Governs | Modifier Formula |
|-------|---------|------------------|
| STR | Melee damage, carry weight | (score - 10) / 2, floor |
| DEX | Ranged, dodge, initiative | same |
| CON | HP, stamina, death saves | same |
| INT | Spell damage, loot ID | same |
| WIS | Healing, perception, saves | same |
| CHA | NPC disposition, bard spells | same |

Scores: 8–20. Players assign **2 points per level** after Level 1 (base preset by class).

---

### 5.3 KNIGHT — Full Ability Tree

**Subclasses at Level 10:** Guardian (tank) or Berserker (DPS)

#### Core Abilities (All Knights)

| Level | Ability | Type | Description |
|-------|---------|------|-------------|
| 1 | **Sword & Shield** | Passive | +2 AC while shield equipped |
| 1 | **Power Strike** | Action | 2d8+STR melee; target makes STR save DC 12 or pushed 2 tiles |
| 2 | **Second Wind** | Bonus Action | Heal 1d10+level HP. Cooldown: 60 seconds |
| 3 | **Action Surge** | Passive (1/rest) | Take one additional Action this turn |
| 4 | **Shield Bash** | Action | 1d6+STR; Stun target 1 round (CON save DC 13) |
| 5 | **Extra Attack** | Passive | Attack twice with Action |
| 6 | **Indomitable** | Reaction | Reroll one failed saving throw (1/long rest) |
| 7 | **Battle Cry** | Bonus Action | Party within 10 tiles gain advantage on attacks for 2 rounds |
| 8 | **Cleave** | Action | AoE swing; hit all enemies within 1-tile radius; 1d10+STR each |
| 9 | **Resilient** | Passive | +CON modifier to all saving throws |

#### Guardian Subclass (Levels 10–20)

| Level | Ability | Description |
|-------|---------|-------------|
| 10 | **Defensive Stance** | Halve incoming damage for 3 rounds; cannot attack. Cooldown: 90s |
| 12 | **Guardian Aura** | Party members within 8 tiles take 5 less damage per hit |
| 14 | **Taunt** | Force all enemies within 6 tiles to target you for 5 rounds |
| 16 | **Unbreakable** | Once per long rest: when HP would hit 0, set to 1 instead |
| 18 | **Fortress** | Immune to Stun, Knockback, Fear while shield equipped |
| 20 | **Juggernaut** | +5 AC; +10% max HP; Shield Bash cooldown removed |

#### Berserker Subclass (Levels 10–20)

| Level | Ability | Description |
|-------|---------|-------------|
| 10 | **Rage** | +4 STR, +50% damage, -2 AC for 20 seconds. Cooldown: 120s |
| 12 | **Reckless Attack** | Advantage on all attacks; enemies have advantage on you |
| 14 | **Frenzy** | During Rage: bonus attack with Bonus Action each round |
| 16 | **Intimidating Presence** | Charm nearby enemies (WIS save DC 15); lasts 10 seconds |
| 18 | **Relentless Rage** | Rage cannot be interrupted by Stun/Freeze during last 5 seconds |
| 20 | **Warlord** | Rage grants +6 STR; Cleave now ignores AC (auto-hit) |

---

### 5.4 ARCHMAGE — Full Ability Tree

**Subclasses at Level 10:** Elementalist or Illusionist

#### Core Abilities (All Archmages)

| Level | Ability | Type | Description |
|-------|---------|------|-------------|
| 1 | **Arcane Focus** | Passive | +1 to all spell attack rolls |
| 1 | **Fire Bolt** | Cantrip | 1d10+INT fire; unlimited uses |
| 2 | **Mage Armor** | Action | AC = 13+DEX (no armor needed). Duration: 8 hours |
| 3 | **Fireball** | Level 1 Spell Slot | 8d6 fire in 4-tile radius; DEX save DC 14 for half |
| 4 | **Arcane Missile** | Cantrip (upgrade) | Three darts, 1d4+INT each; auto-hit |
| 5 | **Counterspell** | Reaction | Negate enemy spell if within 12 tiles (INT contest if Level 2+) |
| 6 | **Haste** | Level 2 Spell Slot | Target gains double speed and one extra action for 60 seconds |
| 7 | **Arcane Eye** | Utility | Project invisible sensor through dungeon rooms; 30-tile range |
| 8 | **Disintegrate** | Level 3 Spell Slot | 10d6+40 force; CON save DC 15 or disintegrated (instant death at <50HP) |
| 9 | **Spell Mastery** | Passive | One Level 1 Spell Slot spell cast at will (player choice) |

#### Elementalist Subclass (Levels 10–20)

| Level | Ability | Description |
|-------|---------|-------------|
| 10 | **Elemental Affinity** | Choose Fire/Ice/Lightning. +2d6 damage of that type on all spells |
| 12 | **Empowered Evocation** | Add INT modifier to all evocation damage rolls |
| 14 | **Sculpt Spells** | Choose up to 4 creatures to be immune to your AoE spell damage |
| 16 | **Overchannel** | Cast Level 1–3 spell at max possible damage (no roll). 1/long rest; deal 2d12 to self |
| 18 | **Storm Surge** | Every crit triggers a free Arcane Missile (no slot) |
| 20 | **Arcane Supremacy** | All spells deal +50% damage; Fireball radius increases to 6 tiles |

#### Illusionist Subclass (Levels 10–20)

| Level | Ability | Description |
|-------|---------|-------------|
| 10 | **Improved Minor Illusion** | Create illusions with sound + image; enemies investigate before attacking |
| 12 | **Malleable Illusions** | Alter existing illusions as bonus action |
| 14 | **Illusory Self** | Once per short rest: negate one attack by creating decoy image |
| 16 | **Phantom Army** | Summon 6 illusory knights; enemies split attacks among them for 30 seconds |
| 18 | **Mind Splinter** | Target hallucinates for 10 seconds; attacks random entities (WIS save DC 17) |
| 20 | **Reality Unraveled** | 60-second zone: all enemies in 8-tile radius have Disadvantage on everything |

---

### 5.5 SHADOWBLADE — Full Ability Tree

**Subclasses at Level 10:** Assassin or Trickster

#### Core Abilities (All Shadowblades)

| Level | Ability | Type | Description |
|-------|---------|------|-------------|
| 1 | **Sneak Attack** | Passive | +1d6 damage when attacking with advantage or flanking (+1d6 per 2 levels) |
| 1 | **Thieves' Tools** | Passive | Proficiency in lockpicking (DEX check), trap disarming, pickpocket |
| 2 | **Cunning Action** | Bonus Action | Dash, Disengage, or Hide each round |
| 3 | **Shadow Step** | Action | Teleport to any shadow/dark tile within 8 tiles |
| 4 | **Uncanny Dodge** | Reaction | Halve damage from one attack per round |
| 5 | **Evasion** | Passive | On DEX save: success = no damage, fail = half damage |
| 6 | **Reliable Talent** | Passive | Any skill check with proficiency treated as minimum roll of 10 |
| 7 | **Smoke Bomb** | Action | 5-tile cloud, blocks line of sight for 10 seconds. Hides Shadowblade |
| 8 | **Death Strike** | Passive | First attack from hidden state: triple Sneak Attack dice |
| 9 | **Slippery Mind** | Passive | Proficiency bonus to WIS saving throws |

#### Assassin Subclass (Levels 10–20)

| Level | Ability | Description |
|-------|---------|-------------|
| 10 | **Assassinate** | Auto-crit when attacking surprised target; +2d8 bonus poison damage |
| 12 | **Infiltration Mastery** | Maintain hidden status through zone transitions |
| 14 | **Execution** | Below 25% HP target: instant kill attempt (CON save DC 16; fail = 0HP) |
| 16 | **Toxic Strikes** | All attacks apply 1d6 poison per second for 5 seconds |
| 18 | **Shadow Cloak** | Become invisible for 30 seconds (broken by attack). Cooldown: 120s |
| 20 | **One in the Dark** | Shadow Step cooldown removed; always considered hidden when attacking |

#### Trickster Subclass (Levels 10–20)

| Level | Ability | Description |
|-------|---------|-------------|
| 10 | **Misdirection** | Redirect one enemy attack to another enemy within 3 tiles |
| 12 | **Duplicity** | Create a perfect decoy; lasts 30 seconds or until hit |
| 14 | **Master of Tricks** | Use two Cunning Actions per round |
| 16 | **Bamboozle** | Confuse target for 15 seconds; they attack nearest entity (any) |
| 18 | **Vanishing Act** | Vanish instantly; no cooldown; cannot be targeted for 5 seconds |
| 20 | **Phantom Thief** | Steal one positive buff from target per round; apply to self |

---

### 5.6 WARDEN — Full Ability Tree

**Subclasses at Level 10:** Lightbringer (healer) or Templar (melee-healer)

#### Core Abilities (All Wardens)

| Level | Ability | Type | Description |
|-------|---------|------|-------------|
| 1 | **Sacred Flame** | Cantrip | 1d8+WIS radiant; ranged, unlimited |
| 1 | **Healing Word** | Bonus Action (Spell Slot) | Heal target 1d4+WIS. Range: 12 tiles |
| 2 | **Divine Shield** | Reaction | Negate one hit on ally within 8 tiles (1/short rest) |
| 3 | **Turn Undead** | Action | Undead within 6 tiles: WIS save DC 13 or flee for 10 seconds |
| 4 | **Spiritual Weapon** | Level 1 Spell Slot | Floating spectral weapon attacks once per round (1d8+WIS) for 60s |
| 5 | **Improved Healing Word** | Upgrade | Healing Word now heals 2d4+WIS; range 20 tiles |
| 6 | **Aura of Protection** | Passive | Allies within 6 tiles gain +WIS modifier to saving throws |
| 7 | **Mass Cure** | Level 2 Spell Slot | Heal all party members for 3d8+WIS |
| 8 | **Banishment** | Level 2 Spell Slot | Send enemy to void for 60 seconds (CHA save DC 15); auto-returns if not killed |
| 9 | **Holy Strike** | Action | 4d8+WIS radiant + target Blinded for 2 rounds |

#### Lightbringer Subclass (Levels 10–20)

| Level | Ability | Description |
|-------|---------|-------------|
| 10 | **Greater Restoration** | Remove all conditions from one ally (1/short rest) |
| 12 | **Healing Beacon** | Place a beacon; allies within 6 tiles heal 1d6+WIS per 5 seconds for 30s |
| 14 | **Resurrection** | Revive downed ally with 50% HP (1/long rest; no death penalty applied) |
| 16 | **Radiant Aura** | All allies within 8 tiles gain +15% max HP for 60 seconds |
| 18 | **Holy Sanctuary** | 10-tile zone: enemies take 2d6 radiant per second while inside for 20s |
| 20 | **Miracle** | Full heal all party members + cleanse all conditions. Cooldown: 10 min |

#### Templar Subclass (Levels 10–20)

| Level | Ability | Description |
|-------|---------|-------------|
| 10 | **Sacred Smite** | Melee attacks deal +2d8 radiant bonus damage |
| 12 | **Aura of Courage** | Allies within 6 tiles immune to Fear and Charm |
| 14 | **War Prayer** | Party gains +3 to attack rolls for 20 seconds |
| 16 | **Crusader's Strike** | Hit: target takes -3 AC for 10 seconds (stackable up to -9) |
| 18 | **Divine Retribution** | When taking damage: 50% chance to deal equal radiant damage to attacker |
| 20 | **Avatar of Light** | 30 seconds: immune to damage; auto-crit all attacks; aura heals 2d8+WIS/sec to allies |

---

### 5.7 RANGER — Full Ability Tree

**Subclasses at Level 10:** Hawkeye or Beastmaster

#### Core Abilities (All Rangers)

| Level | Ability | Type | Description |
|-------|---------|------|-------------|
| 1 | **Hunter's Mark** | Bonus Action | Mark target; +1d6 damage vs. marked target; mark moves on kill |
| 1 | **Archery** | Passive | +2 to ranged attack rolls |
| 2 | **Natural Explorer** | Passive | +perception in chosen terrain; cannot be surprised in that terrain |
| 3 | **Multishot** | Action (Spell Slot) | Fire 3 arrows at up to 3 different targets; 1d8+DEX each |
| 4 | **Colossus Slayer** | Passive | First hit per round on target below max HP: +1d8 |
| 5 | **Extra Attack** | Passive | Attack twice with Action |
| 6 | **Volley** | Action (Spell Slot) | Barrage; 1d8+DEX to all enemies in 4-tile radius |
| 7 | **Fleet Footed** | Passive | +20% movement speed; no stealth penalty when moving |
| 8 | **Evasive Maneuver** | Reaction | Dodge and move 3 tiles when targeted by melee |
| 9 | **Foe Slayer** | Passive | +DEX modifier added to damage vs. favored enemy type (chosen at Lv 1) |

#### Hawkeye Subclass (Levels 10–20)

| Level | Ability | Description |
|-------|---------|-------------|
| 10 | **Precision Shot** | Ignore half and three-quarters cover; +2d6 on next shot after 2-second aim |
| 12 | **Crippling Arrow** | On hit: target speed -50% for 10 seconds (no save) |
| 14 | **Eagle Eye** | Minimap reveals all enemy positions in zone for 30 seconds. Cooldown: 60s |
| 16 | **Piercing Shot** | Arrow passes through all entities in a line (up to 6 tiles); hits each once |
| 18 | **Thousand Needles** | Fire 12 arrows at once in a cone; 1d6+DEX each |
| 20 | **Deadeye** | All attacks auto-crit for 10 seconds. Cooldown: 3 min |

#### Beastmaster Subclass (Levels 10–20)

| Level | Ability | Description |
|-------|---------|-------------|
| 10 | **Beast Companion** | Summon wolf/eagle/bear; fights alongside; HP = 50% of Ranger HP |
| 12 | **Pack Tactics** | Ranger and Beast gain Advantage when both attacking same target |
| 14 | **Bestial Fury** | Beast attacks twice per round |
| 16 | **Share Spells** | Ranger spells/buffs also apply to Beast |
| 18 | **Superior Beast** | Beast gains elite version with special ability (wolf: knockdown; eagle: blind; bear: maul) |
| 20 | **Nature's Wrath** | Summon 3 additional animal spirits for 30 seconds to swarm all enemies in 8-tile radius |

---

### 5.8 BARD — Full Ability Tree

**Subclasses at Level 10:** Spellsinger or Swashbuckler

#### Core Abilities (All Bards)

| Level | Ability | Type | Description |
|-------|---------|------|-------------|
| 1 | **Bardic Inspiration** | Bonus Action | Ally gains +1d6 to next roll. 3 charges per long rest |
| 1 | **Vicious Mockery** | Cantrip | WIS save DC 12 or target Disadvantaged on next attack; 1d4+CHA psychic |
| 2 | **Song of Rest** | Passive | Short rests in party restore extra 1d6 HP |
| 3 | **Hypnotic Pattern** | Level 1 Spell Slot | Charm up to 4 enemies in 4-tile zone for 30 seconds (WIS save DC 13) |
| 4 | **Countercharm** | Bonus Action | Allies within 6 tiles immune to Charm and Fear for 30 seconds |
| 5 | **Magical Secrets** | Passive | Learn 2 spells from any class spell list |
| 6 | **Jack of All Trades** | Passive | Add half proficiency to all non-proficient checks |
| 7 | **Cutting Words** | Reaction | Reduce enemy's roll by 1d8 (after seeing result) |
| 8 | **Power Word Stun** | Level 3 Spell Slot | Target below 150HP is Stunned for 10 seconds (no save) |
| 9 | **Superior Inspiration** | Passive | Never start combat with 0 Bardic Inspiration charges |

#### Spellsinger Subclass (Levels 10–20)

| Level | Ability | Description |
|-------|---------|-------------|
| 10 | **Song of Might** | Continuous song: party +2 to attack rolls while Bard is within 10 tiles |
| 12 | **Resonating Chord** | AoE sound blast; 4d8 thunder in 6-tile radius (CON save DC 15 for half) |
| 14 | **Discord** | Target hears discordant notes; -4 to all rolls for 15 seconds (WIS save DC 16) |
| 16 | **Epic Ballad** | 60-second song: all party members gain +3 to all rolls + 10% bonus XP for encounter |
| 18 | **Word of Creation** | Summon a celestial instrument construct; fights as an ally for 30 seconds |
| 20 | **Grand Finale** | Channel all remaining Bardic Inspiration into one massive explosion: 12d8+CHA thunder to all enemies within 12 tiles |

#### Swashbuckler Subclass (Levels 10–20)

| Level | Ability | Description |
|-------|---------|-------------|
| 10 | **Fancy Footwork** | After melee attack: Disengage for free; cannot be opportunity-attacked |
| 12 | **Rakish Audacity** | Sneak Attack without ally adjacent if 1v1 with target |
| 14 | **Panache** | Charm one humanoid enemy per combat (CHA contest; charmed = no attack Bard) |
| 16 | **Elegant Maneuver** | Use Bonus Action to gain Advantage on next Acrobatics or Athletics check |
| 18 | **Master Duelist** | Once per round: if you miss, reroll the attack with Advantage |
| 20 | **En Garde** | Enter duelist stance: all incoming attacks have Disadvantage; +4 to hit |

---

## 6. Combat System

*(Unchanged from v0.2 — RTD system, 20 ticks/sec, dice resolution, conditions, saving throws, advantage/disadvantage, spell slots, monster design)*

See v0.2 Section 6 for full spec. Phaser.js confirmed as rendering layer — combat animations use Phaser tweens and sprite sheet state machines.

---

## 7. Progression & Advancement

*(Unchanged from v0.2)*

Level cap 20. XP curve, level-up rewards, equipment rarity, skill checks, death/respawn — see v0.2 Section 7.

---

## 8. Crafting System

**Full specification:** `game-design/crafting/crafting-system.md`

AETHERMOOR features six professions (Blacksmithing, Tailoring, Alchemy, Cooking, Enchanting, Woodcrafting). Players choose two primary professions at character creation. Crafting provides an alternative progression path — crafted gear competes with dungeon drops; crafted consumables and housing items are **only obtainable through crafting**.

**Quick reference:**
- Two primary professions per player (changeable with 30-day cooldown)
- Gathering nodes in world (ore, herbs, wood, cloth from enemies, crystals)
- Crafting stations in every town and player housing (with Crafter's Bench)
- Crafting quality scales with profession level (craftsmanship bonus)
- Exceptional craft (5% base, 15% at Master+ L16+ with visible tooltip, 100% at Grand Master L20)
- Crafted items are **BOE (Bind-on-Equip)** — tradeable until equipped

---

## 9. Housing System *(NEW in v0.3)*

### 9.1 Overview

The Housing System gives every player a **persistent, personalised space** in Aethermoor — a home base that persists between sessions, can be visited by friends, and grows with the player over time. Housing serves as a **long-term sink** for gold, crafting materials, and seasonal cosmetics, and provides meaningful passive bonuses.

**Design intent:** Housing should feel like a reward for engaging with the whole game — exploration, crafting, dungeons, and seasons all contribute items and decor. It must not be required to progress; it enhances the experience.

### 9.2 Plot Types

| Plot Tier | Cost | Max Rooms | Visitor Cap | Region |
|-----------|------|-----------|-------------|--------|
| **Hovel** | 500g | 1 | 2 visitors | Any town outskirts |
| **Cottage** | 2,500g | 3 | 4 visitors | Any town outskirts |
| **Manor** | 10,000g | 6 | 8 visitors | City of Aethermoor exclusive |
| **Guild Hall Annex** | Guild purchase (50,000g) | 10 | 20 visitors | City of Aethermoor, guild-shared |

- Plots purchased from the **Housing Registrar** NPC in any town
- Each account may own **one personal plot** at any time (upgrade = old plot sold at 75% value)
- Guild Hall Annex is shared by entire guild, managed by Leader/Officers

### 9.3 Housing Zones — Technical Model

```
Player visits home → Server spawns private housing instance
   (or re-uses warm instance if owner was recently online)
Instance contains: tile layout + furniture object list (from DB)
Visitors join owner's instance via invite or public listing
Instance torn down after all players leave + 10 min idle timer
All furniture state persisted to PostgreSQL on placement/removal
```

- **Instance cap:** 8 players per housing instance (20 for Guild Annex)
- **Warm instance pool:** Frequently visited homes pre-warmed in idle pool
- **Offline access:** Visitors may browse a static screenshot of a player's home when offline; cannot enter

### 9.4 Furniture & Decoration

Furniture comes from multiple sources ensuring all game systems contribute:

| Source | Example Item | Rarity |
|--------|-------------|--------|
| General Store (gold) | Wooden Chair, Stone Fireplace | Common |
| Crafting (Tailoring) | Silk Curtains, Woven Rug | Uncommon |
| Crafting (Blacksmithing) | Iron Candelabra, Forge Display | Uncommon |
| Dungeon Chests | Ancient Trophy Case, Dungeon Boss Trophy | Rare |
| World Events | Event-themed decor (Ember Sconce, Frost Globe) | Rare |
| Seasonal Shop | Seasonal cosmetics (Harvest Scarecrow, Ice Lantern) | Seasonal |
| Faction Vendors (Revered+) | Faction-themed banners, statues | Rare |
| Legendary Drops | "Arcanist's Reading Chair" (unique) | Legendary |
| Achievement Unlocks | Trophy mounts (boss heads), medals, framed lore scrolls | Achievement |

### 9.5 Furniture Placement (UI)

**Mobile:**
- Tap furniture in inventory → Enter placement mode
- Drag to position; grid snaps to 1-tile increments
- Pinch to rotate (90° snapping)
- Tap placed item → context menu: Move / Remove / Inspect

**Web/Tablet:**
- Click and drag from furniture panel sidebar
- Right-click placed item → Move / Remove / Inspect
- Grid overlay shows valid placement zones (green = valid, red = blocked)

**Design rule:** Furniture placement must work comfortably on a 360px wide screen. No drag-and-drop that requires precision smaller than 44px.

### 9.6 Passive Housing Bonuses

Owning and furnishing a home provides passive bonuses — encouraging engagement without gating progress.

| Bonus | Trigger | Effect |
|-------|---------|-------|
| **Rested XP** | Log out in your home | +25% XP for first 30 minutes next session (same as Inn but free) |
| **Crafter's Bench** | Crafting Station placed in home | Craft from home without town visit |
| **War Room** | Map Table placed | View world event schedule 30 min earlier than Notice Board |
| **Vault** | Safe/Chest placed | +50 inventory slots (personal bank extension) |
| **Trophy Room** | 5+ boss trophies placed | +5% gold drop from all bosses |
| **Garden** | Garden Patch placed | Passively grows 1 random herb per real-time hour (Alchemy use) |

### 9.7 Social Features

- **Home Listing:** Players can list their home as "Public" — appears in Housing Directory, any player can visit
- **Guest Book:** NPC book item; visitors can leave a signed message
- **Home Rating:** Visitors can thumbs-up a home; most-liked homes featured in the City of Aethermoor on a "Homes of Note" bulletin board
- **Housing Competitions:** Seasonal event — build to a theme (e.g., "Harvest Hearth"); top-rated homes win cosmetic prizes
- **Party in a Home:** Groups of up to 8 can gather in a home; chat, trade, inspect gear — low-pressure social hub

---

## 10. MMO Social Systems

*(Unchanged from v0.2 — Party system, Guild system, World Events, PvP, Trading & Economy)*

---

## 11. PvP Factions

*(Unchanged from v0.2 — Aetheric Order, Verdant Pact, territory control, battlegrounds, faction lore)*

---

## 12. Seasonal Content

*(Unchanged from v0.2 — quarterly seasons, Year 1 calendar, season pass structure, world events, leaderboards)*

---

## 13. Dungeon Bestiary *(NEW in v0.3)*

### 13.1 Overview

The Dungeon Bestiary catalogs all **15 launch dungeons** with room counts, enemy types, unique mechanic, and boss design. This is the CTO's primary reference for dungeon instance spawning and content loading.

**Dungeon Instance Rules (All):**
- 1–4 players, private instance
- Spin-up target: <1 second
- All enemies and chests reset on each run
- First clear per week grants "Dungeon Weekly" reward (bonus loot + XP)
- Challenge Mode (Level 15+): time-limited, leaderboard, +1 loot tier

---

### 13.2 Region 1 — City of Aethermoor / Ruins

#### DUNGEON 1: Ruins of the First Aethermoor
*Recommended Level: 1–5 | Rooms: 6 | Type: Story*

**Theme:** Crumbling arcane library beneath the city. Tutorial dungeon — teaches core mechanics.

**Unique Mechanic:** Glowing Glyph Plates — step on plates in the correct sequence (shown in faded wall carvings) to open locked doors. Wrong sequence = 1d6 arcane damage per wrong step.

**Enemy Roster:**

| Enemy | HP | AC | Attack | Special |
|-------|----|----|--------|---------|
| Arcane Remnant | 15 | 11 | 1d6 arcane | Spawns on death: 1 Spark Mote |
| Spark Mote | 5 | 8 | 1d4 lightning | Seeks player; explodes on contact |
| Glyph Golem | 40 | 14 | 2d6 + Stun | Immune to glyph plate damage |

**Boss: The Hollow Knight**
- HP: 180 | AC: 16 | Phase 1: Sword sweep 3d8+4, telegraphed 1.5s wind-up
- Phase 2 (<50% HP): Gains ghostly shield (+4 AC); spawns 2 Arcane Remnants per round
- **Mechanic:** Standing on both glyph plates simultaneously removes ghostly shield
- **Loot:** Hollow Edge (Uncommon sword, +1d6 arcane), Sundered Key Fragment (quest item)

---

#### DUNGEON 2: The Waterlogged Crypts
*Recommended Level: 3–7 | Rooms: 8 | Type: Challenge*

**Theme:** Flooded crypts beneath the city; undead + water hazards.

**Unique Mechanic:** Rising Water — rooms gradually flood over 90 seconds. Players must clear enemies and exit before water reaches ceiling (instant wipe at full flood). Water level slows movement at 50%, prevents attacks at 75%.

**Enemy Roster:**

| Enemy | HP | AC | Attack | Special |
|-------|----|----|--------|---------|
| Drowned Skeleton | 20 | 12 | 1d8 | Regenerates 2HP/sec while in water |
| Crypt Crawler | 30 | 10 | 2d4 + Poison | Climbs walls; attacks from above |
| Bog Wraith | 50 | 13 | 2d6 cold | Phases through water; immune to Slow |

**Boss: Waterkeeper Maldren**
- HP: 250 | AC: 15 | Controls water level in boss room
- Phase 1: Floods room to 25% — movement slowed
- Phase 2 (<60% HP): Floods to 60% — attacks slowed; boss gains regenerate 5HP/sec
- Phase 3 (<30% HP): Drains water completely; boss enrages; +50% damage, -2 AC
- **Mechanic:** Drain lever on each wall; players must hit 3 levers to drain water in Phase 2
- **Loot:** Tide Rune (traversal tool — enables swimming in overworld), Drowned Pauldrons (Rare armor)

---

### 13.3 Region 2 — Thornwood Forest

#### DUNGEON 3: The Bramble Maze
*Recommended Level: 5–8 | Rooms: 9 | Type: Story*

**Theme:** Living dungeon — vines shift and regrow, blocking paths.

**Unique Mechanic:** Living Vines — corridors can be blocked by vine walls. Burned (fire damage) or cut (DEX check DC 13) to clear. Regrow after 60 seconds. Ranger/Archmage classes excel here.

**Enemy Roster:**

| Enemy | HP | AC | Attack | Special |
|-------|----|----|--------|---------|
| Thornback Beetle | 25 | 13 | 1d8 pierce | Immune to physical; vulnerable fire |
| Vine Lurker | 35 | 11 | 2d6 + Entangle | Entangle: DEX save DC 12 or rooted 2 rounds |
| Bramble Sprite | 20 | 14 | 1d6 + Poison | Teleports when at <30% HP |

**Boss: The Thornmother**
- HP: 320 | AC: 14 | Immobile; controls 6 vine tendrils
- Phase 1: Tendrils attack (1d10 each); players destroy 3 of 6 tendrils (30HP each)
- Phase 2: Vines regrow faster; boss gains ranged seed volley (4 targets, 2d6 each)
- **Mechanic:** Burning all 6 tendril stumps simultaneously (within 5 seconds) triggers a 10-second vulnerability window for triple damage
- **Loot:** Verdant Bracer (Rare, +WIS +2 and +10% healing), Thornwood Staff (Rare arcane weapon)

---

#### DUNGEON 4: The Elder Root Vault
*Recommended Level: 8–12 | Rooms: 10 | Type: Challenge*

**Theme:** Ancient Pact sanctuary buried beneath the oldest tree in Thornwood.

**Unique Mechanic:** Light Beams — ancient crystal prisms redirect light beams that unlock doors. Players rotate prisms (puzzle) while enemies attack. Beams also deal 1d8 to enemies caught in path.

**Boss: Root Warden Kaeseth** (Ancient treant)
- HP: 450 | AC: 17 | Three-phase fight
- Mechanic: Redirect the dungeon's light beam to strike Kaeseth's 3 glowing knots (one per phase) while surviving AoE root slams (3d6, 5-tile radius, DEX save DC 15)
- **Loot:** Sap of the Elder (Epic potion: full heal + 30-second invulnerability), Knotwood Shield (Rare, +3 AC, chance to root attacker)

---

### 13.4 Region 3 — Crystal Caves

#### DUNGEON 5: The Resonance Chamber
*Recommended Level: 7–10 | Rooms: 8 | Type: Story*

**Theme:** Deep crystal cave where Aether resonance is weaponized. Sound-based puzzles.

**Unique Mechanic:** Sound Waves — certain enemies and walls emit harmful resonance waves (visible as ripple animations). Moving into a wave = 2d6 thunder. Waves can be silenced by standing on a crystal dampener pad.

**Boss: Resonance Wraith Olveth**
- HP: 300 | AC: 14 | Becomes immune to damage when emitting resonance aura (visual: glowing outline)
- Players must stand on all 4 dampener pads simultaneously to suppress the aura
- Requires coordination: ideal for 4-player party; soloable via careful rotation
- **Loot:** Crystal Resonator (Epic wand, +2d6 thunder on all spells), Silence Rune (utility: silences enemies in 4-tile radius for 5 seconds, 3 charges)

---

#### DUNGEON 6: The Fractured Spire
*Recommended Level: 10–14 | Rooms: 12 | Type: Challenge*

**Theme:** Vertical dungeon; players ascend a collapsing crystal spire. Gravity-defying platforms.

**Unique Mechanic:** Crystal Gravity Pads — step on inverted pads to walk on ceiling, then walls. Enemies can also use gravity pads. Falling off ledges = 2d6 fall damage + respawn at room start.

**Boss: The Spire Guardian (3-form)**
- Form 1 (floor): Standard melee boss with crystal AoE
- Form 2 (ceiling): Flips gravity in room; players must walk on ceiling to attack
- Form 3 (walls): Spins, creating rotating safe lanes; players dodge and attack in windows
- **Loot:** Aetherhook Gadget (traversal tool — enables hookshot across gaps in overworld), Spire Crystal Armor set (3-piece Epic set)

---

### 13.5 Region 4 — Frostpeak Mountains

#### DUNGEON 7: The Frost Tomb
*Recommended Level: 9–13 | Rooms: 9 | Type: Story*

**Theme:** Frozen burial chamber of an ancient giant war general.

**Unique Mechanic:** Ice Physics — frozen floor tiles cause sliding (cannot stop movement mid-slide). Push enemies into walls for bonus stun damage. Melt ice with fire damage (4×4 tile area).

**Enemy Roster:**

| Enemy | HP | AC | Attack | Special |
|-------|----|----|--------|---------|
| Frost Revenant | 45 | 14 | 2d6 cold | Slides toward player; unstoppable until wall |
| Ice Golem | 80 | 17 | 3d6 + Freeze | Shatters on death: 2d4 shrapnel to adjacent tiles |
| Glacier Sprite | 20 | 12 | 1d6 + Slow | Creates new ice tiles on movement |

**Boss: General Hroth the Frozen**
- HP: 500 | AC: 18 | Massive giant; 4 phases at 75%, 50%, 25% HP
- Phase 2: Freezes entire floor — permanent ice physics
- Phase 3: Hurls boulders (4d10 + knockback), creating obstacles
- Phase 4: Enrage — one-shots any player hit directly
- **Mechanic:** Four heat crystals on walls; fire on crystals to create temporary safe (non-ice) zones
- **Loot:** Giant's Grudge (Legendary two-handed sword, 2d12+STR, +5 against Giants), Frostplate Armor (Rare, Cold immunity)

---

#### DUNGEON 8: The Sky Bridge Ruins
*Recommended Level: 12–16 | Rooms: 11 | Type: Challenge*

**Theme:** Crumbling ancient sky bridge between peaks; outdoor dungeon with wind hazards.

**Unique Mechanic:** Wind Gusts — periodic gusts push players toward ledge edges. Anchor posts on floors can be grabbed (tap/click) to resist. Enemies light enough to be pushed off ledges.

**Boss: Storm Drake Vethran** (flying boss)
- Lands on platform every 30 seconds to be attacked; otherwise divebombs from air
- Phase 2: Calls storm — gust frequency doubles
- **Loot:** Stormrider Cloak (Rare, +DEX +2, immunity to wind push), Drake Wing Fragment (crafting material for Epic bow)

---

### 13.6 Region 5 — Ember Plains

#### DUNGEON 9: The Ember Forge
*Recommended Level: 11–15 | Rooms: 10 | Type: Story*

**Theme:** Volcanic forge where the Ember Tribes craft weapons for their war machine.

**Unique Mechanic:** Lava Floors — certain tiles are lava (2d6 fire per second while standing). Moveable metal platforms (push with STR check DC 13) create crossing paths.

**Boss: Forgemaiden Scorra** (Ember Tribe champion)
- HP: 480 | AC: 16 | Fights in forge surrounded by lava channels
- Phase 2: Pulls lava across more of the floor — reduces safe space by 50%
- Phase 3: Weaponizes forge bellows — periodic lava jets from walls (telegraphed 2 seconds early)
- **Loot:** Scorra's Ember Brand (Epic dagger, 1d10+DEX + 2d6 fire on crit), Forge Apron (Rare cosmetic + crafting speed +10%)

---

#### DUNGEON 10: The Ashen Catacombs
*Recommended Level: 14–18 | Rooms: 12 | Type: Challenge*

**Theme:** Buried catacombs beneath the Ember Plains; awakened undead and fire elementals.

**Unique Mechanic:** Combustion Zones — ash clouds in rooms ignite if any fire spell used (2d8 AoE to everyone present). Players must choose: use fire abilities and risk group damage, or fight at reduced capacity.

**Boss: The Ashen Archon** (Undead fire colossus)
- HP: 650 | AC: 19 | Immune to fire; vulnerable to cold
- Mechanic: Fire abilities trigger room combustion; Archmage Elementalists specialising in ice are MVP
- Phase 3: Exhales permanent ash cloud across full room — all fire spells forbidden or party wipes
- **Loot:** Archon's Crown (Legendary helmet, +INT/WIS +3, fire immunity), Colossus Core (crafting material for Legendary Archmage staff)

---

### 13.7 Region 6 — Verdant Jungle & Deep Sites

#### DUNGEON 11: The Bloom Sanctum
*Recommended Level: 13–17 | Rooms: 10 | Type: Story*

**Theme:** Living dungeon deep in the Verdant Jungle; responds to player actions — aggressive if attacked, passive if calm.

**Unique Mechanic:** Bloom Response — the dungeon tracks player aggression score. Running (not fighting) through rooms lowers aggression; killing enemies raises it. High aggression = dungeon spawns extra enemies and tightens vines. Low aggression = dungeon opens secret paths and reduces enemy HP.

**Boss: The First Bloom** (Rootbinder fragment)
- HP: 600 | AC: 15 | Changes form based on aggression score at arrival
- Low aggression: Peaceful form — offers dialogue option; partial skip (Bloom tells location of Archon Crown hint)
- High aggression: Rage form — three-phase fight with earthquake AoE, vine tendrils, seed bomb barrages
- **Loot:** Bloom Seed (Quest item — Act 4 key), Verdant Mantle (Epic cape, +WIS +3, nature damage immunity)

---

#### DUNGEON 12: The Sunken Archives
*Recommended Level: 15–18 | Rooms: 11 | Type: Challenge*

**Theme:** Pre-Sundering library, partially submerged. Requires Tide Rune to access lower levels.

**Unique Mechanic:** Knowledge Locks — doors opened by reading floating text runes in correct sequence (sequence shown in lore books in previous rooms). Rewards players who explore and read.

**Boss: Archivist Prime** (Construct of preserved knowledge)
- HP: 700 | AC: 18 | Can rewind 5 seconds to undo player position (Phase 3 mechanic)
- Mechanic: Players must identify which knowledge lock room he accessed (shown in his attack pattern) and activate the matching rune sequence to stun him
- **Loot:** Archivist's Tome (Epic offhand, +INT +4, +1 Spell Slot), Sunken Key (opens final raid wing)

---

### 13.8 Cross-Region — Endgame Dungeons

#### DUNGEON 13: The Aether Rift Delve
*Recommended Level: 17–20 | Rooms: 14 | Type: Challenge (weekly)*

**Theme:** Unstable dimensional rift; rules of physics constantly shift.

**Unique Mechanic:** Reality Tears — random room effects each run: reversed controls (1 in 6 rooms), doubled enemy HP (1 in 6), or healing tiles (1 in 6). Players never know which combination they get.

**Boss: The Rift Sovereign** (Rotating random from pool of 5)
- Pool includes remixed forms of previous bosses with modified mechanics
- Ensures endgame replay value; no two Rift Delve runs feel identical
- **Loot:** Rift Crystal (upgrades Legendary items to +1 tier stat), Rift Title: "Sovereign Slayer"

---

#### DUNGEON 14: Temple of the First Root (Raid — 16 Players)
*Recommended Level: 18–20 | Type: Raid (Act 4 climax)*

**Theme:** The Rootbinder's awakening chamber — final story dungeon.

**Structure:** 5 wings, each requiring 4 players to split and solve simultaneously. Wings reconverge at final boss.

**Final Boss: The Rootbinder (Awakened)**
- HP: 4,000 (shared health pool) | AC: 20
- Phase 1: Split — each wing group fights a Rootbinder avatar (20% HP each)
- Phase 2: Combined — all 16 players converge; Rootbinder at 100% power
- Phase 3 (10% HP): Choice mechanic (Act 4 resolution) — Purify / Weaponize / Contain
- Each choice triggers a different cinematic ending sequence and grants different Legendary loot
- **Loot:** Legendary class-specific weapons (one per class per ending), "Worldshaper" title

---

#### DUNGEON 15: The Shattered Observatory (Sky Archipelago)
*Recommended Level: 19–20 | Rooms: 13 | Type: Challenge + Story (Season 4)*

**Theme:** The Weaver's final refuge; unlocks in Season 4 (The Shattered Sky).

**Unique Mechanic:** Gravity Inversion Zones + Crystal Lens Puzzles combined. Most mechanically complex dungeon at launch.

**Boss: The Weaver's Echo (Final Season 4 Raid Boss)**
- HP: 3,500 | 16-player raid
- Mechanic: Players must reconstruct the Weaver's original Aether Crystal by solving 4 simultaneous crystal lens puzzles while tanks hold the Echo's attention
- **Loot:** "Ascendant" cosmetic armor set (class-specific skin), Weaver's Chronicle (Legendary offhand INT +5), Season 4 title: "Child of the Weaver"

---

## 14. UI/UX — Mobile, Tablet, Web

*(Unchanged from v0.2 — mobile HUD, tablet layout, web controls, shared UX rules, crafting UI spec)*

**Phaser.js notes for CTO:**
- Use Phaser's built-in Scene manager — one scene per zone/dungeon type
- Input handling: Phaser's pointer events for touch + mouse; keyboard plugin for web
- UI layer: Phaser's DOM element plugin for HTML-overlay UI (inventory, menus) — keeps UI responsive across screen sizes without canvas constraints
- Scaling: Phaser ScaleManager with `FIT` mode and letterboxing — maintains aspect ratio on all screen sizes

---

## 15. Technical Requirements for CTO

### 15.1 Confirmed Engine Stack

| Component | Technology | Decision |
|-----------|-----------|----------|
| **Rendering** | Phaser.js (WebGL / Canvas fallback) | Confirmed by CEO |
| **Language** | TypeScript | Aligns with company monorepo |
| **Mobile delivery** | WebView wrapper (Capacitor or similar) | TBD — CTO to confirm |
| **Backend** | Node.js / TypeScript preferred | TBD — CTO to confirm |
| **Database** | PostgreSQL + Redis | As specified |
| **Asset CDN** | TBD | CTO to select |

### 15.2 Architecture Overview

```
Client (Phaser.js — Mobile WebView / Tablet WebView / Desktop Browser)
    <-> WebSocket (real-time game state — zone events, combat, chat)
    <-> REST API (auth, inventory, quests, market, crafting, housing, faction)

Game Server Layer
    +-- Zone Servers (authoritative, per zone/instance)
    +-- Global Server (chat, events, guilds, auctions, faction state)
    +-- Match Server (dungeon + battleground instance spawner)
    +-- Crafting Server (roll resolution, recipe validation)
    +-- Housing Server (instance management, furniture state)

Data Layer
    +-- PostgreSQL (player state, inventory, quests, guild, faction, housing, crafting)
    +-- Redis (session cache, zone state, pub/sub, territory bars, housing warm pool)
    +-- Object Storage / CDN (Phaser asset bundles: tilesets, spritesheets, audio)
```

### 15.3 Phaser.js Asset Pipeline (CTO Reference)

- **Tile size:** 32×32px; power-of-2 texture atlases (max 2048×2048px)
- **Sprite sheets:** 4-frame walk, 2-frame attack, 1-frame idle; row-per-direction (4 dirs)
- **Tilemap format:** Tiled JSON (.tmj) — server imports for collision map + event trigger zones
- **Atlas format:** Phaser-compatible JSON hash atlas (TexturePacker export)
- **Audio:** OGG + MP3 dual-format (Phaser auto-selects)
- **Asset loading:** Phaser Loader with progress bar; lazy-load zone assets on zone transition
- **Asset versioning:** Append content hash to filenames for cache-busting on CDN

### 15.4 Rendering & Camera System

**Camera Type:** Fixed viewport camera (Zelda-style)

**Architecture:**
- Player sprite is fixed at viewport center (non-scrolling)
- Camera positioned at player's logical world position
- World (tiles, NPCs) scrolls around player sprite
- Only visible tiles rendered (viewport + 1 tile padding)

**Benefits:**
- Supports arbitrarily large maps (1000×1000+ tiles)
- Constant memory usage regardless of map size
- Consistent UX across all map sizes
- Built-in performance optimization via viewport culling

**Technical Details:**
- Player sprite: `setScrollFactor(0)` — fixed at `(viewportWidth/2, viewportHeight/2)`
- Logical position tracked separately: `playerTileX`, `playerTileY`
- Camera scrolls via `camera.scrollX = playerWorldX - centerX`
- All world objects (tiles, NPCs, other players) scroll normally

**See:** `docs/technical/rendering-camera-system.md` for full implementation plan

### 15.5 Dungeon Instance Technical Spec

- Instances spawned by Match Server on `POST /dungeon/instance`
- Payload: `{dungeonId, partyId, playerIds[], difficulty}`
- Match Server selects from pre-warmed container pool
- Returns: `{instanceId, wsEndpoint, ttl}`
- Instance torn down: on completion + 5 min idle, or after 2-hour hard TTL
- Dungeon state loaded from JSON config (room layout, enemy spawn tables, boss phases)
- All 15 dungeons defined as JSON — no hardcoded dungeon logic in server core

### 15.5 Persistence Model

| Data Type | Storage | Write Pattern |
|-----------|---------|---------------|
| Player stats/inventory | PostgreSQL | Write on change |
| Housing furniture layout | PostgreSQL | Write on placement/removal |
| Housing instance state | Redis | Ephemeral; warm pool for frequent visitors |
| Crafting profession XP | PostgreSQL | Write on craft completion |
| Faction standing | PostgreSQL | Write on standing change |
| Territory control bar | Redis → PostgreSQL | Real-time Redis; checkpoint every 30s |
| Zone state (enemies) | Redis + Zone Server RAM | Ephemeral |
| Quest state | PostgreSQL | Write on quest step |
| Guild data | PostgreSQL | Write on change |
| Auction House | PostgreSQL | ACID transactions |
| Season pass progress | PostgreSQL | Write on XP gain |
| Chat messages | Redis pub/sub | Fire-and-forget, 24h retention |

### 15.6 Scalability Targets

| Metric | Target |
|--------|--------|
| Concurrent users (total) | 2,000 (soft cap, horizontal scale) |
| Players per overworld shard | 50 |
| Players per town shard | 200 |
| Housing instance player cap | 8 (20 for Guild Annex) |
| Server tick latency | <50ms p95 (in-region) |
| Dungeon instance spin-up | <1 second |
| Housing instance spin-up | <2 seconds |
| Battleground match spin-up | <3 seconds |
| API response time | <100ms p95 |
| Asset CDN cache hit ratio | >95% |
| Uptime SLA | 99.5% monthly |

### 15.8 Key APIs — Full List

| API | Purpose |
|-----|---------|
| POST /auth/login | JWT auth, OAuth (Google/Apple) |
| GET /player/{id}/state | Full player state on session load |
| WS /zone/{zoneId}/connect | Zone WebSocket |
| POST /dungeon/instance | Spawn dungeon instance |
| GET /inventory/{playerId} | Fetch inventory |
| POST /inventory/equip | Equip item (server-validated) |
| GET /quests/{playerId} | Active quest log |
| POST /quests/{questId}/progress | Advance quest step |
| GET /market/listings | Auction House browse |
| POST /market/bid | Place bid / buy-now |
| POST /guild/{guildId}/invite | Invite player to guild |
| GET /world/events | Current + upcoming world events |
| GET /crafting/recipes/{profession} | Known recipes |
| POST /crafting/craft | Execute craft (server resolves roll) |
| GET /faction/{factionId}/standing/{playerId} | Player standing |
| POST /faction/territory/capture | Submit capture tick |
| GET /season/current | Active season + pass progress |
| GET /season/leaderboard/{category} | Season leaderboard |
| GET /housing/{playerId}/plot | Player housing plot info |
| POST /housing/{plotId}/furniture | Place furniture |
| DELETE /housing/{plotId}/furniture/{id} | Remove furniture |
| GET /housing/directory | Public housing listings |
| POST /housing/{plotId}/visit | Join a housing instance |

---

## 16. Fishing Mechanic

### 16.1 Overview

Fishing is a relaxing, skill-based mini-game that gives players a rewarding break from combat and questing. It ties into the Crafting System (Cooking, Alchemy), the Economy (rare fish as trade goods), the Housing System (aquarium furniture), and PvP Factions (Sunken Docks contested territory). Fishing is intentionally accessible — a mobile player waiting for their party can fish productively in 2–3 minutes.

**Design Goals:**
- Provide a calm, satisfying activity with meaningful rewards
- Give Crafting players a non-combat resource path
- Anchor the Sunken Docks faction territory with unique content
- Work fully on mobile with one-handed tap input

---

### 16.2 Fishing Locations

| Location | Region | Fish Tier | Special Conditions |
|----------|--------|-----------|--------------------|
| Millhaven Docks | Millhaven (starter town) | Common, Uncommon | Always accessible |
| Sunken Docks | Ember Plains | Uncommon, Rare | Faction territory — must be controlled by your faction or be neutral |
| Crystal Lake | Crystal Caves (overworld approach) | Uncommon, Rare | Night only (18:00–06:00 game time) |
| Frostpeak Glacier | Frostpeak Mountains | Rare, Epic | Requires Cold Weather gear (Fur Cloak or equivalent) |
| Abyssal Vent | Rift Delve (overworld approach) | Epic, Legendary | Level 18+ only, solo or duo only |
| Hidden Grotto | Secret zone — discoverable via World Lore scroll | Legendary | Hidden zone entrance |

---

### 16.3 Fishing Rods & Equipment

**Rod Tiers** (each craftable or purchasable):

| Rod | Level Required | Bonus | Source |
|-----|---------------|-------|--------|
| Driftwood Rod | 1 | None | Millhaven starter vendor, 50g |
| Ironwood Rod | 5 | +10% catch speed | Blacksmithing lv 2 or fishing vendor |
| Aethersteel Rod | 10 | +15% rare fish chance | Blacksmithing lv 4 |
| Crystal Rod | 15 | +20% rare fish chance, chance to catch 2 fish | Crystal Cave vendor (Uncommon chest reward) |
| Void Rod | 20 | +30% epic/legendary fish chance, prevents fish escaping | Crafted: requires Void Shard (endgame mat) |

**Bait** (consumable, stackable to 99):

| Bait | Effect | Source |
|------|--------|--------|
| Worm | No bonus | Forage from overworld grass tiles |
| Dough Ball | +5% common catch rate | Cook (Cooking lv 1) |
| Shrimp | +10% uncommon catch rate | Fishing vendor, 5g each |
| Aether Lure | +20% rare catch rate | Alchemy lv 3 craft |
| Void Crumb | +25% epic/legendary catch rate | Season reward / Rift Delve vendor |

---

### 16.4 The Fishing Mini-Game

**Flow:**

1. Player equips rod and has bait selected in hotbar.
2. Player taps a **Cast** button (or presses F on desktop). A cast arc indicator appears — swipe/drag to aim on mobile, click target on desktop.
3. Bobber lands. A 5–30 second wait begins (random, shortened by Ironwood+ rod).
4. When a fish bites: the bobber bobs and a **BITE!** indicator pulses with audio cue.
5. Player taps the screen (any tap) or presses F to **Hook**.
6. A **Tension Bar** mini-game begins:
   - A fish icon pulls a line left/right on a horizontal bar.
   - Player taps-and-holds to reel; releases to rest.
   - Keeping the reel marker in the **green zone** (moves with fish) fills a **Catch Progress** bar.
   - If tension goes **red zone**, line snap warning plays — player must release immediately or line breaks.
   - Rare/Epic fish move faster and more erratically.
7. When Catch Progress reaches 100%: fish landed. Reward delivered to inventory.
8. If line snaps or player is too slow to hook: fish escapes. Bait is consumed.

**Mobile Considerations:**
- All actions are single tap or tap-and-hold — no joystick required
- Tension Bar is large (minimum 280px wide), high-contrast (green/yellow/red)
- BITE! pulse uses both visual and haptic feedback (mobile vibration API)
- Landscape and portrait both supported; bar orientation flips for portrait

---

### 16.5 Fish Catch Table

**Common (40% base weight):**

| Fish | Cooking Use | Sell Price |
|------|-------------|------------|
| Silverscale Trout | Cook: Grilled Trout (+5 STR, 30 min) | 8g |
| Murkminnow | Cook: Murk Stew (+5 CON, 30 min) | 6g |
| River Crab | Cook: Crab Broth (+10 HP regen, 15 min) | 10g |
| Speckled Bass | Cook: Bass Fillet (+5 DEX, 30 min) | 8g |

**Uncommon (35% base weight):**

| Fish | Use | Sell Price |
|------|-----|------------|
| Glowfin Eel | Alchemy: Clarity Tonic (+10 INT/WIS, 1hr) | 40g |
| Jade Carp | Crafting: Jewel Crafting mat; Housing: Jade Aquarium display | 55g |
| Ironback Turtle | Blacksmithing mat: Shell Plate (Shield bonus) | 65g |
| Deepwater Lantern Fish | Housing: Live aquarium furniture piece | 70g |

**Rare (18% base weight):**

| Fish | Use | Sell Price |
|------|-----|------------|
| Aetherfin Salmon | Cook: Aetherfin Stew (+15 to all stats, 2hr) | 200g |
| Void Jellyfish | Alchemy: Void Flask (Blink cooldown –2s, 1hr) | 250g |
| Crystalscale Pike | Enchanting mat: Crystal Dust (weapon enchant) | 300g |
| Sunken Relic | Not fish — chance of random Uncommon gear piece | 150g |

**Epic (6% base weight — rare locations only):**

| Fish | Use | Sell Price |
|------|-----|------------|
| Glacial Whale | Cook: Whale Feast (party buff, +20 all stats, 3hr) | 1,200g |
| Void Serpent | Pet: Void Serpent cosmetic companion unlock | 2,000g |
| Deep One's Eye | Alchemy: True Sight Elixir (+10% crit on bosses, 2hr) | 1,500g |

**Legendary (1% base weight — Abyssal Vent / Hidden Grotto only):**

| Fish | Effect | Notes |
|------|--------|-------|
| The Wandering Leviathan | Catch triggers server-wide announcement; player earns Leviathan Hunter title + trophy | Unique catch — only 1 per week per server. Sell to vendor: 10,000g |
| Aether Kraken Egg | Housing: Kraken Aquarium (passive CHA +5 to all visitors) | Bind on pickup |
| First Catch | Legendary fishing rod skin — Glowing | Bind on pickup, account-wide |

---

### 16.6 Fishing Skill Progression

Fishing has its own Skill Track separate from crafting professions:

| Level | Requirement | Unlock |
|-------|-------------|--------|
| Novice (1) | Default | Access to Millhaven, Driftwood Rod |
| Apprentice (10 catches) | 10 successful catches | Access to Crystal Lake night fishing |
| Journeyman (50 catches) | 50 successful catches | Tension Bar shrinks by 10% less erratically |
| Expert (150 catches) | 150 catches | Access to Abyssal Vent; +5% epic catch rate |
| Master (300 catches) | 300 catches + catch 1 Legendary | Unlock Hidden Grotto hint quest; +10% legendary rate |

---

### 16.7 Economy Integration

- Rare fish are a meaningful trade commodity on the Auction House
- Cooking players depend on fishing players for high-tier buff ingredients
- Alchemy players depend on fishing players for flask components
- The Sunken Docks territory produces +20% rare fish for the controlling faction — incentivising PvP defense
- Housing aquarium items drive a decorating economy for non-combat players
- Fishing-only players can be self-sustaining gold generators without ever entering a dungeon

---

### 16.8 MMO Considerations

- Fishing spot capacity: 8 concurrent fishers per dock node (server-side counter, soft visible indicator)
- Fish populations reset every 4 real hours — depleted spots reduce yield by 20% but never to zero
- Legendary fish have a 1-per-week server cooldown (not player cooldown) — creates emergent events
- Fishing in Faction territory requires real-time flag check (HTTP poll every 30s is acceptable latency)
- All fish storage is server-side inventory — no client-authoritative catches

---

### 16.9 Technical Notes for CTO

| Item | Spec |
|------|------|
| Mini-game rendering | Phaser.js scene, overlaid on world — pause player movement during mini-game |
| Cast arc | Line arc tween, 16 cast directions (22.5° increments), snap to nearest tile |
| Tension Bar | Phaser.js Graphics object, 60fps update |
| Fish bite timing | Server-side random seed, result returned via WebSocket event |
| Catch validation | Server validates fish type at catch completion — client sends only "catch complete" signal |
| Inventory | Adds to standard inventory stack; fish stack to 99 |
| Sunken Docks faction check | Piggyback on faction territory tick (existing system) |
| Legendary server announce | WebSocket broadcast to all connected clients in same shard |

---

## 17. NPC Dialogue Trees (Sample)

### 17.1 Overview

AETHERMOOR NPCs use a **branching dialogue tree** system. Every named NPC has:
- A **greeting** (changes based on time of day, player faction, player level, quest state)
- 2–4 **primary dialogue options** (player-driven)
- **Response branches** that can award items, advance quests, reveal lore, or open shops
- An **exit line** that varies by relationship state

All dialogue is written in-engine as a JSON dialogue tree, compiled from this GDD's sample scripts into engine-ready format by the CTO.

**Design Goals:**
- NPCs feel like individuals, not bulletin boards
- Player choices should feel consequential (even minor ones)
- Dialogue should be short — mobile players read quickly
- Quest-critical information must always be accessible (no one-time-only dialogue)

---

### 17.2 Dialogue Tree — Elara Thornwick (Millhaven Innkeeper)

**Context:** Elara runs the Millhaven Inn. She gives the first main quest, provides rest bonuses, and has a personal storyline about her missing son.

---

**GREETING** (first visit):

> *"Welcome, stranger. Don't get many adventurers through Millhaven these days — not since the Ashgate Road went dark. You look like you can handle yourself. Bed's 10 gold a night if you need rest."*

**GREETING** (returning, Rested status active):

> *"Sleep well? You've got that look — rested and ready. The road won't wait for you."*

**GREETING** (returning, Aetheric Order faction):

> *"Ah, an Order member. My late husband served the Order. We've got a room set aside for Order folk — 8 gold, no questions asked."*

---

**PRIMARY OPTIONS:**

**[A] "What happened to the Ashgate Road?"**

> *"Three months ago, merchants stopped coming through. Scouts went to look — two came back. Said the road's been swallowed by the Thornwood. Old trees moving, they said. Nothing natural about it. The Verdant Pact blames the Order. The Order blames the Pact. I just want safe roads again."*

→ Reveals: Thornwood Forest is corrupted (World Lore hint). No reward.
→ Unlocks dialogue option [A1]:

**[A1] "Has anyone investigated the Thornwood?"**

> *"My boy Tam went to look two weeks ago. Said he'd be back in three days. I... I've given up hoping. If you're the investigating type — the Thornwood entrance is north of the old mill. Please. If you find anything..."*

→ Triggers quest: **"What the Thornwood Took"** (Main Story, Act 1 Step 2)
→ Journal update: "Find Tam Thornwick in the Thornwood."

---

**[B] "I need a room."**

> *"10 gold a night. You'll wake up with Rested XP — that means 50% bonus experience for two hours. Worth it if you're grinding."*

→ Opens lodging purchase UI: 10g / night (standard) | 8g if Order faction | 12g for Premium Room (+3hr Rested)

---

**[C] "What do you sell?"**

> *"Basic provisions. Trail rations, torches, bandages. Nothing fancy — Millhaven's not what it was."*

→ Opens shop: Trail Rations (5g, +20 HP on use), Torch (2g, 1hr light radius), Bandage (8g, +50 HP over 10s out of combat)

---

**[D] "Tell me about Millhaven."**

> *"Two hundred years old, or near enough. Founded by the Aether Council as a waystation between the capital and the Crystal Caves. Good folk here. Farmers, mostly. The dungeon under the old manor — the Greystone Crypts — used to be sealed. A year ago the seal broke. That's when the trouble started."*

→ Lore delivered. Unlocks Greystone Crypts dungeon marker on map (if not already discovered).

---

**EXIT OPTIONS:**

- (After quest trigger): *"Safe travels. And please — find my boy."*
- (Default): *"The fire's on if you need warmth. Mind the curfew bell."*
- (Order faction): *"For the light, traveller."*

---

### 17.3 Dialogue Tree — Garrak Stonefist (Frostpeak Blacksmith)

**Context:** Gruff dwarf blacksmith in Frostpeak Village. Sells high-tier weapons and armor. Has a personal quest about a stolen forge-hammer.

---

**GREETING** (first visit, Level < 10):

> *"Aye? You look barely old enough to hold a sword. Come back when you've seen a few dungeons, then we'll talk business."*

**GREETING** (Level 10+):

> *"Now THAT'S a traveller who's done some living. Welcome to Stonefist's. Finest steel north of the Ember Plains."*

**GREETING** (if player has completed his quest):

> *"My hammer's back where it belongs, thanks to you. Mates' rates apply — always."*

---

**PRIMARY OPTIONS:**

**[A] "Show me your wares."** → Opens blacksmith shop (Tier 3 weapons/armor, level 10–16)

**[B] "Can you repair my gear?"** → Opens repair UI (cost: 5% of item base value)

**[C] "You seem troubled."** *(Only available: Level 10+)*

> *"Aye. My grandfather's forge-hammer — Emberstrike — was nicked. Three days ago. I know who did it: that thieving Rogue guild that's taken up in the old mine. Wouldn't bother me to ask you to go get it back. But I'd owe you. Proper."*

→ Triggers quest: **"Emberstrike"** (Side Quest, Frostpeak)
→ Quest objective: "Retrieve Emberstrike from the Frostpeak Mine Rogue camp."

**[D] "What do you know about the mountains?"** → Lore dump, hints at Dungeon 7 (Glacial Citadel).

---

### 17.4 Dialogue System — Technical Spec for CTO

| Property | Spec |
|----------|------|
| Format | JSON dialogue tree, one file per NPC |
| Conditions | `requiresLevel`, `requiresFaction`, `requiresQuestState`, `requiresTimeOfDay`, `requiresItemInInventory` |
| Rewards | `giveItem`, `giveGold`, `giveXP`, `triggerQuest`, `updateQuestStep`, `openShop`, `openLodging` |
| Node types | `greeting`, `option`, `response`, `exit` |
| Dialogue rendering | Modal overlay (Phaser DOM overlay); portrait image + text + options list |
| Mobile layout | Portrait image (64×64px), scrollable text box, max 4 option buttons (44px tall) |
| Localisation | All text referenced by key; locale JSON files loaded per language |
| State persistence | Quest state, faction standing, and dialogue flags stored server-side per player |

---

## 18. Quest Scripts (Sample)

### 18.1 Overview

AETHERMOOR quests follow a structured script format that defines: trigger, objectives, NPC interactions, progress checkpoints, rewards, and branch outcomes. Every quest script in this section is implementation-ready for the CTO to build quest engine logic from.

---

### 18.2 Main Quest — "What the Thornwood Took" (Act 1, Step 2)

**Quest ID:** `MQ_ACT1_002`
**Quest Type:** Main Story
**Level Range:** 1–5
**Prerequisites:** Complete `MQ_ACT1_001` (Arrive in Millhaven)
**Quest Giver:** Elara Thornwick (Millhaven Inn) — via Dialogue Option A1
**Turn-in NPC:** Elara Thornwick (Millhaven Inn)

---

**Summary:**
Elara's son Tam went missing investigating the Thornwood corruption. The player must enter the Thornwood, find Tam, discover the source of the corruption (a corrupted Aether Crystal), and return Tam to safety.

---

**Objectives:**

| Step | Objective | Completion Condition |
|------|-----------|---------------------|
| 1 | Travel to the Thornwood entrance (north of Millhaven Mill) | Player enters Thornwood zone |
| 2 | Investigate the Thornwood | Player discovers 3 Corruption Nodes (glowing tiles, interact) |
| 3 | Find Tam Thornwick | Player reaches Tam's location (scripted spawn point, zone northeast) |
| 4 | Defend Tam (he's injured) | Defeat 3 Corrupted Treants (standard combat) |
| 5 | Discover the Corrupted Crystal | Player interacts with Crystal object at zone centre |
| 6 (Branch A) | Destroy the Crystal | Interact: play animation, -50% Thornwood enemies for 24hr in-game |
| 6 (Branch B) | Leave the Crystal intact | Player exits without destroying — note: Crystal strengthens enemy respawn; available to return later |
| 7 | Return Tam to Elara | Player travels back to Millhaven Inn with Tam (Tam follows as escort NPC) |

---

**Dialogue — Finding Tam:**

> **Tam:** *"You... you came. Mum sent you? I've been pinned here for days. The trees move at night — I've seen them. It's not natural. There's something in the centre of the forest. A crystal, cracked. It's… breathing."*

**Player options:**

- **"Let's get you out of here first."** → Escorts Tam immediately. Player can return for Crystal later.
- **"Show me this crystal first."** → Tam follows to Crystal. Step 5 triggered immediately.

---

**Dialogue — Corrupted Crystal:**

> *The crystal pulses with a sickly green light. Fractured. A low hum emanates from it — you feel it in your back teeth.*
>
> **Interact prompt:** [Destroy the Crystal] / [Leave it]

**Destroy:** → Crystal shatters, burst animation, zone-wide enemy debuff applied. Journal: *"You destroyed the Corrupted Crystal. The Thornwood seems quieter."*

**Leave:** → Journal: *"You left the Crystal intact. Something about it felt… important."* — flags a future quest branch (Act 2 relevance).

---

**Turn-In Dialogue (Elara):**

> **Elara:** *"Tam! Oh, my boy — come here. I thought—"* *(pauses, composes herself)* *"Thank you. I don't have much, but take this. And... whatever you found in that forest. Be careful. The Thornwood doesn't give things up for nothing."*

---

**Rewards:**

| Reward | Value |
|--------|-------|
| XP | 250 XP |
| Gold | 75g |
| Item | Thornwood Cloak (Uncommon — +5 DEX, +10 Stealth) |
| Reputation | Millhaven Standing +100 (Friendly threshold) |
| Unlock | Thornwood Forest now fully accessible on map |

---

**Quest Flags:**

- `tam_rescued = true`
- `crystal_destroyed = true/false` (branch dependent)
- `millhaven_standing += 100`
- Unlocks: `MQ_ACT1_003` (The Crystal's Secret)

---

### 18.3 Side Quest — "Emberstrike" (Frostpeak)

**Quest ID:** `SQ_FROST_001`
**Quest Type:** Side Quest
**Level Range:** 10–13
**Prerequisites:** Level 10; speak to Garrak Stonefist (Dialogue option C)
**Quest Giver:** Garrak Stonefist (Frostpeak Village)
**Turn-in NPC:** Garrak Stonefist

---

**Summary:**
A Rogue guild called the Coldspike Gang has taken up in the old Frostpeak Mine and stolen Garrak's ancestral forge-hammer, Emberstrike. The player must infiltrate the mine, recover the hammer, and return it.

---

**Objectives:**

| Step | Objective | Completion Condition |
|------|-----------|---------------------|
| 1 | Find the Frostpeak Mine entrance | Player enters Mine zone |
| 2 | Locate the Coldspike Gang's camp | Reach inner mine room |
| 3 | Recover Emberstrike | Option A: Steal (Stealth check DC 14) / Option B: Defeat Coldspike Leader in combat |
| 4 | Escape the mine | Exit zone with Emberstrike in inventory |
| 5 | Return Emberstrike to Garrak | Speak to Garrak |

---

**Branch — Stealth (DC 14 DEX check):**
- Success: Player retrieves hammer without combat. No XP from enemies. +Bonus Rogue Faction reputation.
- Failure: Coldspike Gang alerted. All enemies in room aggro. Player must fight or flee.

---

**Branch — Combat:**
- Coldspike Leader: HP 800, AC 15, attacks: Backstab (d8+5 pierce) + Smoke Bomb (AOE blind 2s)
- Defeating Leader causes remaining Rogues to flee.
- Looting Leader's body always yields Emberstrike + bonus: Coldspike Dagger (Rare, 1d8+8 pierce, +5 Stealth)

---

**Turn-In Dialogue:**

> **Garrak:** *"Emberstrike... by the deep forge. You actually got it back. I'd given it up for lost."* *(tests the hammer's weight)* *"Aye. Balance is perfect. My grandfather would be proud. You've earned more than a thank-you — come back any time. And if anyone gives you grief about your steel, send them to me."*

---

**Rewards:**

| Reward | Value |
|--------|-------|
| XP | 600 XP |
| Gold | 200g |
| Item | Stonefist's Favour token (permanent 10% discount at Garrak's shop) |
| Bonus (combat path) | Coldspike Dagger (Rare) |
| Bonus (stealth path) | Shadowstep duration +1s (passive, permanent) |

---

### 18.4 Daily Quest — "The Market Courier" (Millhaven)

**Quest ID:** `DQ_MILL_001`
**Quest Type:** Daily Repeatable
**Level Range:** 1+ (scales)
**Reset:** Daily at 00:00 UTC
**Quest Giver:** Notice Board (Millhaven Town Square)

---

**Summary:**
Deliver 5 packages from the Millhaven Merchant to NPCs around the overworld within 10 minutes (real time). Teaches the overworld layout to new players.

---

**Objectives:**

| Step | Objective |
|------|-----------|
| 1 | Accept packages from Merchant Aldous (Millhaven Market) |
| 2 | Deliver to 5 named NPCs (randomised from pool of 10 each day) |
| 3 | Return to Aldous for reward |

**Delivery NPCs (Pool of 10, 5 selected daily):** Elara Thornwick, Blacksmith Holt, Healer Sister Mara, Guard Captain Renwick, Fisher Neb, Old Farmer Wex, Arcanist Dusk, Stable Master Brynn, Miller Corvin, Priestess Lena

**Time limit:** 10 minutes. Fail: packages returned, quest resets next day. Partial credit: none (all 5 or nothing).

**Rewards (daily, first completion):**
- 50 XP (scales: +10 XP per 5 player levels above 1)
- 25g (scales: +5g per 5 player levels)
- Millhaven Standing +25
- Chance: 1× Common crafting material (random)

---

### 18.5 Quest Engine — Technical Spec for CTO

| Property | Spec |
|----------|------|
| Quest data format | JSON per quest, versioned |
| Objective tracking | Server-side; each step has a `trigger` (zone_enter, kill, interact, item_pickup, escort_complete) |
| Branch outcomes | Stored as flags per player in player state DB |
| NPC escort logic | Pathfinding follower (A* with player as waypoint target); dies = quest fails if critical NPC |
| Stealth checks | Client sends "attempt stealth" → server rolls DEX mod + d20 vs DC → returns result |
| Time-limited quests | Server-side countdown timer, starts on objective step 1; fail event broadcasts to client |
| Daily reset | Cron job resets all DQ completion flags at 00:00 UTC |
| Quest log | Client UI reads from GET /quests/{playerId} — server-authoritative |
| Reward delivery | Atomic: all rewards delivered server-side on turn-in; client notified via event |

---

## 19. Economy Balancing Model

### 19.1 Overview

AETHERMOOR's economy is player-driven within server-authoritative bounds. Gold enters the game through quests, mob drops, and daily activities; it exits through vendor purchases, crafting costs, housing, and repair fees. The goal is a **stable, deflationary-resistant economy** that keeps gold meaningful at all levels without hyperinflation at endgame.

**Design Goals:**
- Gold should feel hard-earned but not scarce
- High-level players should not trivially flood the market
- Players who prefer non-combat paths (fishing, crafting, housing) should be economically viable
- The Auction House should be competitive but not manipulable by a single guild

---

### 19.2 Gold Sources (Inflows)

| Source | Rate | Notes |
|--------|------|-------|
| Quest rewards (Main) | 50–2,000g per quest | Scales with level and difficulty |
| Quest rewards (Daily) | 25–100g per quest | Capped per day per player |
| Monster drops | 1–50g per kill | Common enemies: 1–5g; elites: 10–50g |
| Dungeon completion bonus | 100–2,000g | One-time per dungeon + weekly bonus chest |
| Fishing sales (to vendor) | 6–2,000g per fish | Rare fish retain value via trade |
| Crafting sales (AH) | Variable | Player-set price; AH takes 5% cut |
| World Event participation | 50–500g (bonus chest) | Shared pool, no diminishing returns |
| PvP territory control bonus | 100g/hr per zone held | Faction-shared; distributed equally to online faction members in zone |

**Anti-inflation controls:**
- Daily quest gold is hard-capped (25–100g/day per player)
- Monster gold drops have per-session diminishing returns (-10% per 50 kills, resets after 30min offline)
- Dungeon completion bonus is weekly (not per run)
- PvP territory requires active presence — AFK farming blocked by activity check every 5 min

---

### 19.3 Gold Sinks (Outflows)

| Sink | Cost | Notes |
|------|------|-------|
| Gear repair | 5% item base value | Occurs on death or after 100 uses |
| Vendor-purchased consumables | 2–500g | Trail rations, bait, torches, potions |
| Crafting materials (vendor-sold) | 10–5,000g | Raw mats that can't be foraged |
| Housing plots | 500–50,000g | One-time purchase; highest tier is meaningful grind |
| Housing furniture (vendor) | 50–2,000g per piece | Crafted furniture is cheaper but time-cost |
| Auction House listing fee | 10g flat + 5% sale cut | Listing fee lost if item doesn't sell |
| Fast Travel (inns) | 5g per hop | Local teleport network |
| Respawn gold penalty (PvP) | 50–200g at endgame | Only in PvP zones; not in PvE |
| Guild vault storage upgrade | 1,000–10,000g | Per-tier expansion cost |
| Season Pass (if adopted) | TBD (Board decision) | Could be direct gold purchase at premium conversion |

---

### 19.4 Gold Velocity by Playstyle

| Playstyle | Avg Gold/hr (estimate) | Primary sinks |
|-----------|----------------------|---------------|
| Casual questing (levels 1–10) | 80–150g/hr | Vendor consumables, repairs |
| Dungeon runner (levels 10–20) | 300–600g/hr | Repair costs, AH listings, housing |
| Crafter / fisher (all levels) | 100–400g/hr (AH dependent) | Crafting materials, listing fees |
| PvP player (faction zones) | 200–500g/hr | Respawn penalty, consumables, territory bribes |
| Endgame raider (level 18–20) | 800–1,500g/hr | High-end repairs, consumable stacks, AH flipping |

*Note: These are design targets, not guarantees. CTO should instrument actual gold flows at launch and adjust drop tables/sink costs within ±20% without a GDD revision.*

---

### 19.5 Auction House Design

**How it works:**
- Players list items at any price with a 48-hour expiry
- Listing fee: 10g flat (discarded on fail) + 5% of sale price (taken on success)
- Buyout price optional — without buyout, item goes to highest bidder at expiry
- Search: by item name, tier, item type, level range, price range
- Category tabs: Weapons, Armor, Consumables, Materials, Housing, Cosmetics, Fishing, Misc

**Anti-manipulation rules:**
- Maximum 20 active listings per player at any time
- Minimum listing price = vendor sell price (prevents undercutting to zero)
- Price history shown (7-day average) to prevent uninformed panic selling
- Shill bidding prevention: player cannot bid on their own listings (server-enforced)

**Mobile AH UI:**
- Category tabs → scrollable list → tap item → detail sheet → Buy/Bid button
- Sell: tap item in inventory → Sell on AH → price field → confirm
- Notifications: AH sale/expiry delivered as in-game mail

---

### 19.6 Player-to-Player Trade

- Direct trade: Face-to-face trade window (tap other player → Trade)
- Trade window: both players add items + gold → both confirm → atomic swap server-side
- No mail-based trade to reduce scam risk for new players
- Guild bank: shared storage, permission tiers (View / Deposit / Withdraw)

---

### 19.7 Inflation Watchpoints & Tuning Levers

If gold inflation is detected (defined as: median AH price of Uncommon gear rising >20% month-over-month), the following levers are available without a content update:

| Lever | Direction | Effect |
|-------|-----------|--------|
| Monster drop rate | Reduce | Less gold per kill |
| Daily quest gold reward | Reduce | Less daily inflow |
| Repair cost multiplier | Increase | More sink |
| AH listing fee | Increase | More friction for high-volume traders |
| Housing plot price | Increase | Larger sink for late-game gold |
| Introduce new gold sink (e.g., cosmetic gacha, lore scrolls) | New sink | Absorb excess gold |

*CTO note: All these values should be live-configurable from the admin panel without a deployment.*

---

### 19.8 MMO Considerations

- Economy is per-shard — no cross-shard AH (prevents server economy collapse)
- If shards merge in future, AH histories should be merged carefully (CEO approval required)
- Bot detection: flag accounts with >2x median gold/hr for manual review
- Gold-per-session cap: no hard cap, but diminishing returns on monster drops (see §19.2)
- Season resets: gold is NOT wiped at season end — only cosmetic progression resets. Economy continuity is a player trust issue.

---

## 20. Open Questions / Decisions Pending

| # | Question | Owner | Status |
|---|----------|-------|--------|
| 1 | ~~Engine Choice~~ | CEO | **RESOLVED: Phaser.js** |
| 2 | Monetization model / season pass price | Board | Escalated — placeholder $9.99/season |
| 3 | Mobile delivery wrapper: Capacitor vs. Cordova vs. custom | CTO | Open |
| 4 | Backend language/framework preference | CTO | Open — TypeScript/Node.js suggested |
| 5 | CDN provider selection | CTO | Open |
| 6 | ~~Fishing mechanic (Sunken Docks)~~ | Game Designer | **RESOLVED: v0.4** |
| 7 | Housing plot cap per server | CTO | Open — needs capacity planning |
| 8 | World PvP anti-griefing: 5-level bracket vs. gear-score bracket | CEO/GD | Open |
| 9 | Season length: 90 days vs. 60 days | CEO | Open |
| 10 | Economy gold inflow targets: approved or adjust? | CEO | New — please review §19.4 targets |
| 11 | AH cross-shard policy at scale | CEO | New — escalated from §19.8 |
| 12 | Dialogue localisation languages at launch | CEO | New — how many locales at launch? |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v0.1 | 2026-04-13 | Game Designer | Initial draft: core loop, world, classes overview, combat, progression, MMO systems, UI/UX, technical spec |
| v0.2 | 2026-04-13 | Game Designer | Added: Crafting System, PvP Factions, World Lore & History, Seasonal Content |
| v0.3 | 2026-04-14 | Game Designer | Added: Full Class Ability Trees (all 6 classes, all subclasses), Housing System, Dungeon Bestiary (15 dungeons). Confirmed Phaser.js engine. |
| v0.4 | 2026-04-14 | Game Designer | Added: Fishing Mechanic (Sec 16), NPC Dialogue Trees — Elara Thornwick & Garrak Stonefist (Sec 17), Quest Scripts — Main/Side/Daily with engine spec (Sec 18), Economy Balancing Model with gold inflows/sinks/AH design (Sec 19). Updated Open Questions (Sec 20). |
| v0.5 | 2026-04-16 | Game Designer | Added: Full Crafting System Design (docs/game-design/crafting/crafting-system.md) — six professions, gathering, crafting workflow, quality system, economy integration, API endpoints. Added subsystem cross-reference table. Updated Section 8. |
| v0.6 | 2026-04-16 | Game Designer | Updated Crafting System with CEO design decisions: BOE (bind-on-equip), visible exceptional chance (15% at Master+), Grand Master quality guarantee (100% exceptional at L20). Updated crafting quick reference in Section 8. |

