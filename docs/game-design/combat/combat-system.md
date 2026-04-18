# Combat Design Specification — Project AETHERMOOR
**Document Key:** `combat-spec`
**Issue:** [RPGAA-14](/RPGAA/issues/RPGAA-14)
**Version:** 1.0
**Date:** 2026-04-14
**Author:** Game Designer

---

## Overview

This document is the complete Combat Design Specification for Project AETHERMOOR. It defines every rule, number, and mechanic the CTO needs to implement the Combat Service. The system uses a **real-time-with-turns hybrid model** inspired by D&D 5e, adapted for a persistent 2D top-down MMO. Every die roll matters — the D&D design pillar — is preserved throughout.

---

## Design Goals

| Goal | Description |
|---|---|
| Meaningful dice | Every attack roll and saving throw creates genuine tension |
| Real-time feel | Players move freely; actions resolve in structured turns |
| MMO-scalable | Group combat, aggro, and loot rules work for 2–5 players |
| Mobile-first | All combat can be played via tap/touch with no precision penalty |
| Approachable depth | New players can fight; veterans can optimise |

---

## 1. Combat Model

### 1.1 Real-Time with Turn-Based Action Resolution

AETHERMOOR uses a hybrid model:

- **Movement** is real-time and continuous. Players move freely on the Phaser.js canvas at any time.
- **Actions** (attacks, spells, abilities) are locked to a **combat round** of **6 seconds** (matching D&D 5e).
- When a player spends an Action in combat, their action cooldown begins. They cannot use another Action until the 6-second round elapses.
- Bonus Actions and Reactions have their own independent 6-second cooldown.

**Visual Metaphor for Players:** The hotbar shows a circular cooldown ring over each action slot that fills over 6 seconds.

### 1.2 Turn/Tick Rate

| Parameter | Value |
|---|---|
| Round duration | 6 seconds (real-time) |
| Server combat tick | 100ms (10 ticks/second) |
| Action resolution | Processed server-side at end of the tick in which the action was submitted |
| Movement update | Sent from client every 50ms; server validates position on each tick |

### 1.3 Initiative System

Initiative determines resolution order when multiple actions are submitted within the same server tick.

**Initiative Roll:** `d20 + DEX modifier`

- Calculated once when combat begins (first hostile action or first attack received).
- Cached for the duration of the combat encounter.
- Ties broken by: higher DEX modifier → then higher raw initiative roll → then coin flip (random server-side).

**Server queue logic:**
1. Collect all actions submitted in the current 100ms tick.
2. Sort by initiative (descending).
3. Resolve in order, re-checking validity (e.g. target dead, out of range) before each.
4. Broadcast results to all clients.

### 1.4 Action Economy

AETHERMOOR implements all three D&D action types, simplified for MMO use:

| Type | Per Round | Resets |
|---|---|---|
| **Action** | 1 | Every 6 seconds |
| **Bonus Action** | 1 | Every 6 seconds |
| **Reaction** | 1 | Every 6 seconds (auto-triggered or manual) |

- **Action:** Attack, cast a levelled spell, use an item, dash (doubles movement for the round), disengage, help.
- **Bonus Action:** Off-hand attack (light weapons), cast a bonus-action spell, activate a class ability.
- **Reaction:** Opportunity attack (triggered automatically when an enemy leaves melee range), Shield spell (Wizard), Sentinel feat strike.

**Simplification for mobile:** Reactions can be set to Auto (server resolves automatically) or Manual (player taps a prompt within a 2-second window before auto-resolving).

### 1.5 Movement Speed

Movement is continuous, not tile-counted per round. Speed governs maximum distance per round for rules purposes (opportunity attacks, dash).

| Base Speed | Value |
|---|---|
| Default (all classes) | 30 tiles per round (5 tiles/second) |
| DEX modifier bonus | +1 tile/round per +1 DEX mod (max +5) |
| Heavy armour penalty | −5 tiles/round if STR < 15 |

**1 tile = 1 in-game metre = 5 ft (D&D standard)**

Classes and their speed modifiers:

| Class | Speed |
|---|---|
| Warrior | 30 tiles/round |
| Rogue | 35 tiles/round |
| Ranger | 35 tiles/round |
| Mage | 30 tiles/round |
| Cleric | 30 tiles/round |

---

## 2. Attack Resolution

### 2.1 Attack Roll

**Formula:** `d20 + Attack Bonus ≥ Target AC → Hit`

**Attack Bonus = Ability Modifier + Proficiency Bonus**

| Level | Proficiency Bonus |
|---|---|
| 1–4 | +2 |
| 5–8 | +3 |
| 9–12 | +4 |
| 13–16 | +5 |
| 17–20 | +6 |

