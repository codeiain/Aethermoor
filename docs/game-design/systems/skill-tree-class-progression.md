# Skill Tree & Class Progression System — Project AETHERMOOR

**Document Key:** `skill-tree-spec`
**Issue:** [RPG-77](/RPG/issues/RPG-77) · [RPG-80](/RPG/issues/RPG-80)
**Version:** 2.0
**Date:** 2026-04-19
**Author:** Game Designer

---

## Overview

This document specifies the Skill Tree and Class Progression system for AETHERMOOR. It gives players meaningful build identity beyond the base level-up loop, delivering the systemic RPG depth pillar of the project while remaining accessible to new players.

**Scope:** All six playable class archetypes — **Knight**, **Archmage**, **Ranger**, **Shadowblade**, **Cleric (Warden)**, and **Bard** — each with two specialisation branches. The system is designed for iteration; new classes follow the same template and can be added without architectural change.

**Cross-references:** All stats, damage types, conditions, and class modifiers in this document align with the [Combat Design Specification](/RPG/issues/RPG-77) (`docs/game-design/combat/combat-system.md`) and [Progression Balancing](/RPG/issues/RPG-77) (`docs/game-design/beta-content/progression-balancing.md`). Do not alter those without reconciling here.

---

## Design Goals

| Goal | Player Experience |
|---|---|
| Build identity | Players feel their Knight plays meaningfully differently from a friend's Knight based on skill choices |
| Gradual complexity | Players spend their first few levels on obvious, impactful skills; depth reveals itself naturally |
| Meaningful gates | Skills unlock when the player is actually encountering content where they shine |
| Respec availability | Players can experiment without feeling permanently punished |
| MMO party synergy | Branch choices create complementary roles in group content |

---

## 1. Talent Point Economy

### 1.1 Earning Points

| Trigger | Points Awarded |
|---|---|
| Level up (levels 1–20) | 1 Talent Point per level |
| **Total at level 20** | **20 Talent Points** |

The first point is awarded at **level 1** (character creation) so the skill tree is immediately interactive. There are no bonus milestone points — the clean 1-per-level model is easy to communicate to players and to implement.

### 1.2 Spending Points

Skills are arranged in two branches per class. Skills have:

1. **A level requirement** — cannot spend the point until that character level is reached.
2. **A TP cost** — see tier table below.
3. **Prerequisite skill(s)** — must have unlocked the listed skill(s) first.

| Skill Tier | Character Level Gate | TP Cost | Skills per Branch |
|---|---|---|---|
| Tier 1 | 1–5 | 1 TP | 3 |
| Tier 2 | 6–10 | 1 TP | 3 |
| Tier 3 | 11–15 | 2 TPs | 2 |
| Tier 4 | 16–20 | 3 TPs | 2 |
| **Branch total** | — | **16 TPs** | **10** |

**Build budget analysis:**

- Fully mastering one branch costs **16 TPs**.
- Players have **20 TPs** at max level.
- Remaining **4 TPs** allow partial investment into the second branch (up to Tier 2).
- Fully unlocking both branches would cost **32 TPs** — never achievable.
- This creates genuine specialisation: every player commits to a primary playstyle.

### 1.3 Respec

| Parameter | Value |
|---|---|
| Respec allowed | Once per week |
| Cost | 50g × character level |
| NPC | Trainer in any major town |
| Scope | Full reset — all TPs refunded and re-spendable |
| Restriction | Cannot respec in an active dungeon instance |

Rationale: weekly respec lets players experiment without breaking the economy. Scaling gold cost makes endgame respec a meaningful spend without being prohibitive.

---

## 2. Skill Tree UI

### 2.1 Layout

- Two vertical branches side-by-side per class.
- Skills displayed as icon nodes, connected by lines indicating prerequisites.
- Locked nodes: greyed out; tooltip shows missing prerequisite and level requirement.
- Available nodes: highlighted border; tap to preview, double-tap/click to confirm spend.
- Invested nodes: filled with branch colour.

### 2.2 Mobile Layout

- Full-screen modal: triggered from Character Sheet → Skills tab.
- Pinch-zoom supported; default view shows all tiers simultaneously.
- Each node: 64×64px minimum touch target.
- TP counter always visible at top of modal.

### 2.3 Branch Colours

| Class | Branch A | Branch B |
|---|---|---|
| Knight | Blue (Guardian) | Red (Berserker) |
| Archmage | Orange (Elementalist) | Purple (Arcanist) |
| Ranger | Green (Warden) | Gold (Sharpshooter) |
| Shadowblade | Crimson (Assassin) | Silver (Phantom) |
| Cleric (Warden) | White/Gold (Divine Healer) | Amber (Crusader) |
| Bard | Teal (Maestro) | Violet (Skirmisher) |

---

## 3. Class Skill Trees

### 3.1 Notation

- **[P]** — Passive: always active once unlocked.
- **[A]** — Active: player-triggered ability; uses Action, Bonus Action, or Reaction as noted.
- **[R]** — Reaction: triggers automatically or on player prompt.
- **DC** — Difficulty Class for saving throws. Where INT/WIS/DEX/CHA appears, use the class's key ability modifier: `8 + proficiency bonus + ability modifier`.
- All damage types align with combat-system.md Section 3.3.
- Proficiency bonus table from combat-system.md Section 2.1 applies to all skill attack rolls.

---

## 4. KNIGHT

**Key abilities:** STR (melee attacks), CON (HP, saves)
**Weapons:** Longsword, Greataxe, Greatsword, Shield
**Role spectrum:** Tank anchor (Guardian) ↔ High-burst melee DPS (Berserker)

**Class passive (both branches):** _Iron Constitution_ — +3 HP per level beyond base HP die.

---

### 4A. Guardian Branch (Tank / Defender)

Branch passive: _Shield Wall_ — While wielding a shield, AC +1.

| # | Skill | Tier | Cost | Level Gate | Prerequisites | Type | Effect |
|---|---|---|---|---|---|---|---|
| 1 | **Taunt** | T1 | 1 TP | 1 | — | [A] Action | Force one enemy within 30ft to target only you for 2 rounds. Generates +20 flat threat. DC: CON. |
| 2 | **Shield Mastery** | T1 | 1 TP | 1 | — | [P] | Shield bash (Bonus Action): 1d4+STR bludgeoning; target STR save or knocked prone. Once per round. |
| 3 | **Second Wind** | T1 | 1 TP | 3 | Taunt | [A] Bonus | Heal self: 1d10 + level HP. Once per combat. |
| 4 | **Deflect** | T2 | 1 TP | 5 | Shield Mastery | [R] | When hit by a melee attack, reduce damage by 1d6 + CON modifier. Once per round. |
| 5 | **Rallying Cry** | T2 | 1 TP | 7 | Taunt + Second Wind | [A] Action | All allies within 20ft gain 1d6 + level temporary HP for 1 minute. Once per short rest. |
| 6 | **Fortified Stance** | T2 | 1 TP | 9 | Deflect | [A] Bonus | For 1 round: +3 AC; speed reduced to 0. Can break early by moving (bonus ends). |
| 7 | **Iron Will** | T3 | 2 TPs | 11 | Second Wind + Deflect | [P] | Advantage on all CON saving throws. |
| 8 | **Guardian's Aura** | T3 | 2 TPs | 13 | Rallying Cry + Fortified Stance | [P] | All allies within 10ft gain +1 AC (does not stack with multiple Guardians). |
| 9 | **Unyielding** | T4 | 3 TPs | 15 | Iron Will + Guardian's Aura | [P] | When reduced to 0 HP, make a CON save DC 15 to survive at 1 HP instead. Once per long rest. |
| 10 | **Last Stand** | T4 | 3 TPs | 17 | Unyielding | [P] | While below 25% max HP, all incoming damage is halved (rounded down, minimum 1). |