### 2.2 Ability Modifiers by Attack Type

| Attack Type | Key Ability | Classes |
|---|---|---|
| Melee weapon | STR modifier | Warrior |
| Finesse melee (choose higher) | STR or DEX | Rogue |
| Ranged weapon | DEX modifier | Ranger |
| Spell attack | INT modifier | Mage |
| Spell attack | WIS modifier | Cleric |
| Spell attack | CHA modifier | Paladin |

**Ability Modifier Table:**

| Score | Modifier |
|---|---|
| 1 | −5 |
| 2–3 | −4 |
| 4–5 | −3 |
| 6–7 | −2 |
| 8–9 | −1 |
| 10–11 | 0 |
| 12–13 | +1 |
| 14–15 | +2 |
| 16–17 | +3 |
| 18–19 | +4 |
| 20–21 | +5 |
| 22+ | +6 |

### 2.3 Advantage and Disadvantage

- **Advantage:** Roll `2d20`, take the higher result.
- **Disadvantage:** Roll `2d20`, take the lower result.
- Advantage and disadvantage cancel each other out regardless of sources.
- Multiple sources of advantage do not stack beyond a single extra die.

**Common sources:**

| Source | Effect |
|---|---|
| Blinded attacker | Disadvantage on attacks |
| Blinded target | Advantage on attacks vs. them |
| Rogue Sneak Attack eligible | Advantage if flanking |
| Prone target (melee) | Advantage |
| Prone target (ranged) | Disadvantage |
| Charmed attacker (vs. charmer) | Disadvantage |

### 2.4 Critical Hit and Critical Miss

| Roll | Effect |
|---|---|
| **Natural 20** | Critical Hit: roll all damage dice **twice**, add modifiers once |
| **Natural 1** | Critical Miss: attack automatically misses; attacker takes no damage but loses the action |

Critical Hit visual: screen flash gold, special particle emitter on target, floating "CRIT!" text in orange.
Critical Miss visual: weapon fumble animation, floating "MISS!" in grey.

### 2.5 Miss Mechanics

AETHERMOOR uses **full miss** (no partial damage on a miss). Design rationale: partial damage muddies the tension of the attack roll and undercuts the D&D pillar of "every roll matters."

**Exception:** The Ranger's `Glancing Shot` ability allows them to deal DEX modifier damage on a miss (class-specific feat at level 5).

---

## 3. Damage and Healing

### 3.1 Damage Dice by Weapon Type

| Weapon | Damage Die | Properties |
|---|---|---|
| Dagger | d4 | Light, Finesse, Thrown (20/60 ft) |
| Shortsword | d6 | Light, Finesse |
| Longsword | d8 (d10 two-handed) | Versatile |
| Greataxe | d12 | Heavy, Two-Handed |
| Handaxe | d6 | Light, Thrown (20/60 ft) |
| Greatclub | d8 | Heavy, Two-Handed |
| Quarterstaff | d6 (d8 two-handed) | Versatile |
| Longbow | d8 | Ranged (150/600 ft), Two-Handed |
| Shortbow | d6 | Ranged (80/320 ft), Two-Handed |
| Hand Crossbow | d6 | Ranged (30/120 ft), Light |
| Staff (arcane) | d6 | Versatile, +1 spell DC |

### 3.2 Ability Modifier to Damage

On a hit, add the key ability modifier (same as attack) to the damage roll. Minimum 1 damage per hit.

**Example:** Warrior with STR 18 (+4), hits with a Longsword (d8). Rolls 5. Total damage = 5 + 4 = **9**.

### 3.3 Damage Types

| Category | Types |
|---|---|
| Physical | Slashing, Piercing, Bludgeoning |
| Elemental | Fire, Cold, Lightning, Thunder, Acid, Poison |
| Arcane | Force, Psychic |
| Divine | Radiant, Necrotic |

### 3.4 Resistances, Vulnerabilities, Immunities

| Status | Effect |
|---|---|
| **Resistance** | Damage from that type halved (round down, minimum 1) |
| **Vulnerability** | Damage from that type doubled |
| **Immunity** | Damage from that type reduced to 0 |

Resistances stack only from different sources (equipment + condition). Two resistances of the same type do not stack to immunity.

### 3.5 Healing

| Source | Formula |
|---|---|
| Cure Wounds (Cleric, lv1) | 1d8 + WIS modifier |
| Mass Cure Wounds (Cleric, lv5) | 3d8 + WIS modifier (all party members in range) |
| Healing Word (Bonus Action) | 1d4 + WIS modifier |
| Minor Healing Potion | Restores 2d4 + 2 HP |
| Standard Healing Potion | Restores 4d4 + 4 HP |
| Greater Healing Potion | Restores 8d4 + 8 HP |
| Natural Regeneration | +1 HP per 10 seconds out of combat |

**Out-of-combat** is defined as: no hostile entity has attacked the player or been attacked by the player in the last 15 seconds.

---

## 4. Spell System

### 4.1 Spell Slots by Class and Level

Spellcasting classes: **Mage**, **Cleric**, **Paladin** (half-caster).

**Full Casters (Mage, Cleric) — Spell Slots:**

| Level | 1st | 2nd | 3rd | 4th | 5th |
|---|---|---|---|---|---|
| 1 | 2 | — | — | — | — |
| 2 | 3 | — | — | — | — |
| 3 | 4 | 2 | — | — | — |
| 4 | 4 | 3 | — | — | — |
| 5 | 4 | 3 | 2 | — | — |
| 6 | 4 | 3 | 3 | — | — |
| 7 | 4 | 3 | 3 | 1 | — |
| 8 | 4 | 3 | 3 | 2 | — |
| 9 | 4 | 3 | 3 | 3 | 1 |
| 10 | 4 | 3 | 3 | 3 | 2 |

**Half Caster (Paladin) — Spell Slots:**

| Level | 1st | 2nd | 3rd |
|---|---|---|---|
| 1 | — | — | — |
| 2 | 2 | — | — |
| 3 | 3 | — | — |
| 4 | 3 | — | — |
| 5 | 4 | 2 | — |
| 6 | 4 | 2 | — |
| 7 | 4 | 3 | — |
| 8 | 4 | 3 | — |
| 9 | 4 | 3 | 2 |
| 10 | 4 | 3 | 2 |

**Spell Slot Recovery:** Full recovery on a **Long Rest** (8 hours offline or at an Inn). Short Rest (5 minutes, not in combat) restores 0 slots for Mage/Paladin; Cleric recovers 2 slots of any level on Short Rest (Channel Divinity perk).

### 4.2 Concentration Mechanic

Some spells require Concentration (marked **[C]** in spell list). Rules:

- Only one Concentration spell can be active at a time.
- Starting a new [C] spell ends the previous one immediately.
- When a concentrating player takes damage, they make a **Constitution Saving Throw**: DC = max(10, half damage taken). Fail → spell ends.
- Constitution Save: `d20 + CON modifier ≥ DC`.

### 4.3 Spell Targeting Modes

| Mode | Description | Render (Phaser.js) |
|---|---|---|
| **Single Target** | One entity within range | Highlight ring on target entity |
| **AoE — Circle** | Radius in tiles, centred on point | Translucent circle overlay on canvas, confirm on release |
| **AoE — Cone** | 15-tile cone in facing direction | Translucent pie-slice from caster; rotates with mouse/joystick |
| **Line** | 1-tile wide, N tiles long | Translucent line from caster to max range |
| **Self** | Affects caster only | Instant, no targeting |

**Mobile targeting:** Tap+hold reveals the targeting reticle; drag to aim; release to cast.

### 4.4 Cantrips vs Levelled Spells

- **Cantrips:** Always available, no slot cost, scale with character level.
  - Mage damage cantrip (Firebolt): `1d10 fire` at levels 1–4, `2d10` at 5–10.
  - Cleric cantrip (Sacred Flame): `1d8 radiant`, DEX save or take damage.
- **Levelled spells:** Require a slot. Casting at a higher slot tier (upcast) increases effect (damage dice, targets, duration) per spell definition.

### 4.5 Sample Spells — Mage

| Name | Level | Action | Range | Target | Effect | Slot |
|---|---|---|---|---|---|---|
| Firebolt | Cantrip | Action | 120 ft | Single | 1d10 fire damage | — |
| Magic Missile | 1st | Action | 120 ft | Up to 3 single | 3× (1d4+1) force, auto-hit | 1st |
| Burning Hands | 1st | Action | 15 ft | Cone | 3d6 fire, DEX save halves | 1st |
| Misty Step | 2nd | Bonus | Self | Self | Teleport up to 30 ft to visible point | 2nd |
| Fireball | 3rd | Action | 150 ft | AoE 20ft radius | 8d6 fire, DEX save halves | 3rd |
| Counterspell | 3rd | Reaction | 60 ft | Single spell | Interrupt enemy spell (DC 10 + spell level) | 3rd |
| Wall of Fire | 4th | Action | 120 ft | Line (60ft) | 5d8 fire/round for 1 min [C] | 4th |
| Cone of Cold | 5th | Action | 60 ft | Cone | 8d8 cold, CON save halves | 5th |

### 4.6 Sample Spells — Cleric