**Guardian branch narrative:** "I stand between my party and death."

---

### 4B. Berserker Branch (Melee DPS / High-Risk)

Branch passive: _Battle Fury_ — Deal +1 damage per 10% of max HP missing (stacks to +10 damage at 1 HP).

| # | Skill | Tier | Cost | Level Gate | Prerequisites | Type | Effect |
|---|---|---|---|---|---|---|---|
| 1 | **Power Strike** | T1 | 1 TP | 1 | — | [A] Action | One melee attack at +2 hit, +1d6 damage. Uses full Action. |
| 2 | **Reckless Attack** | T1 | 1 TP | 1 | — | [A] Action | Attack with advantage on all attack rolls this round. Until your next turn, all attacks against you also have advantage. |
| 3 | **Cleave** | T1 | 1 TP | 3 | Power Strike | [P] | When you hit a melee attack, adjacent enemies (within 5ft of target) take half the damage dice result (no modifier). |
| 4 | **Battle Cry** | T2 | 1 TP | 5 | Reckless Attack | [A] Bonus | Gain advantage on your next attack roll this round. Once per round. |
| 5 | **Extra Attack** | T2 | 1 TP | 7 | Power Strike + Battle Cry | [P] | Make 2 attacks with your Attack action instead of 1. |
| 6 | **Frenzy** | T2 | 1 TP | 9 | Reckless Attack + Battle Cry | [A] Bonus | Enter Frenzy for 3 rounds: +2 to attack rolls, +1d6 damage, −2 AC; gain one free Bonus Action attack per round (1d6+STR). Once per short rest. |
| 7 | **Brutal Critical** | T3 | 2 TPs | 11 | Cleave + Extra Attack | [P] | Critical hits roll one additional weapon damage die (e.g. longsword: 3d8 instead of 2d8 on crit). |
| 8 | **War Machine** | T3 | 2 TPs | 13 | Frenzy + Brutal Critical | [P] | While in Frenzy: ignore disadvantage from being surrounded (3+ adjacent enemies); move through enemy spaces (provoking no opportunity attacks from targets you attacked this round). |
| 9 | **Overwhelming Blow** | T4 | 3 TPs | 15 | War Machine | [A] Action | One attack at +4 to hit dealing ×3 weapon dice damage. Target: STR save DC 15 or knocked prone for 1 round. Once per combat. |
| 10 | **Avatar of War** | T4 | 3 TPs | 17 | Overwhelming Blow | [P] | While below 50% max HP: advantage on all attacks, +4 to all damage rolls, +10 tiles/round movement. |

**Berserker branch narrative:** "The more it hurts, the harder I hit."

---

## 5. ARCHMAGE

**Key abilities:** INT (spell attacks, spell DC), CON (Concentration saves)
**Weapons:** Staff (Arcane), Dagger
**Role spectrum:** AoE elemental burst (Elementalist) ↔ Control/single-target force damage (Arcanist)

**Class passive (both branches):** _Arcane Recovery_ — Once per long rest, after a short rest, recover spell slots with total levels equal to half your level (round up). (Matches spell slot table in combat-system.md.)

---

### 5A. Elementalist Branch (AoE / Elemental DPS)

Branch passive: _Elemental Mastery_ — All elemental spells (Fire, Cold, Lightning) deal +10% damage.

| # | Skill | Tier | Cost | Level Gate | Prerequisites | Type | Effect |
|---|---|---|---|---|---|---|---|
| 1 | **Firebolt Upgrade** | T1 | 1 TP | 1 | — | [P] | Firebolt cantrip deals an additional +1d6 fire damage. Scales: +1d6 at levels 5, 10, 15. |
| 2 | **Frost Nova** | T1 | 1 TP | 1 | — | [A] Action | 10ft radius burst centred on self; 1d6 cold damage; DEX save DC or Frozen for 12s. No slot cost; 1/short rest. |
| 3 | **Chain Lightning** | T1 | 1 TP | 4 | Firebolt Upgrade | [P] | Lightning-type spells arc to 1 additional enemy within 20ft of primary target for 50% damage (once per cast). |
| 4 | **Ice Wall** | T2 | 1 TP | 6 | Frost Nova | [A] Action | Place a 3-tile solid ice wall (1 tile wide) within 30ft. Blocks movement. Lasts 3 rounds or until dealt 10+ fire damage. No slot; 1/short rest. |
| 5 | **Combustion** | T2 | 1 TP | 8 | Firebolt Upgrade + Chain Lightning | [P] | Fire spells you cast apply Burning (1d6 fire/6s, 18s) on a critical hit or when cast using a 3rd-level or higher slot. |
| 6 | **Elemental Convergence** | T2 | 1 TP | 9 | Ice Wall + Combustion | [P] | When you deal damage of two different elemental types to the same target in one round, that target takes a bonus 2d6 force damage (once per target per round). |
| 7 | **Blizzard** | T3 | 2 TPs | 11 | Ice Wall + Combustion | [A] Action | 30ft radius AoE zone, Concentration 1 min. Any creature entering or starting turn inside: 2d8 cold + DEX save or Frozen. Costs a 3rd-level spell slot. |
| 8 | **Thundercrash** | T3 | 2 TPs | 13 | Chain Lightning + Elemental Convergence | [A] Action | 20ft radius AoE; 4d6 lightning; DEX save halves. Frozen targets take double damage from this spell. Costs a 3rd-level slot. |
| 9 | **Inferno** | T4 | 3 TPs | 15 | Blizzard + Thundercrash | [A] Bonus | Activate: for 1 minute, all your spells deal an additional +1d10 fire damage. Once per long rest. |
| 10 | **Arcane Storm** | T4 | 3 TPs | 17 | Inferno + Elemental Convergence | [A] Action | 50ft radius Concentration zone, 1 min. Allies deal +1d8 elemental damage on hits; enemies take 2d6 elemental per round (type cycles: fire/cold/lightning each round). Costs a 5th-level slot. |

**Elementalist branch narrative:** "Choose your element. Choose your moment."

---

### 5B. Arcanist Branch (Control / Force Damage)

Branch passive: _Arcane Focus_ — Spell save DC +1; spell attack rolls +1.