| Name | Level | Action | Range | Target | Effect | Slot |
|---|---|---|---|---|---|---|
| Sacred Flame | Cantrip | Action | 60 ft | Single | 1d8 radiant, DEX save or hit | — |
| Cure Wounds | 1st | Action | Touch | Single | 1d8 + WIS HP restored | 1st |
| Bless | 1st | Action | 30 ft | Up to 3 allies | +1d4 to attack rolls & saves for 1 min [C] | 1st |
| Healing Word | 1st | Bonus | 60 ft | Single | 1d4 + WIS HP restored | 1st |
| Spiritual Weapon | 2nd | Bonus | 60 ft | AoE single/round | 1d8 + WIS force, moves each bonus | 2nd |
| Spirit Guardians | 3rd | Action | Self | 15 ft radius | 3d8 radiant/round in aura [C] | 3rd |
| Mass Cure Wounds | 5th | Action | 60 ft | Up to 6 in range | 3d8 + WIS HP each | 5th |

### 4.7 Sample Spells — Paladin

| Name | Level | Action | Range | Target | Effect | Slot |
|---|---|---|---|---|---|---|
| Divine Smite | 1st | Bonus (on hit) | Touch | Single | +2d8 radiant (extra 1d8 per slot above 1st) | 1st+ |
| Thunderous Smite | 1st | Bonus (on hit) | Touch | Single | +2d6 thunder; STR save or knocked back 10 ft | 1st |
| Wrathful Smite | 1st | Bonus (on hit) | Touch | Single | +1d6 psychic; WIS save or frightened [C] | 1st |
| Shield of Faith | 1st | Bonus | 60 ft | Single | +2 AC for 10 min [C] | 1st |
| Lay on Hands | — | Action | Touch | Single | Pool of 5× level HP, spend any amount | — |
| Aura of Protection | — | Passive | 10 ft | All allies | +CHA mod to all saving throws | — |

---

## 5. Conditions

### 5.1 Condition Reference Table

| Condition | Source | Effect | Duration | Stacking | Visual HUD |
|---|---|---|---|---|---|
| **Stunned** | Stun Strike, certain spells | Incapacitated; can't move or act; all attacks vs. them have advantage | 1 round | Does not stack | Gold stars icon + character flickers |
| **Poisoned** | Poison attacks, Bites | Disadvantage on attack rolls and ability checks | Until cured or 30s | Stacks duration (max 60s) | Green droplet icon |
| **Bleeding** | Slash crits, Bleed abilities | −1d4 HP per 6 seconds | Until bandaged or healed | Stacks to 3× (each +1d4) | Red droplet icon |
| **Burning** | Fire spells, Flaming weapons | 1d6 fire damage per 6 seconds | Until extinguished or 18s | Does not stack; refreshes duration | Flame icon |
| **Frozen** | Cold spells (e.g. Ice Storm) | Speed halved; next hit deals +1d6 cold | Until dispelled or 12s | Does not stack | Ice shard icon, character tinted blue |
| **Charmed** | Charm Person, certain enemies | Cannot attack charmer; CHA checks vs. charmer have disadvantage | Until charmer attacks them or 60s | Does not stack | Heart icon |
| **Frightened** | Wrathful Smite, Fear spells | Disadvantage on attacks while source is visible; can't voluntarily move closer | Until source leaves sight or 30s | Does not stack | Skull icon, character trembles |
| **Blinded** | Blindness/Deafness spell, Sand Attack | Attacks have disadvantage; attacks vs. blinded have advantage | Until cured or 18s | Does not stack | Eye-slash icon |
| **Exhausted** | Extended combat without rest | −2 to all attack rolls and ability checks per stack | Until rest | Stacks up to 5× | Zzz icon + greyed portrait |

### 5.2 Condition Application

- Conditions are applied server-side on the tick the triggering hit resolves.
- Multiple conditions from different sources are independent and do not cancel each other.
- Dispel Magic (Mage 3rd level) removes all magical conditions from a single target.
- Lesser Restoration (Cleric 2nd level) removes one condition of the caster's choice.

### 5.3 HUD Visual Indicators

- Condition icons appear in a row below the player's HP bar (mobile: scrollable icon strip).
- Hovering/tapping an icon shows the name, effect, and remaining duration.
- Conditions with stacking values show a numeric badge (e.g. Bleeding ×3).

---

## 6. Enemy Design

### 6.1 Enemy Stat Block Format

```
[Enemy Name]
Tier: Early / Mid / Late
Biome: Forest / Desert / Mountain / Swamp / Dungeon
HP: [value]     AC: [value]     Speed: [tiles/round]
Attack Bonus: +[value]
Damage: [dice] [type]
STR / DEX / CON / INT / WIS / CHA: [modifiers]
Saving Throws: [list]
Resistances: [list or None]
Abilities:
  - [Ability Name]: [Description]
XP Reward: [value]
Loot Table: [table reference]
```

### 6.2 Sample Enemy Stat Blocks — Early Game (Forest Biome)

**Giant Rat**
> Tier: Early | Biome: Forest
> HP: 12 | AC: 11 | Speed: 25 tiles/round
> Attack Bonus: +3 | Damage: 1d4+1 Piercing
> STR −1 / DEX +1 / CON +0 / INT −4 / WIS −1 / CHA −3
> Abilities: Pack Tactics — advantage on attacks when an ally is adjacent
> XP: 10

**Goblin Scout**
> Tier: Early | Biome: Forest
> HP: 18 | AC: 13 | Speed: 30 tiles/round
> Attack Bonus: +4 | Damage: 1d6+2 Piercing (shortbow, 80ft range)
> STR −1 / DEX +2 / CON +0 / INT −1 / WIS −1 / CHA −1
> Abilities: Nimble Escape — can Disengage as Bonus Action
> XP: 25

**Forest Bandit**
> Tier: Early | Biome: Forest
> HP: 22 | AC: 14 | Speed: 30 tiles/round
> Attack Bonus: +3 | Damage: 1d6+1 Slashing (shortsword)
> STR +0 / DEX +1 / CON +0 / INT −1 / WIS +0 / CHA −1
> XP: 35

**Thorn Sprite**
> Tier: Early | Biome: Forest
> HP: 14 | AC: 12 | Speed: 20 tiles/round (flight)
> Attack Bonus: +3 | Damage: 1d4 Piercing + Poison (CON save DC 11 or Poisoned 18s)
> DEX +2 / others low
> Abilities: Hovering — immune to ground effects
> XP: 30

**Skeleton Archer**
> Tier: Early | Biome: Dungeon
> HP: 20 | AC: 13 | Speed: 25 tiles/round
> Attack Bonus: +4 | Damage: 1d6+2 Piercing (shortbow)
> Resistances: Piercing, Slashing (half damage) | Immunities: Poison, Necrotic
> XP: 40

### 6.3 Sample Enemy Stat Blocks — Mid Game (Mountain/Swamp Biome)

**Stone Golem**
> Tier: Mid | Biome: Mountain
> HP: 85 | AC: 17 | Speed: 20 tiles/round
> Attack Bonus: +7 | Damage: 2d10+5 Bludgeoning
> STR +5 / CON +4 / others low
> Immunities: Poison, Psychic | Resistances: Non-magical Physical
> Abilities: Slow — AoE debuff on attack; reduces speed of all in 15ft radius by half for 1 round
> XP: 250

**Swamp Troll**
> Tier: Mid | Biome: Swamp
> HP: 70 | AC: 15 | Speed: 30 tiles/round
> Attack Bonus: +6 | Damage: 2d6+4 Slashing (claws, two attacks per Action)
> STR +4 / CON +3
> Abilities: Regeneration — recovers 5 HP per 6 seconds (negated by Fire or Acid damage that round)
> XP: 200

**Marsh Witch**
> Tier: Mid | Biome: Swamp
> HP: 48 | AC: 14 | Speed: 25 tiles/round
> Spell Attack: +5 | Damage: 2d8+3 Necrotic (ranged 60ft)
> Abilities: Hex — applies Frightened on hit (WIS save DC 13); Blink — short-range teleport reaction when hit
> XP: 175

**Desert Wyvern (young)**
> Tier: Mid | Biome: Desert
> HP: 95 | AC: 16 | Speed: 35 tiles/round (flight)
> Attack Bonus: +8 | Damage: 2d8+5 Piercing (bite) + 2d6 Poison (tail sting, CON save DC 13)
> XP: 350

**Mountain Ogre**
> Tier: Mid | Biome: Mountain
> HP: 80 | AC: 15 | Speed: 30 tiles/round
> Attack Bonus: +6 | Damage: 2d8+5 Bludgeoning
> STR +5 / CON +3
> Abilities: Knock Down — on natural 18+ attack roll, target must STR save DC 14 or fall prone
> XP: 220

### 6.4 Sample Enemy Stat Blocks — Late Game (Dungeon Endgame)

**Lich Acolyte**
> Tier: Late | Biome: Dungeon
> HP: 130 | AC: 18 | Speed: 25 tiles/round
> Spell Attack: +9 | Damage: 3d8+5 Necrotic or 4d6 Fire (alternates)
> Immunities: Poison, Necrotic | Resistances: Cold, Lightning
> Abilities: Raise Dead — on death, rises once after 10s with 30 HP unless targeted by Radiant damage before revival
> XP: 800