| # | Skill | Tier | Cost | Level Gate | Prerequisites | Type | Effect |
|---|---|---|---|---|---|---|---|
| 1 | **Arcane Bolt** | T1 | 1 TP | 1 | — | [A] Action | Ranged spell attack (100ft); 1d10 force damage. On Natural 20 attack roll: target is Stunned 1 round. |
| 2 | **Arcane Shield** | T1 | 1 TP | 1 | — | [R] | When hit by any attack, gain +3 AC against that triggering attack. Once per round. |
| 3 | **Gravity Well** | T1 | 1 TP | 4 | Arcane Bolt | [A] Action | 10ft radius field at a point within 60ft. Concentration, 1 min. All enemies inside: speed halved; cannot take Dash action. Costs a 1st-level slot. |
| 4 | **Counterspell** | T2 | 1 TP | 6 | Arcane Shield | [R] | When an enemy within 60ft casts a spell, attempt to interrupt it: spell level ≤2 auto-cancelled; spell level 3+ requires INT check DC 10 + spell level. Costs a 3rd-level slot. Once per short rest. |
| 5 | **Force Lance** | T2 | 1 TP | 8 | Arcane Bolt + Gravity Well | [A] Action | 120ft line attack (1 tile wide); 3d8 force damage; STR save or pushed 15ft back. Costs a 2nd-level slot. |
| 6 | **Arcane Echo** | T2 | 1 TP | 9 | Arcane Bolt + Arcane Shield | [P] | On any spell critical hit, deal 1d8 force damage to one additional enemy within 20ft of the target (free, no action). |
| 7 | **Nullfield** | T3 | 2 TPs | 11 | Gravity Well + Counterspell | [A] Action | 20ft radius zone, 1 round. All magical effects (buffs and debuffs) are suppressed; no spells can be cast inside. Costs a 3rd-level slot. |
| 8 | **Spell Surge** | T3 | 2 TPs | 13 | Force Lance + Arcane Echo | [P] | After casting any spell of 3rd level or higher, your next spell of 1st or 2nd level costs no slot. Once per short rest. |
| 9 | **Reality Bend** | T4 | 3 TPs | 15 | Nullfield + Spell Surge | [A] Bonus | Teleport up to 60ft to any visible location; ignore opportunity attacks this round. Costs a 2nd-level slot. Unlimited uses. |
| 10 | **Reality Fracture** | T4 | 3 TPs | 17 | Reality Bend + Arcane Echo | [A] Action | 30ft radius AoE at a point within 120ft. All enemies take 8d10 force damage (no save, no resistance applies). Allies take no damage. Costs a 5th-level slot. Once per long rest. |

**Arcanist branch narrative:** "I reshape the rules of the fight itself."

---

## 6. RANGER

**Key abilities:** DEX (attack rolls, damage), WIS (nature abilities, some saves)
**Weapons:** Longbow, Shortbow, Hand Crossbow, Dagger (finesse)
**Role spectrum:** Precision single-target ranged (Sharpshooter) ↔ Nature magic, traps, pet (Warden)

**Class passive (both branches):** _Wilderness Expertise_ — Advantage on Perception checks; cannot be surprised in outdoor zones.

---

### 6A. Sharpshooter Branch (Precision / Ranged DPS)

Branch passive: _Eagle Eye_ — Ranged attacks ignore half-cover; +1 attack rolls against targets at range >60ft.

| # | Skill | Tier | Cost | Level Gate | Prerequisites | Type | Effect |
|---|---|---|---|---|---|---|---|
| 1 | **Aimed Shot** | T1 | 1 TP | 1 | — | [A] Bonus | Spend Bonus Action aiming; next attack this round gains +2 hit and +1d8 damage. |
| 2 | **Steady Hand** | T1 | 1 TP | 1 | — | [P] | No disadvantage on ranged attacks while adjacent to enemies. |
| 3 | **Vital Strike** | T1 | 1 TP | 4 | Aimed Shot | [P] | On a critical hit with a ranged weapon, target gains Bleeding (1d4/6s) for 18s. |
| 4 | **Long Shot** | T2 | 1 TP | 6 | Steady Hand | [P] | All bow/crossbow range increments increased by 50%. No penalty die at long range. |
| 5 | **Piercing Arrow** | T2 | 1 TP | 8 | Aimed Shot + Vital Strike | [A] Action | One arrow penetrates through primary target and hits the next enemy directly behind it in a line for 60% damage. |
| 6 | **Hunter's Mark** | T2 | 1 TP | 9 | Long Shot | [A] Bonus | Mark one target; deal +1d6 damage on all hits against them for 1 hour. On marked target's death, automatically re-marks nearest enemy (free, no action). Concentration. |
| 7 | **Glancing Shot** | T3 | 2 TPs | 11 | Piercing Arrow + Hunter's Mark | [P] | On a ranged miss, deal DEX modifier damage to the target (minimum 1; no dice). |
| 8 | **Sniper Stance** | T3 | 2 TPs | 13 | Vital Strike + Glancing Shot | [A] Bonus | Toggle on: lose 10 tiles/round movement; gain +3 to all ranged attack rolls. Toggle off: free. |
| 9 | **Eagle Eye Mastery** | T4 | 3 TPs | 15 | Sniper Stance + Hunter's Mark | [P] | Crits occur on a roll of 19–20 for all ranged attacks. Critical hits apply Vital Strike's Bleeding even without the Vital Strike skill. |
| 10 | **Perfect Shot** | T4 | 3 TPs | 17 | Eagle Eye Mastery | [A] Action | One ranged attack that automatically hits and deals maximum damage (no roll, no random — roll substituted by max value). Once per combat. |

**Sharpshooter branch narrative:** "One shot. One kill. No wasted arrows."

---

### 6B. Warden Branch (Nature / Pet / AoE Utility)

Branch passive: _Nature's Bond_ — You may summon an **Animal Companion** (Wolf, stats below) at will once you invest in this branch. The companion persists until dismissed or killed; resummon after combat at no cost.