**Shadow Drake**
> Tier: Late | Biome: Dungeon
> HP: 150 | AC: 17 | Speed: 40 tiles/round (flight)
> Attack Bonus: +10 | Damage: 3d8+6 Cold (breath weapon, 30ft cone, recharge 5–6 on d6)
> Resistances: Physical | Immunities: Cold
> Abilities: Shadow Step — can teleport between areas of darkness (Dungeon mechanic)
> XP: 1,000

**Voidwalker Assassin**
> Tier: Late | Biome: Dungeon
> HP: 110 | AC: 18 | Speed: 40 tiles/round
> Attack Bonus: +11 | Damage: 3d6+6 Piercing + 2d6 Psychic (sneak)
> Abilities: Phase Shift — 20% chance to become incorporeal for 1 round (immune to Physical), then re-solidify; Backstab — always has Sneak Attack bonus in first round
> XP: 900

**Elder Earth Elemental**
> Tier: Late | Biome: Mountain/Dungeon
> HP: 200 | AC: 20 | Speed: 20 tiles/round
> Attack Bonus: +10 | Damage: 3d10+7 Bludgeoning (slam), two attacks per Action
> Immunities: Poison, Psychic, Lightning | Resistances: Non-magical Physical
> Abilities: Tremor — AoE ground shake, DEX save DC 16 or prone; Stone Form — can reduce to AC 25 but Speed 0 for 1 round
> XP: 1,500

**Spectral Knight**
> Tier: Late | Biome: Dungeon
> HP: 140 | AC: 19 | Speed: 30 tiles/round
> Attack Bonus: +10 | Damage: 2d10+6 Necrotic (spectral sword)
> Immunities: Necrotic, Poison | Resistances: Physical (non-magical), Cold
> Abilities: Life Drain — on hit, target's HP max is reduced by damage dealt (restored on Long Rest); Ethereal Jaunt — move through walls once per round
> XP: 1,200

### 6.5 Boss Mechanics

Bosses have three universal traits plus unique per-boss mechanics:

| Trait | Rule |
|---|---|
| **Legendary Resistance** | 3×/day, when a boss fails a saving throw, it can choose to succeed instead |
| **Legendary Actions** | Boss takes 2 extra actions at end of other players' turns |
| **Phase Transitions** | At 75%, 50%, and 25% HP, boss enters next phase (new abilities, visual change) |
| **Enrage Timer** | If combat exceeds 8 minutes, boss enters Enrage: +50% damage, immunity to conditions |

**Sample Boss — The Rot Lord of Vaelmoss Dungeon:**

> HP: 600 (Phase 1: 600→450, Phase 2: 449→225, Phase 3: 224→0)
> AC: 18 | Speed: 25 tiles/round
> **Phase 1:** Basic attacks, Poison AoE (3d6 every 10s), spawns 4 Skeleton Archers
> **Phase 2 (at 75% HP):** Gains Regrowth (heals 15 HP per 6s); Plague Aura (10ft necrotic, 1d8/round)
> **Phase 3 (at 50% HP):** Regrowth accelerates to 25 HP/6s; Summons 2 Marsh Witches; casting Finger of Death on highest-HP target (8d8+3 necrotic, CON save DC 18 for half)
> **Enrage:** Attacks twice per Action; Plague Aura becomes 2d8/round
> XP: 5,000 | Loot: Boss-tier table (guaranteed rare drop)

### 6.6 Aggro System (MMO Groups)

Aggro determines which player an enemy attacks. The server maintains a **threat table** per enemy.

| Action | Threat Generated |
|---|---|
| Damage dealt | 1 threat per 1 HP damage |
| Healing done (ally in combat) | 0.5 threat per 1 HP healed |
| Taunt ability (Warrior) | Sets Warrior to top of threat table + 20 flat |
| AoE damage | Split equally among targets hit |
| Entering combat first | +10 flat threat |

- Enemy attacks the **highest-threat player** within movement range.
- If highest-threat target is unreachable, enemy moves toward them or attacks second-highest.
- Enemy re-evaluates threat every 600ms (server-side).

---

## 7. Group Combat (MMO)

### 7.1 Party Size

Maximum party size: **5 players**. Design rationale: standard D&D table size; manageable for UI and server load.

### 7.2 Threat/Aggro in Groups

Each enemy maintains its own threat table (Section 6.6). Party roles:

| Role | Primary Function | Class |
|---|---|---|
| Tank | High threat generation, absorb hits | Warrior (Defender spec) |
| Healer | Healing generates threat; avoid overthreat | Cleric |
| DPS (Melee) | Burst damage on threat-settled targets | Rogue, Warrior (DPS spec) |
| DPS (Ranged) | Consistent damage from distance | Ranger |
| Support/DPS | Mix of damage and utility | Mage, Paladin |

### 7.3 Friendly Fire Rules

| Zone Type | Friendly Fire |
|---|---|
| PvE Zone | **Off** — AoE spells and attacks cannot damage party members |
| PvP Contested Zone | **On** — Full friendly fire; positioning matters |
| Dungeon (instanced) | **Off** by default; server flag can enable for Hardcore mode |

### 7.4 Loot Distribution

| Mode | Rule |
|---|---|
| **Need/Greed/Pass** (default) | Item dropped into party loot window; each player votes; Need > Greed; ties broken by random roll |
| **Round Robin** | Items distributed in order around the party |
| **Free for All** | First player to tap/click the drop gets it (PvP contested zones) |

- Party loot window stays open for 30 seconds per item; unclaimed items go to highest-threat player.
- Gold is split automatically and equally among party members present when the kill occurs.
- XP is split equally (no penalty for group XP in AETHERMOOR — design decision to encourage grouping).

---

## 8. PvP Combat

### 8.1 PvP vs PvE Differences

| Parameter | PvE | PvP |
|---|---|---|
| Healing received | 100% | 50% (anti-sustain balance) |
| CC duration | Full | Half (Stunned 1s max in PvP) |
| Friendly fire | Off | On |
| Revive | 30 seconds, self-revive possible | 60 seconds; cannot self-revive while in combat |

### 8.2 Anti-Griefing Rules (5-Level Bracket)

As decided by the CEO: players may only attack players within **5 levels** of their own level in contested PvP zones.

- Level check is computed server-side at the time of attack initiation.
- Attacking an out-of-bracket player in a PvP zone shows an error: "Target is too far above/below your level."
- **Exception:** If an out-of-bracket player attacks you first, you are granted a 30-second "retaliation window" during which you may attack them regardless of bracket.

### 8.3 PvP Flagging System

Players must **opt into PvP** by entering a Contested Zone. Contested Zones are marked on the map with a red border.

| Trigger | PvP Status |
|---|---|
| Entering a Contested Zone | PvP-flagged (visual: red aura on character) |
| Exiting a Contested Zone | 15-second grace period, then unflagged |
| Attacking a flagged player (anywhere) | Attacker becomes flagged for 5 minutes |
| Being attacked | Not auto-flagged unless in Contested Zone |

Guards in safe towns attack PvP-flagged players on sight.

### 8.4 Death Penalty in PvP

On death in a PvP encounter:

| Penalty | Value |
|---|---|
| Gold dropped | 5% of carried gold (not banked gold) |
| Durability loss | 10% durability on all equipped items |
| Item drop | None (items are safe) |
| XP loss | None |
| Respawn | At nearest Waystone (10s revive timer) |

Gold dropped by the victim can be looted by the killer within 60 seconds; after that it disappears.

---

## 9. Combat UI

### 9.1 Damage Numbers

- Floating numbers appear at the point of impact, drift upward, fade over 1.2 seconds.
- Font size scales with damage amount (small: <20, medium: 20–99, large: 100+).

| Damage Type | Colour |
|---|---|
| Physical | White |
| Fire | Orange |
| Cold | Cyan |
| Lightning | Yellow |
| Necrotic | Purple |
| Radiant | Gold |
| Healing | Green |
| Critical Hit | Oversized, orange with glow |
| Miss | Grey, "MISS" |

### 9.2 Cooldown Indicators (Hotbar)

- Each ability slot on the hotbar displays a circular radial-fill animation over the icon.
- Fill completes when ability is ready (6-second default).
- Colour states: Ready (normal), On Cooldown (dark overlay + timer in seconds), Out of Resources (red tint).
- Mobile: hotbar is at bottom of screen, 6 slots, each 72×72px touch target.

### 9.3 Threat/Aggro Indicator (Tank)

- Warriors using Defender spec see a small coloured ring around each nearby enemy:
  - **Green ring** = enemy is targeting this Warrior (aggro held).
  - **Yellow ring** = aggro at risk (enemy at 80%+ threat from another player).
  - **Red ring** = enemy is targeting another party member.

### 9.4 Party Frames

- Top-left panel (mobile: collapsible) showing up to 5 party member frames.
- Each frame: Player name, class icon, HP bar (colour-coded by class), Mana/Stamina bar.
- Clicking/tapping a frame targets that player (for healing).
- Condition icons appear below each frame (max 4 visible before scrolling).

### 9.5 Enemy Health Bar

| Enemy Type | Health Bar Location |
|---|---|
| Standard enemy | Floating above head, 60px wide, shrinks with HP |
| Elite enemy | Larger bar (90px) with yellow border |
| Boss | Dedicated boss bar at top of screen, full-width, with phase markers |