**Animal Companion (Wolf) base stats:**
- AC: 11 | HP: Ranger level × 5 | Speed: 40 tiles/round
- Attack: Bite — 1d6 + DEX modifier (Ranger's DEX), +proficiency to hit
- Improves with Beast Bond skill (see below)

| # | Skill | Tier | Cost | Level Gate | Prerequisites | Type | Effect |
|---|---|---|---|---|---|---|---|
| 1 | **Entangle** | T1 | 1 TP | 1 | — | [A] Action | 15ft radius at a point within 60ft; vines erupt. DEX save or Restrained 2 rounds. Costs a 1st-level slot; 1/short rest if no slot. |
| 2 | **Barbed Trap** | T1 | 1 TP | 1 | — | [A] Action | Place a trap on an adjacent tile. Triggers on any enemy entering the tile: 2d6 piercing + Bleeding (1d4/6s, 18s). Lasts 10 minutes. Carry up to 3 traps. |
| 3 | **Camouflage** | T1 | 1 TP | 4 | Entangle | [A] Bonus | Become invisible while standing still on a vegetation tile (forest, grass, swamp). Breaks on movement or attack. No cost; unlimited uses. |
| 4 | **Pack Hunter** | T2 | 1 TP | 6 | Barbed Trap (and Warden branch passive active) | [P] | You and your Animal Companion have Pack Tactics: both gain advantage on attack rolls against an enemy if the other is within 5ft of that enemy. |
| 5 | **Multi-Arrow** | T2 | 1 TP | 8 | Entangle + Barbed Trap | [A] Action | Fire arrows at up to 3 separate targets within 30ft; each takes 1d6 + DEX modifier piercing damage. Uses full Action. |
| 6 | **Poison Arrow** | T2 | 1 TP | 9 | Pack Hunter + Barbed Trap | [A] Bonus | Coat your next 3 arrows with poison (1 minute preparation). Each poisoned arrow deals +1d6 poison damage on hit; target CON save DC 13 or Poisoned 18s. |
| 7 | **Volley** | T3 | 2 TPs | 11 | Multi-Arrow + Camouflage | [A] Action | Rain arrows in a 20ft radius at a point within 120ft. All targets take 2d8 piercing damage; DEX save halves. |
| 8 | **Beast Bond** | T3 | 2 TPs | 13 | Pack Hunter + Poison Arrow | [P] | Animal Companion gains: +2 to attack rolls, +3 HP per Ranger level (retroactive), Pack Hunter range extended to 20ft. |
| 9 | **Storm of Arrows** | T4 | 3 TPs | 15 | Volley + Beast Bond | [A] Action | Massive arrow volley. 40ft radius AoE at a point within 120ft. All enemies: 4d8 piercing + 2d6 poison (no save). Once per long rest. |
| 10 | **Apex Predator** | T4 | 3 TPs | 17 | Storm of Arrows | [P] | Once per combat, when you or your Animal Companion kills an enemy, both of you immediately gain one free action (attack, move, or use an ability — not a spell slot ability). |

**Warden branch narrative:** "The forest fights with me."

---

## 7. SHADOWBLADE

**Key abilities:** DEX (attack rolls, damage, evasion), INT (trap DCs, special ability checks)
**Weapons:** Dagger (finesse), Short sword, Rapier, Hand crossbow
**Role spectrum:** Glass-cannon burst assassin (Assassin) ↔ Evasive phantom with mobility/debuffs (Phantom)

**Class passive (both branches):** _Predator's Mark_ — Once per round, when you attack a target who has not yet acted in this combat, is Surprised, Stunned, or Prone, deal +1d6 bonus damage on the hit. Scales: +1d6 at levels 6, 11, 16 (max +4d6 at L16).

---

### 7A. Assassin Branch (Burst / Single-Target Damage)

Branch passive: _Death's Edge_ — Critical hits with melee weapons apply Bleeding (1d6/6s, 24s). Critical hit range: 19–20 (stackable with skills that extend crit range; floor is 17–20).

| # | Skill | Tier | Cost | Level Gate | Prerequisites | Type | Effect |
|---|---|---|---|---|---|---|---|
| 1 | **Backstab** | T1 | 1 TP | 1 | — | [A] Action | Melee attack; if you are behind or flanking the target (within 5ft and an ally is also adjacent to the same target), deal +2d6 bonus damage. |
| 2 | **Shadowstep** | T1 | 1 TP | 1 | — | [A] Bonus | Teleport up to 20ft to any unoccupied tile. If used before attacking this round, also grants Hidden until your next action. 1/round. |
| 3 | **Cheap Shot** | T1 | 1 TP | 3 | Backstab | [A] Bonus | One melee attack at −1 to hit; on hit: target loses their Reaction until the start of their next turn. |
| 4 | **Poison Blade** | T2 | 1 TP | 5 | Backstab | [P] | Your melee attacks can apply Poison on a critical hit (CON save DC 13 or Poisoned 18s). On an already-Poisoned target, the attack also deals +1d6 bonus poison damage. |
| 5 | **Mark for Death** | T2 | 1 TP | 7 | Shadowstep + Cheap Shot | [A] Bonus | Mark one target: all your attacks against them deal +1d6 bonus damage and apply Vulnerable to Slashing for 1 minute. Once per combat. |
| 6 | **Hemorrhage** | T2 | 1 TP | 9 | Poison Blade + Cheap Shot | [P] | Attacks against Bleeding targets deal +1 extra damage per Bleeding stack on the target (max +5). |
| 7 | **Shadow Strike** | T3 | 2 TPs | 11 | Mark for Death + Hemorrhage | [A] Action | Devastating melee strike: 3× weapon damage dice + DEX modifier. You then become Hidden (if not fully surrounded by 3+ adjacent enemies). Once per short rest. |
| 8 | **Execution** | T3 | 2 TPs | 13 | Shadow Strike + Poison Blade | [P] | When a target is at ≤25% max HP, your attacks deal +2d6 damage and crit range extends to 17–20 against them. |
| 9 | **Death Mark** | T4 | 3 TPs | 15 | Execution + Shadow Strike | [A] Action | Your next melee attack (within 1 minute) is an automatic critical hit dealing max damage on all dice. Once per long rest. |
| 10 | **Reaper** | T4 | 3 TPs | 17 | Death Mark | [P] | When you kill a target, immediately reset Shadowstep's cooldown, become Hidden for 3 seconds (enough to reposition), and gain +1d6 bonus damage on all attacks this combat (stacks per kill; hard cap: +5d6 at 5 kills; resets each combat). |

**Assassin branch narrative:** "One mark. One wound. One death."

---

### 7B. Phantom Branch (Mobility / Debuffs / Evasion)

Branch passive: _Phantom Veil_ — While not wearing heavy armour, all Stunned and Slowed debuff durations on you are halved. You may move through enemy-occupied tiles without provoking opportunity attacks.

| # | Skill | Tier | Cost | Level Gate | Prerequisites | Type | Effect |
|---|---|---|---|---|---|---|---|
| 1 | **Smoke Bomb** | T1 | 1 TP | 1 | — | [A] Bonus | Throw a smoke bomb at a point within 30ft. 10ft radius cloud: all attacks originating from inside have disadvantage. Lasts 3 rounds. 2 charges; recharge on short rest. |
| 2 | **Crippling Strike** | T1 | 1 TP | 1 | — | [A] Action | Melee attack; on hit: target's movement speed halved for 2 rounds (CON save DC 12 negates; DC = 8 + proficiency + DEX modifier). |
| 3 | **Feint** | T1 | 1 TP | 3 | Smoke Bomb | [A] Bonus | Fake an attack to bait a reaction; your real attack this round gains advantage. Once per round. |
| 4 | **Shadow Meld** | T2 | 1 TP | 5 | Smoke Bomb | [A] Action | Become fully invisible for up to 3 rounds (Concentration). Breaks on attack or spell. Once per short rest. |
| 5 | **Ghost Walk** | T2 | 1 TP | 7 | Feint + Crippling Strike | [A] Bonus | For 1 round, pass through solid tiles (walls, obstacles) and ignore collision with enemies. 1/short rest. |
| 6 | **Blind Strike** | T2 | 1 TP | 9 | Crippling Strike + Feint | [A] Action | Melee attack; on hit: apply Blinded for 2 rounds (WIS save DC 13 negates). Blinded: all attacks by the target have disadvantage; all attacks against the target have advantage. |
| 7 | **Spectral Form** | T3 | 2 TPs | 11 | Shadow Meld + Ghost Walk | [A] Bonus | For 2 rounds: gain +4 AC, resist physical damage, and your attacks ignore AC bonuses from worn armour (treat armour bonus as 0; natural DEX/shield bonuses still apply). Once per combat. |
| 8 | **Mirage** | T3 | 2 TPs | 13 | Ghost Walk + Blind Strike | [A] Action | Spawn 2 illusory decoy copies within 20ft. Enemies targeting you must succeed on a WIS save (DC 14) or attack a copy instead. Each copy has 1 HP. Copies last 1 minute. Once per short rest. |
| 9 | **Void Step** | T4 | 3 TPs | 15 | Spectral Form + Mirage | [A] Bonus | Teleport to any visible unoccupied tile within 40ft, bypassing line-of-sight restrictions (ethereal transit). Does not break stealth or Concentration. Unlimited uses. |
| 10 | **Phantom Shroud** | T4 | 3 TPs | 17 | Void Step + Mirage | [P] | Once per combat, when you would be reduced to 0 HP, instead drop to 1 HP, become invisible for 5 seconds, and Void Step up to 30ft in any direction (triggers automatically). While at ≤20% max HP, all incoming damage is reduced by your DEX modifier (minimum 0 reduction). |

**Phantom branch narrative:** "You can't kill what you can't touch."

---

## 8. CLERIC (WARDEN)

**Key abilities:** WIS (spell attacks, spell DC, healing), CON (HP, Concentration saves)
**Weapons:** Mace, Flail, Shield, Quarterstaff
**Role spectrum:** Restoration/party healer (Divine Healer) ↔ Holy warrior melee DPS (Crusader)

**Class passive (both branches):** _Sacred Ground_ — Whenever you cast a healing spell or ability, you and all allies within 10ft of the target also gain 1d4 HP (radiant overflow; not a separate heal action). Scales: +1d4 at levels 7 and 13 (max +3d4 at L13).

---

### 8A. Divine Healer Branch (Restoration / Party Support)

Branch passive: _Overheal_ — Your healing spells can overheal targets up to 20% of their max HP (stored as temporary HP, maximum 30-second duration). Example: a full-health player with 100 max HP can receive up to 20 overhealing as temporary HP.

| # | Skill | Tier | Cost | Level Gate | Prerequisites | Type | Effect |
|---|---|---|---|---|---|---|---|
| 1 | **Holy Bolt** | T1 | 1 TP | 1 | — | [A] Action | Ranged spell attack (60ft); 1d8 + WIS modifier radiant damage. Deals double damage to undead. |
| 2 | **Cure Wounds** | T1 | 1 TP | 1 | — | [A] Action | Touch: restore 1d8 + WIS modifier HP. Costs a 1st-level slot. Upcasting: +1d8 per slot level. |
| 3 | **Lesser Restoration** | T1 | 1 TP | 3 | Cure Wounds | [A] Action | Remove one condition from a touched target: Poisoned, Bleeding, Slowed, or Frightened. No slot cost. 1/short rest. |
| 4 | **Prayer of Mending** | T2 | 1 TP | 5 | Cure Wounds | [A] Bonus | Attach a healing-over-time prayer to a target: heals 1d6 + WIS at the start of each of their turns for 3 rounds. Costs a 2nd-level slot. Only one Prayer active per Cleric at a time. |
| 5 | **Mass Heal** | T2 | 1 TP | 7 | Lesser Restoration + Prayer of Mending | [A] Action | 20ft radius centred on self: all allies heal 2d6 + WIS modifier HP. Costs a 3rd-level slot. Once per short rest. |
| 6 | **Shield of Faith** | T2 | 1 TP | 9 | Holy Bolt + Prayer of Mending | [A] Bonus | Grant one target +2 AC for 1 minute (Concentration). Does not stack with Guardian's Aura. Costs a 1st-level slot. Unlimited uses. |
| 7 | **Revive** | T3 | 2 TPs | 11 | Mass Heal + Shield of Faith | [A] Action | Touch a downed ally (0 HP, within the KO window): restore them to 25% max HP, remove all conditions. Costs a 3rd-level slot. Once per combat. |
| 8 | **Sanctuary** | T3 | 2 TPs | 13 | Revive + Shield of Faith | [A] Bonus | Target ally: enemies must succeed on a WIS save (Cleric's spell DC) before targeting them with an attack or harmful spell; failure forces another target. Lasts 1 minute or until the target attacks. Costs a 2nd-level slot. |
| 9 | **Greater Restoration** | T4 | 3 TPs | 15 | Sanctuary + Mass Heal | [A] Action | Touch: remove all negative conditions and heal 4d8 + WIS modifier HP. Costs a 5th-level slot. Once per long rest. |
| 10 | **Miracle** | T4 | 3 TPs | 17 | Greater Restoration | [A] Action | 30ft radius: all allies fully healed to max HP, all negative conditions removed. Any ally who died during this combat may be restored to 50% HP (server KO-window permitting — see OQ-8). Costs a 5th-level slot. Once per long rest. |

**Divine Healer branch narrative:** "No one falls while I stand."

---

### 8B. Crusader Branch (Smite / Melee Holy DPS)

Branch passive: _Holy Wrath_ — Your melee attacks deal +1d4 radiant damage. Against undead or demonic enemies, this bonus becomes +1d8.

| # | Skill | Tier | Cost | Level Gate | Prerequisites | Type | Effect |
|---|---|---|---|---|---|---|---|
| 1 | **Divine Smite** | T1 | 1 TP | 1 | — | [A] Bonus | After hitting with a melee attack, expend a spell slot to deal bonus radiant damage: 1st-level slot +2d8; 2nd +3d8; 3rd +4d8. Against undead/demons: +1d8 per slot level additionally. |
| 2 | **Lay on Hands** | T1 | 1 TP | 1 | — | [A] Action | Touch any creature: restore HP from a healing pool equal to Cleric level × 5. Pool recharges on long rest. Multiple touches draw from same pool. |
| 3 | **Aura of Courage** | T1 | 1 TP | 3 | Lay on Hands | [P] | All allies within 10ft are immune to the Frightened condition. (Radius scales to 20ft at level 14.) |
| 4 | **Consecrate Ground** | T2 | 1 TP | 5 | Divine Smite | [A] Action | Sanctify a 15ft radius for 1 minute: allies inside gain advantage on all saving throws; undead/demons inside take 1d6 radiant damage per round. Costs a 2nd-level slot. 1/short rest. |
| 5 | **Holy Nova** | T2 | 1 TP | 7 | Aura of Courage + Consecrate Ground | [A] Action | Burst of holy energy: 10ft radius centred on self. Enemies: 2d8 radiant (WIS save halves). Allies: heal 1d8 HP. Costs a 2nd-level slot. |
| 6 | **Sacred Weapon** | T2 | 1 TP | 9 | Divine Smite + Lay on Hands | [A] Bonus | Empower weapon for 1 minute: +WIS modifier to attack and damage rolls; weapon counts as magical (overcoming non-magical resistances). Concentration. Once per short rest. |
| 7 | **Blessed Assault** | T3 | 2 TPs | 11 | Holy Nova + Sacred Weapon | [P] | When you deal damage with Divine Smite, the target becomes Vulnerable to Radiant damage for 1 round. Allies who hit the Vulnerable target this round deal +1d6 radiant damage. |
| 8 | **Crusader's Vow** | T3 | 2 TPs | 13 | Sacred Weapon + Consecrate Ground | [P] | While Sacred Weapon is active, each of your melee attacks restores 1d4 HP to the lowest-HP ally within 30ft (once per attack). |
| 9 | **Wrath of the Divine** | T4 | 3 TPs | 15 | Blessed Assault + Crusader's Vow | [A] Action | Massive melee strike: 5d8 radiant damage. Against undead/demons: 8d8 instead. All allies within 20ft heal 2d6 HP. Costs a 4th-level slot. Once per combat. |
| 10 | **Avatar of the Light** | T4 | 3 TPs | 17 | Wrath of the Divine | [A] Bonus | Activate once per long rest for 1 minute: all melee attacks deal +3d8 radiant damage; you emit a 20ft radius bright light (enemies entering the aura are Blinded for 1 round the first time); allies inside the aura gain resistance to Necrotic damage. |

**Crusader branch narrative:** "Faith made manifest. The divine is my blade."

---

## 9. BARD

**Key abilities:** CHA (spells, social abilities, CC DCs), DEX (ranged attacks, AC, finesse melee)
**Weapons:** Dagger (finesse), Rapier, Hand crossbow, Lute (musical instrument as arcane focus)
**Role spectrum:** Party buffer/support musician (Maestro) ↔ Disruptive skirmisher with CC (Skirmisher)

**Class passive (both branches):** _Bardic Inspiration_ — Once per short rest, grant an ally within 60ft a Bardic Inspiration die (1d6). The ally may add this die to one attack roll, ability check, or saving throw within the next 10 minutes. Scales: 1d8 at level 7, 1d10 at level 13. Only one Bardic Inspiration die per ally at a time.

---

### 9A. Maestro Branch (Party Buffs / Support)

Branch passive: _Song of Rest_ — During short rests, your music heals all party members within earshot for 1d6 + CHA modifier HP (in addition to their own Hit Dice recovery).

| # | Skill | Tier | Cost | Level Gate | Prerequisites | Type | Effect |
|---|---|---|---|---|---|---|---|
| 1 | **Cutting Words** | T1 | 1 TP | 1 | — | [R] | When an enemy within 60ft makes an attack roll or ability check, spend a Bardic Inspiration die to reduce the result by 1d6. 1/round. |
| 2 | **Hymn of Valor** | T1 | 1 TP | 1 | — | [A] Action | Sing for 1 round; all allies within 30ft gain +1d4 to all attack rolls for 1 minute (Concentration). Once per short rest. |
| 3 | **Dissonant Whispers** | T1 | 1 TP | 3 | Hymn of Valor | [A] Action | Wrack an enemy's mind within 60ft: 3d6 psychic damage; WIS save DC or target must immediately move its full speed away from you using its Reaction. Costs a 1st-level slot. |
| 4 | **Battle Hymn** | T2 | 1 TP | 5 | Hymn of Valor | [A] Bonus | Sung as a Bonus Action; for 3 rounds all allies within 30ft gain +1d6 bonus damage on attacks. Costs a 2nd-level slot. Once per short rest. |
| 5 | **Inspire Heroics** | T2 | 1 TP | 7 | Dissonant Whispers + Battle Hymn | [A] Bonus | Grant one ally a Heroic Inspiration die (1d8). They may use it to: deal +1d8 damage on one attack, reduce damage taken by 1d8, or automatically succeed on one saving throw. Once per ally per combat. |
| 6 | **Countercharm** | T2 | 1 TP | 9 | Cutting Words + Battle Hymn | [P] | While you perform (holding your instrument and not attacking), all allies within 30ft have advantage on saves against being Charmed or Frightened. Breaks if you attack or take damage. |
| 7 | **Magnificent Inspiration** | T3 | 2 TPs | 11 | Inspire Heroics + Countercharm | [P] | Bardic Inspiration die upgraded to 1d8 at all levels regardless of character level. Allies may add the die *after* seeing the roll result (not before). |
| 8 | **Symphony of Might** | T3 | 2 TPs | 13 | Battle Hymn + Countercharm | [A] Action | 1-minute performance: all allies within 40ft gain +2 to all attack rolls, +1d6 bonus damage on hits, and advantage on DEX saving throws. Concentration. Costs a 3rd-level slot. Once per long rest. |
| 9 | **Grand Finale** | T4 | 3 TPs | 15 | Symphony of Might + Magnificent Inspiration | [A] Action | Explosive musical crescendo, 30ft radius centred on self. Allies: +2d8 temporary HP and advantage on all rolls for 2 rounds. Enemies: 3d8 thunder damage, WIS save DC or Stunned 1 round. Costs a 4th-level slot. Once per long rest. |
| 10 | **Legend of the Battlefield** | T4 | 3 TPs | 17 | Grand Finale | [P] | Activate as Bonus Action once per long rest for 1 minute: Bardic Inspiration recharges on short rest instead of long rest; Hymn of Valor no longer requires Concentration; Symphony of Might becomes non-Concentration. Any ally who kills an enemy while under any of your active buffs heals 1d6 HP. |

**Maestro branch narrative:** "My song makes legends. Yours too."

---

### 9B. Skirmisher Branch (Disruption / CC / Mobility)

Branch passive: _Jack of All Trades_ — Add half your proficiency bonus (rounded down) to any skill check you are not already proficient in. You may use DEX instead of STR for melee attack and damage rolls with finesse weapons.

| # | Skill | Tier | Cost | Level Gate | Prerequisites | Type | Effect |
|---|---|---|---|---|---|---|---|
| 1 | **Brutal Mockery** | T1 | 1 TP | 1 | — | [A] Bonus | Savage insult at a target within 60ft. CHA spell DC (WIS save). On fail: target has disadvantage on all attacks against targets other than you for 1 round. |
| 2 | **Vicious Mockery** | T1 | 1 TP | 1 | — | [A] Action | Psychic cantrip: 1d4 psychic damage; WIS save DC or disadvantage on their next attack roll. No slot cost. Cantrip scaling: +1d4 at levels 5, 11, 17. |
| 3 | **Tumble** | T1 | 1 TP | 3 | Brutal Mockery | [A] Bonus | Disengage and move up to 10 extra tiles this turn. Ignore opportunity attacks this round. Once per round. |
| 4 | **Captivate** | T2 | 1 TP | 5 | Brutal Mockery | [A] Action | Paralysing performance: one humanoid target within 60ft. WIS save DC or Paralysed (Concentration, max 1 minute). All attacks against Paralysed targets have advantage; melee attacks are automatic critical hits. Costs a 2nd-level slot. |
| 5 | **Dissonance** | T2 | 1 TP | 7 | Vicious Mockery + Captivate | [A] Action | Sonic burst at a target within 60ft: 2d6 thunder damage; CON save DC or Silenced for 2 rounds (cannot cast spells or use verbal abilities). Costs a 2nd-level slot. |
| 6 | **Sonic Veil** | T2 | 1 TP | 9 | Tumble + Vicious Mockery | [A] Bonus | Harmonic blur for 1 minute: all attacks against you have disadvantage (while not Incapacitated). Concentration. Costs a 2nd-level slot. Once per short rest. |
| 7 | **Hypnotic Refrain** | T3 | 2 TPs | 11 | Captivate + Dissonance | [A] Action | Mesmerising musical pattern in a 30ft cube at a point within 120ft. Each creature that hears it: WIS save DC or Incapacitated with speed 0 (Concentration, max 1 minute). Costs a 3rd-level slot. |
| 8 | **Cacophony** | T3 | 2 TPs | 13 | Sonic Veil + Dissonance | [A] Action | Maddening noise in a 10ft radius at a point within 90ft. WIS save DC or affected creatures act randomly for 1 minute. Each affected creature rolls 1d8 at the start of their turn: 1 = attack a random adjacent creature; 2–6 = do nothing; 7–8 = act normally. Costs a 4th-level slot. Once per short rest. |
| 9 | **Mass Silence** | T4 | 3 TPs | 15 | Hypnotic Refrain + Cacophony | [A] Action | 20ft radius zone at a point within 60ft. No sound can pass through the zone boundary; all verbal spells and abilities are impossible inside; CON save DC or any creature that starts its turn inside is Silenced for 1 minute even after leaving. Costs a 4th-level slot. Once per combat. |
| 10 | **Pandemonium** | T4 | 3 TPs | 17 | Mass Silence | [P] | When any enemy fails a saving throw against one of your abilities: that enemy becomes Vulnerable to Psychic damage for 1 round. Your Cutting Words die is now 2d6 (use the higher result). Cacophony-affected creatures that accidentally attack an ally deal +1d6 psychic damage on those hits. |

**Skirmisher branch narrative:** "I don't fight fair. I fight loud."

---

## 10. Cross-Class Considerations

### 10.1 In Scope for v2.0

This document covers single-class skill trees only. The following are explicitly **out of scope** for this milestone:

| Feature | Status |
|---|---|
| Multiclassing | Out of scope — flag for post-MVP design |
| Prestige system | Out of scope — progression doc notes it opens at L20; design ticket needed |
| Cross-class skill borrowing | Out of scope |

### 10.2 Synergies Within Party (In Scope)

All six classes create natural party role synergies the server must account for:

| Combo | Synergy |
|---|---|
| Knight (Guardian) + Archmage (Elementalist) | Guardian holds aggro; Archmage nukes from safety |
| Knight (Berserker) + Ranger (Warden) | Entangle + Beast Bond sets up flanking for Pack Hunter; Berserker's Cleave hits grouped enemies |
| Ranger (Sharpshooter) + Knight (Guardian) | Hunter's Mark re-marks on kill; Guardian's Taunt funnels enemies for safe ranging |
| Archmage (Arcanist) + any class | Nullfield + Counterspell protects the party from elite caster enemies |
| Shadowblade (Assassin) + Cleric (Divine Healer) | Healer keeps the glass-cannon Shadowblade alive; Revive is the safety net for Death Mark gambits |
| Shadowblade (Phantom) + Bard (Skirmisher) | Blind Strike + Captivate creates double-locked targets; Pandemonium amplifies Phantom's Vulnerable to Slashing |
| Bard (Maestro) + Knight (Berserker) | Battle Hymn + Frenzy = devastating combined offense; Bard stays safely behind the Berserker |
| Cleric (Crusader) + Archmage (Elementalist) | Consecrate Ground advantage stacks with Thundercrash/Blizzard; Blessed Assault Vulnerable + Elemental Mastery |
| Bard (Maestro) + Ranger (Sharpshooter) | Hymn of Valor + Sniper Stance: Ranger gains +1d4 attack rolls on top of +3 static bonus; devastating accuracy |
| Cleric (Crusader) + Shadowblade (Assassin) | Sacred Weapon + Backstab flanking: Crusader's Aura of Courage removes Frightened (common debuff on fragile Shadowblade) |

### 10.3 Naming Note — "Warden"

**Flag for CEO review:** The Ranger class has a branch named "Warden Branch" (6B), and the Cleric class's full class title is "Cleric (Warden)." These names overlap in the branch colour UI (Ranger shows "Green (Warden)" while Cleric branches show "Divine Healer" and "Crusader" — no collision in branch display). However, the class selection screen and character sheet label must distinguish "Ranger — Warden Branch" from "Cleric (Warden)" clearly. Recommend: rename the Cleric's display title to **"Warden"** (dropping "Cleric" in-game UI) or rename the Ranger branch to **"Naturalist."** CEO to decide before UI implementation.

---

## 11. MMO Scaling Considerations

| Concern | Design Response |
|---|---|
| Multiple Guardians in one party | Guardian's Aura does not stack — only the Guardian with the highest level aura applies |
| Multiple Wardens (Animal Companion spam) | Server limits to 1 active Animal Companion per player; dismisses the old one on new summon |
| Nullfield (Arcane Arcanist) disrupting friendly casters | Nullfield affects all entities inside — friendly fire rule; AoE warning pulse before placement |
| Entangle / Ice Wall griefing movement | Only blocks enemy pathfinding; allied movement is unimpeded |
| Hunter's Mark multi-player stacking | Only one Hunter's Mark can apply to a target at once (last applied wins); bonus applies to the marking player's damage only |
| PvP skill balance | All CC durations halved in PvP contested zones (existing rule in combat-system.md Section 8.1) |
| Shadowblade Reaper stacking | Kill-chain damage bonus hard-capped at +5d6 (5 kills); prevents runaway DPS in dungeons with many weak enemies |
| Multiple Clerics — Mass Heal overlap | If two Clerics cast Mass Heal in the same server tick, each heal resolves independently but both apply (no de-duplication): this is intentional and rewards coordinated healer parties |
| Cleric Miracle revival | Only one Miracle can be active per raid encounter; the "dead this combat" state is tracked server-side (see Technical Notes 12.6) |
| Bard Bardic Inspiration overwrite | New Inspiration die replaces the old one on the same ally; client shows updated die size immediately |
| Phantom Mirage decoy entities | Cap 2 active Mirage decoys per player; in PvP zones, the WIS save is mandatory and server-authoritative per attack (not per round) |
| Captivate / Hypnotic Refrain in PvP | Paralysis and Incapacitation reduced to 1-round maximum in PvP contested zones (standard CC halving) |
| Bard Countercharm + movement | The "performing" state that triggers Countercharm is a server-side flag; any attack or incoming damage event instantly clears it |
| Sanctuary in PvP | WIS save before each attack attempt is technically correct but may frustrate PvP pacing — see OQ-11 |

---

## 12. Technical Notes for CTO

### 12.1 Data Model

```
SkillTree {
  classId: string
  branches: [
    {
      id: "guardian" | "berserker" | "assassin" | "phantom" | ...
      passive: SkillEffect
      skills: Skill[]
    }
  ]
}

Skill {
  id: string              // namespaced: e.g. "shadowblade_assassin_backstab"
  tier: 1 | 2 | 3 | 4
  tpCost: 1 | 2 | 3
  levelRequirement: number
  prerequisites: string[]   // array of skill IDs
  type: "passive" | "active_action" | "active_bonus" | "active_reaction"
  effect: SkillEffect
}

PlayerSkillState {
  playerId: string
  classId: string
  talentPointsTotal: number        // = character level
  talentPointsSpent: number
  unlockedSkills: string[]         // array of skill IDs
}
```

**Skill ID namespacing:** Skill IDs must be globally unique across all classes. Use the format `{class}_{branch}_{skill_slug}` (e.g. `shadowblade_assassin_backstab`, `cleric_divinehealer_cure_wounds`, `bard_maestro_cutting_words`). This prevents collision between same-named abilities across classes.

### 12.2 Server Authority

- All TP award and spend logic must be **server-side only**. Never trust client-submitted TP counts.
- Skill unlock validation on spend: verify `levelRequirement ≤ player.level` AND all `prerequisites` are in `unlockedSkills` AND `talentPointsSpent + tpCost ≤ talentPointsTotal`.
- Active skill triggers are sent as ability intent messages from client; server validates the skill is unlocked before resolving.

### 12.3 Passive Application

Passives are applied at character load and re-applied on skill unlock. No polling required — apply on state change events:
- `player_level_up` → re-evaluate passive bonuses
- `skill_unlocked` → add passive effect to character state
- `skill_reset` → remove all passive effects and recompute from current `unlockedSkills`

### 12.4 Animal Companion (Ranger Warden)

The Animal Companion is an **NPC entity** server-side, spawned in the player's zone instance on Warden branch activation. It must:
- Pathfind autonomously toward the player's current target
- Be eligible for AoE damage from enemies (can die)
- Not count toward party size cap (it is not a player)
- Not generate aggro threat (avoids disrupting the tank's threat table)
- Persist on zone transitions (despawn + respawn at destination)

### 12.5 Respec Implementation

On respec:
1. Set `unlockedSkills` to `[]`
2. Set `talentPointsSpent` to `0`
3. Remove all passive effects from character state
4. Recompute all stats from base
5. Deduct respec gold cost from player wallet (atomic transaction)
6. Emit `skill_reset` event to client for UI refresh

### 12.6 Shadowblade — Hidden State

Hidden is already a binary server-side status flag (used by Ranger Camouflage). Shadowblade sources (Shadowstep, Shadow Strike, Phantom Shroud) must use the same flag with source tracking so multiple sources can set/clear it independently. A Hidden player becomes visible server-side when they attack or take damage — the existing Camouflage break logic applies.

**Reaper kill-chain tracking:** Maintain a per-combat `reaperStacks` counter (integer, 0–5) on PlayerCombatState. Increment on confirmed kill event; reset on `combat_end`. Each stack adds +1d6 to all outgoing damage rolls.

### 12.7 Shadowblade — Mirage Decoys

Two NPC decoy entities with 1 HP each, spawned at runtime as lightweight NPC objects with no AI. Each attack directed at the player while Mirage is active requires a server-side WIS save roll; on fail, the attack resolves against a decoy NPC instead. Decoys do not generate threat or aggro events.

**Void Step through walls:** The destination tile must pass a `is_valid_walkable_tile()` check even though line-of-sight is bypassed. Flag puzzle zones (dungeon lever rooms, etc.) with a `no_ethereal_transit` zone flag — Void Step returns an error if the destination is in a flagged zone (see OQ-10).

### 12.8 Cleric — Heal Over Time (HOT) System

Prayer of Mending and Sacred Ground overflow both require periodic heal events. Server must process:
- `hot_tick` events on each player's combat turn start (not on server clock tick — avoids latency drift)
- HOT stacks stored on `PlayerCombatState.activeHots[]` with remaining duration in rounds
- Sacred Ground overflow: fires once per heal action, not per tick; implemented as a separate micro-heal broadcast to players within 10ft of the target

**KO-window for Revive and Miracle:** When a player reaches 0 HP, the server transitions them to `DOWNED` state (not `DEAD`) for a configurable window (recommend: 10 seconds). During this window, Revive can restore them. After the window expires, state transitions to `DEAD` and Revive no longer applies. Miracle's "died this combat" revival works only if the player's session persists in the zone — confirm with CTO whether dead-player session eviction timing conflicts with Miracle's cast time (~1 second). See OQ-8.

### 12.9 Bard — Random Behavior (Cacophony)

Cacophony's random 1d8 roll per affected creature per turn must be server-authoritative. For NPC entities: server controls the random action selection and executes it directly. For player characters: **do not override player controls**. Design intent (see OQ-9) is that Cacophony affects only NPC entities; players under Cacophony should receive a Heavy Disorientation debuff (disadvantage on all rolls, −2 to AC) instead of truly random actions. CEO to confirm.

### 12.10 Bard — Party-Wide Buffs

Symphony of Might and similar party-wide buffs must broadcast to all party members within range at the moment of cast, then apply/remove as players enter/leave the radius if Concentration is maintained. Use the existing party broadcast system (confirmed available from guild system RPG-76). Buff state stored on each `PlayerCombatState` — do not store centrally to avoid single-point invalidation on Bard disconnection.

---

## 13. Open Questions

| # | Question | Status | Decision |
|---|---|---|---|
| OQ-1 | Should Taunt cost 1 TP or a Bonus Action? Currently: Action. | **Resolved (CEO 2026-04-19)** | 1 TP is correct. Taunt is a core Guardian identity skill and should be accessible early. |
| OQ-2 | Animal Companion death: respawn timer (30s) or immediately after combat? | **Resolved (CEO 2026-04-19)** | Respec cost of 50g × level approved. |
| OQ-3 | Respec once-per-week limit: confirm cadence or relax to unlimited with gold gate only. | **Resolved (CEO 2026-04-19)** | 50g × level approved as designed. Passive vs. active skills ratio approved — CTO to flag if implementation complexity changes the calculus. |
| OQ-4 | Reality Fracture balance: 5th-slot + once-per-long-rest gate sufficient, or add cooldown? | **Open — CTO** | CTO to assess whether a 3-turn cooldown + 30% max HP cost is self-limiting in PvP. Reduce to 20% HP cost if needed for balance. |
| OQ-5 | Animal Companion NPC entity: confirm feasibility within current quest/NPC service architecture. | **Open — CTO** | CTO to confirm NPC entity approach is feasible. |
| OQ-6 | Multiclass/prestige system: confirm deferred post-MVP; ensure data model does not block it. | **Resolved (CEO 2026-04-19)** | Confirmed deferred. Right call for launch scope — flag as post-launch roadmap item. |
| OQ-7 | Shadowblade Reaper: how is "this combat" defined for stack reset — on zone exit, or on combat-state-cleared event? | **Open — CTO** | CTO to confirm `combat_end` event timing and whether it fires reliably on mob-wipe, zone exit, and manual disengage. |
| OQ-8 | Cleric Miracle — revival of allies who died this combat: does the server retain the DOWNED/DEAD player state long enough for the spell to function? | **Open — CTO** | Depends on KO-window implementation (see Technical Note 12.8). CTO to confirm 10-second DOWNED window is feasible and that dead-player session is not evicted before Miracle resolves. |
| OQ-9 | Bard Cacophony random behavior on player characters: should players be truly randomised or instead receive a Heavy Disorientation debuff? | **Open — CEO** | Design intent: random action override for NPCs only; players get disadvantage-based debuff. CEO to confirm or override. |
| OQ-10 | Void Step through walls in dungeon puzzle zones: confirm `no_ethereal_transit` zone flag approach and who is responsible for flagging puzzle rooms. | **Open — CTO + CEO** | CTO to confirm zone flag is implementable. CEO to confirm which zones are puzzle-gated and should restrict Void Step. |
| OQ-11 | Cleric Sanctuary in PvP: WIS save per attack attempt may be disruptive to PvP pacing. Reduce to 1 application per Cleric per combat in PvP zones, or cap duration to 10s in PvP? | **Open — CEO** | Balance call. CEO to decide: full Sanctuary in PvP, capped duration, or limited applications. |
| OQ-12 | Cleric class naming collision: "Ranger Warden Branch" vs. "Cleric (Warden)" class title. Recommend: rename Cleric display name to Warden, or rename Ranger branch to Naturalist. | **Open — CEO** | CEO to pick display name resolution before UI implementation begins. |

---

## Version History

| Version | Date | Summary |
|---|---|---|
| 1.0 | 2026-04-19 | Initial complete draft — Knight, Archmage, Ranger (3 classes × 2 branches × 10 skills each); full talent point economy; MMO/tech notes. ([RPG-77](/RPG/issues/RPG-77)) |
| 2.0 | 2026-04-19 | Added Shadowblade, Cleric (Warden), Bard (3 classes × 2 branches × 10 skills each); updated branch colours table; expanded MMO scaling, technical notes, and open questions. ([RPG-80](/RPG/issues/RPG-80)) |