Boss bar shows:
- Phase threshold markers (lines at 75%, 50%, 25%)
- Boss name and current HP/max HP
- Enrage timer countdown (last 60 seconds)
- Phase name label (e.g. "Phase 2 — Plague Form")

---

## 10. Technical Notes for CTO

### 10.1 Server Authority Model

AETHERMOOR uses a **server-authoritative** architecture for all combat.

| Aspect | Client | Server |
|---|---|---|
| Movement position | Predicted (client moves immediately) | Validated and corrected on next tick |
| Attack initiation | Sends action intent with timestamp | Validates range, cooldown, resources; rolls dice; broadcasts result |
| Damage calculation | Never computed client-side | Always server-side; client receives final HP values |
| Condition application | Receives and renders only | Applied and tracked server-side |
| Spell casting | Client shows cast animation | Server resolves targets, checks spell slots, deducts, broadcasts |

**Client-side prediction for movement:** Client moves player immediately on input; server sends authoritative position corrections if desync detected (>3 tile divergence). Smooth correction interpolation over 200ms.

### 10.2 Combat Tick Architecture

**Recommended architecture: Event Queue + Per-Tick Resolution**

```
[Client] → WebSocket → [Action Queue] → [Combat Tick Processor (100ms)]
                                                ↓
                              Sort by Initiative → Resolve in order
                                                ↓
                              Broadcast state delta to all zone clients
```

- Each combat zone maintains its own event queue.
- Each queue is processed on a 100ms tick.
- Actions submitted between ticks are queued (with server timestamp for ordering).
- State delta is a compact JSON diff: only changed HP values, condition lists, and position corrections.
- Do not send full world state every tick — only dirty fields.

**Suggested data structures:**
- `CombatEntity`: HP, maxHP, AC, conditions[], threatTable{}, actionCooldown, bonusCooldown, reactionCooldown
- `ActionEvent`: actorId, targetId, type, timestamp, spellId?, weaponId?
- `CombatTick`: events[], resolvedEffects[], stateDelta[]

### 10.3 Anti-Cheat Requirements

| Check | Where | Method |
|---|---|---|
| Dice rolls | Server only | All d20, damage dice computed server-side with a CSPRNG |
| Range validation | Server | Check Euclidean distance in tiles on action receipt |
| Cooldown validation | Server | Server-tracked timestamps; reject actions submitted before cooldown expires |
| Speed hacking | Server | Reject movement updates that imply speed > class max + 20% tolerance |
| Spell slot tampering | Server | Spell slot counts stored only on server; never trust client-submitted slot state |

### 10.4 Latency Tolerance

Target: **200ms round-trip combat feel** for 95th percentile players.

| Strategy | Detail |
|---|---|
| Optimistic movement | Client-predicted movement; server corrects only on significant desync |
| Action latency buffer | Server accepts actions up to 150ms after their logical tick window (client latency compensation) |
| Condition render | Apply conditions client-side immediately on receiving the event; server is authoritative on expiry |
| Boss phase transitions | Pre-broadcast phase transition 500ms before it applies (client plays transition animation) |
| Heartbeat ping | Client sends ping every 5 seconds; server responds; display latency in UI settings |

### 10.5 Zone Architecture

- **Open World Zones:** Up to 100 players per zone instance; combat calculations scoped to visible entities (30-tile view radius).
- **Dungeon Zones:** Instanced per party (max 5 players); dedicated combat processor per instance.
- **PvP Contested Zones:** Up to 50 players; combat processor optimised for player-vs-player latency (lower tick interval: 66ms / 15 ticks/second).

---

## Open Questions (CEO/CTO Input Needed)

| # | Question | Urgency | Raised by |
|---|---|---|---|
| OQ-1 | Should Warrior have access to a Taunt reaction (auto-triggered) or only a manual Taunt active ability? | Medium | Game Designer |
| OQ-2 | Party size capped at 5 — confirm this is correct for MVP or should we start with 4? | High | Game Designer |
| OQ-3 | Enrage timer set at 8 minutes — is this tunable per boss in the CMS, or hard-coded? | Medium | Game Designer |
| OQ-4 | PvP death penalty: CEO confirmed gold drop + durability. Should we also disable item drop permanently, or leave it configurable for future Hardcore mode? | Medium | Game Designer |
| OQ-5 | Concentration mechanic: should we implement full D&D 5e CON save on damage in MVP, or simplify to "new [C] spell breaks old one, no save required"? | High | Game Designer |
| OQ-6 | Half-casters (Paladin): confirm they share this slot table with the CTO — do we want to simplify to full-caster slots in MVP to reduce implementation scope? | Medium | Game Designer |

---

## Version History

| Version | Date | Summary |
|---|---|---|
| 1.0 | 2026-04-14 | Initial complete draft — all 10 sections. Authored by Game Designer. |

