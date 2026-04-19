# Darkwood Forest — Zone 2 Design Document
**GDD Key:** `darkwood-forest-zone2`
**Issue:** [RPG-73](/RPG/issues/RPG-73)
**Version:** 1.0
**Date:** 2026-04-19
**Author:** Game Designer
**Status:** Draft — Awaiting CTO feasibility review + Asset Designer coordination

> **Naming note:** The overworld map (v1.0) refers to this region as "Thornwood Forest" (Region 2). This GDD uses the CEO-specified working title **Darkwood Forest**. Final naming should be confirmed by CEO before the zone is seeded. Zone ID slugs below use `darkwood-*` and will need reconciliation if the Thornwood naming is retained. See Open Questions OQ-1.

---

## Table of Contents

1. Overview & Design Intent
2. Player Experience Goals
3. Zone Layout & Map Design
4. Progression Entry — Discovery & Unlock from Starter Zone
5. Enemy Roster
6. NPC Concept List
7. Quest Hooks (5+)
8. Loot Table Outline
9. MMO Scaling Considerations
10. Technical Notes for CTO
11. Open Questions
12. Version History

---

## 1. Overview & Design Intent

Darkwood Forest is the **second major explorable zone** in AETHERMOOR, designed for players graduating from the Starter Zone (Millhaven, Level 1–5) and progressing through to Level 15. It serves three design purposes:

1. **Escalation** — It meaningfully raises the threat level, enemy variety, and environmental complexity compared to the Starter Zone, teaching players to read hazards and use their toolkit.
2. **World-building anchor** — Darkwood Forest is the player's first encounter with the wider AETHERMOOR lore: ancient ruins, the Rootbinder's corruption spreading through the natural world, and the conflict between the Verdant Pact (forest guardians) and Aetheric Order (scholars of containment).
3. **Replayability hook** — The zone spans Levels 5–15, giving it enough depth range that both freshly graduated players and mid-game characters have reasons to return (elite enemies, resource nodes, world events, faction questing).

**Aesthetic identity:** Dense ancient woodland where beauty and rot coexist. The canopy is thick enough to fracture sunlight into pillars. Glowing fungi, bioluminescent root systems, and corrupted clearings establish visual contrast between the living forest and the spreading Blight. The zone should feel *earned* — larger and more dangerous than anything in Millhaven, but still navigable solo.

---

## 2. Player Experience Goals

| # | Goal | How it manifests |
|---|---|---|
| G-1 | First sense of real danger | Enemy encounters can kill careless players; patrol patterns must be read |
| G-2 | Reward exploration | Hidden paths, buried lore, secret fishing spot, optional dungeon wing access |
| G-3 | Introduce faction tension | Both Verdant Pact and Aetheric Order have camps here; player neutral by default but must choose allegiance for quest resolution |
| G-4 | Layer narrative depth | Zone lore reveals the Blight is not random — it follows Rootbinder influence patterns |
| G-5 | Support grouping | Elite enemies and the zone dungeon require 2–4 players at the appropriate level; solo play is viable for overworld content |
| G-6 | Mobile-friendly pacing | Zone entry point (Greywood Crossing) is a safe rest hub; players can log out and return without losing significant progress |

---

## 3. Zone Layout & Map Design

### 3.1 Sub-Zone Register

Darkwood Forest is divided into three sub-zones with escalating level ranges, matching the overworld map traversal model.

| Zone ID | Name | Level Range | Max Players/Shard | Key Connects |
|---|---|---|---|---|
| `darkwood-edge` | Darkwood Edge | 5–8 | 50 | `millhaven-fields`, `aethermoor-city`, `darkwood-heart` |
| `darkwood-heart` | Darkwood Heart | 8–12 | 50 | `darkwood-edge`, `darkwood-depths`, `darkwood-crossroads` |
| `darkwood-depths` | Darkwood Depths | 11–15 | 50 | `darkwood-heart`, `goblin-wastes-border`, `blighted-vault-entrance` |
| `darkwood-crossroads` | Darkwood Crossroads | 8–12 | 100 | `darkwood-heart`, `goblin-wastes-border` |

> `darkwood-crossroads` is the PvP-contested sub-zone (Verdant Pact vs Aetheric Order), matching the overworld map's Thornwood Crossroads design. It controls Lumber and Herb nodes.

### 3.2 Key Landmarks & Points of Interest

#### Darkwood Edge
| Landmark | Type | Description |
|---|---|---|
| **Greywood Crossing** | Village / Quest Hub | Small, fortified waystation at the forest border. Verdant Pact rangers maintain it. Services: Inn, Notice Board, basic gear vendor. First safe respawn point in zone. |
| **The Treeline Gate** | Environmental POI | An ancient stone arch overgrown with roots — the visual threshold between open grassland and dense forest. Zone entry text displays here. |
| **Old Ranger's Watchtower** | Secret POI | Collapsed tower interior accessible via jump-puzzle (Zelda-style). Contains a lore scroll: *"The Roots Remember."* |
| **Mossglen Stream** | Fishing Spot | Gentle stream, Common/Uncommon fish. No level requirement. Player cap: 8. |
| **Goblin Outpost (Fallen)** | Combat POI | Abandoned goblin camp — the goblins fled from something deeper in the forest. Spawn: Darkwood Stalker packs. Contains a clue item for Quest Hook Q-2. |

#### Darkwood Heart
| Landmark | Type | Description |
|---|---|---|
| **The Whispering Stones** | Lore POI | A ring of nine standing stones carved with pre-Aethermoor script. Interacting with each activates a lore fragment (collectible: "Stones of the First Root" — 9 pieces). Collecting all 9 grants the passive title *Stone-Reader*. |
| **Darkwood Sanctuary** | Quest Hub | Hidden Verdant Pact druid camp, concealed by illusion (revealed by Quest Q-1). Contains: Druid Questmaster, Herbalist merchant, campfire respawn point, faction board. |
| **Blight's Edge** | Environmental Hazard Zone | Corrupted clearing where the ground glows sickly purple. Enemies here have +20% HP. The corruption visually creeps 2 tiles outward from a central dead tree (server-side world state flag). |
| **The Sunken Glade** | Fishing Spot (Night Only) | Partially flooded clearing. Active 18:00–06:00 game time. Uncommon/Rare fish. Level 8+ required. Player cap: 6. |
| **Blighted Vault Approach** | Dungeon Entry Path | The forested path leading to the zone dungeon. Requires completion of Quest Q-3 to fully unlock the lower wing (Silence Rune not required — uses a different key item: the Druid's Seal). |

#### Darkwood Depths
| Landmark | Type | Description |
|---|---|---|
| **Ravenswood Ruins** | POI + Dungeon Entrance | Crumbling pre-Aethermoor temple complex. Main dungeon entrance: **The Blighted Vault** (see Dungeon entry). Ancient architecture — stone columns, submerged walkways. |
| **The Root Altar** | World-Event Spawn / Boss POI | A massive corrupted root mass — the Blightbear (zone mini-boss) patrols here. World event: *Root Surge* (see §9). |
| **Aetheric Order Outpost** | Quest Hub | Rival camp to Darkwood Sanctuary. Aetheric Order scholars studying the Blight spread. Contains: Order Questmaster, Alchemist merchant (fire/light resistance gear), campfire respawn point. |
| **Verdant Spring** | Secret POI | Hidden underground spring discovered by solving the Whispering Stones collectible. Contains a rare herb spawn (respawn: 30 min server-side) and a chest: guaranteed Uncommon gear drop. |
| **The Deep Canopy** | Environmental POI | Where the tree canopy is so thick it creates near-total darkness. Torch or Light spell required for full exploration (environmental light mechanic — first appearance in the game). |

### 3.3 Zone Traversal Diagram

```
DARKWOOD FOREST — TRAVERSAL (Zone 2)
══════════════════════════════════════════════

  [MILLHAVEN FIELDS]       [CITY OF AETHERMOOR]
        │                          │
        └──────────┬───────────────┘
                   │
       ┌───────────▼──────────────┐
       │     DARKWOOD EDGE        │ LV 5–8
       │   darkwood-edge          │
       │   ★ Greywood Crossing    │
       │   🎣 Mossglen Stream     │
       │   🗼 Old Watchtower      │
       └───────────┬──────────────┘
                   │
       ┌───────────▼──────────────┐      ┌──────────────────────┐
       │     DARKWOOD HEART       │──────│  DARKWOOD CROSSROADS │ PvP⚔️
       │   darkwood-heart         │      │  darkwood-crossroads  │
       │   ★ Darkwood Sanctuary   │      │  LV 8–12             │
       │   ◆ Whispering Stones    │      └──────────────────────┘
       │   🎣 Sunken Glade (🌙)  │
       │   ⚠ Blight's Edge       │
       └───────────┬──────────────┘
                   │
       ┌───────────▼──────────────┐
       │     DARKWOOD DEPTHS      │ LV 11–15
       │   darkwood-depths        │
       │   🏰 Blighted Vault Ent. │
       │   ⚔ Root Altar (Boss)   │
       │   ◎ Aetheric Order Camp  │
       │   🌿 Verdant Spring★     │
       └───────────┬──────────────┘
                   │
         [GOBLIN WASTES BORDER]

LEGEND:
  ★ = Respawn/Rest Point   🏰 = Dungeon Entrance
  ⚔ = PvP / Boss          🎣 = Fishing Spot
  ◆ = Collectible POI      🌙 = Night-only content
  ⚠ = Hazard Zone          ◎ = Faction Outpost
```

---

## 4. Progression Entry — Discovery & Unlock from Starter Zone

### 4.1 How Players Find Darkwood Forest

Darkwood Forest is **not gated** — players can enter at any level — but two progression paths make it the natural second zone:

**Path A — Millhaven Fields → Darkwood Edge (Organic Discovery)**
- Millhaven Fields connects directly to `darkwood-edge` at its northern edge. After completing the Millhaven starter quests and reaching Level 3–5, the Notice Board at Millhaven posts a quest: *"Trouble at Greywood Crossing"* (Q-1 gateway quest). This quest NPC, Ranger Wren, mentions the forest and offers to guide the player.
- Visual design: the forest canopy is visible from the Millhaven Fields northern boundary. At night, bioluminescent glow is visible — a deliberate visual hook that rewards curiosity.

**Path B — City of Aethermoor → Darkwood Edge (Institutional Hook)**
- From the City, players who speak to the Verdant Pact Faction Envoy (Sylvara Dawnbloom) at Level 5+ receive a quest sending them to Darkwood Sanctuary. This hooks Order-aligned players into the Darkwood narrative from the faction angle.

### 4.2 First-Entry Experience

1. Player crosses the Treeline Gate → Zone entry text fades in (4 seconds, dismissable):
   > *"The Darkwood earned its name honestly. Ancient trees press close overhead, swallowing the sun. The air smells of rain and something older — a faint sweetness that should be pleasant but isn't. Somewhere ahead, a forest settlement is sending up smoke. Somewhere deeper, something is making the goblins run."*

2. Greywood Crossing is within 30 tiles of the entry point — players reach a safe respawn point quickly without mandatory combat.

3. Ranger Wren (at Greywood Crossing) gives the player a brief orientation and starts Quest Q-1.

### 4.3 Unlock Dependencies for Sub-Zones

| Sub-Zone | Unlock Condition |
|---|---|
| `darkwood-edge` | None — open from Level 1 (dangerous for L1–4) |
| `darkwood-heart` | Reaching `darkwood-edge` and defeating the Goblin Outpost event (or simply walking north — no hard lock) |
| `darkwood-depths` | No hard lock; enemy danger is the natural gate (Level 11+ strongly implied) |
| Darkwood Sanctuary (hidden) | Completing Q-1 — illusion dispelled |
| Blighted Vault lower wing | Obtaining the Druid's Seal item from Quest Q-3 |
| The Deep Canopy exploration | Torch item or Light cantrip (Mage/Cleric class ability) |
| Verdant Spring | Completing all 9 Whispering Stones collectibles |

---

## 5. Enemy Roster

### Design Principles
- Enemies escalate mechanically as players push deeper (Edge → Heart → Depths).
- All enemies use the combat system's D&D-adjacent stat block format (HP, AC, Attack Bonus, Damage, Save DC for abilities).
- Blight-corrupted enemies have a shared visual language: purple/black discolouration, glowing fissures. Designers should consult Asset Designer on the corruption shader.
- Pack tactics are used on Levels 5–9 enemies; individual power and special abilities dominate Levels 10–15.

### Enemy Stat Blocks

#### E-1: Darkwood Stalker (Level 5–7 encounter)
*A wolf-like predator warped by proximity to the Blight. Faster than its natural counterpart and capable of short-range teleportation through shadows.*

| Stat | Value |
|---|---|
| HP | 52 |
| AC | 13 |
| Attack Bonus | +5 |
| Damage (Bite) | 1d8 + 3 piercing |
| Speed | 40 tiles/round |
| XP | 150 |
| Loot (Common) | Stalker Fang, Shadowfur Pelt |

**Special Ability — Shadow Step (Recharge 5–6):** Teleports up to 6 tiles to any unoccupied space. Triggers on first drop below 50% HP. Cooldown: 18 seconds (3 combat rounds).

**Encounter notes:** Spawns in packs of 2–4. Pack leader has +10 HP. Fleeing behaviour triggered if pack drops below 2 members.

**Spawn locations:** Millhaven Fields border, Darkwood Edge patrol routes, Goblin Outpost surrounds.

---

#### E-2: Thornweb Spider (Level 7–10 encounter)
*An unnaturally large spider that weaves webs of petrified vine rather than silk — an adaptation unique to the Darkwood. The web contains residual Blight energy that slows movement.*

| Stat | Value |
|---|---|
| HP | 78 |
| AC | 14 |
| Attack Bonus | +6 |
| Damage (Fangs) | 1d10 + 4 piercing + 1d4 poison |
| Speed | 30 tiles/round (ignores web terrain) |
| XP | 220 |
| Loot (Common) | Petrified Websilk, Venom Gland |
| Loot (Uncommon, 20%) | Thornweb Bracers (light armour, DEX +1) |

**Special Ability — Web Trap (Recharge 4–6):** Launches a web projectile (range 8 tiles). On hit: target is *Restrained* (speed 0) for 6 seconds (1 round). DEX Saving Throw DC 14 to resist.

**Special Ability — Egg Sac (Passive):** On death, 40% chance to spawn 2 Spiderlings (1 HP each, 1d4 damage, AC 10). Spiderlings despawn after 18 seconds.

**Spawn locations:** Darkwood Heart undergrowth, tree canopy areas, near Blight's Edge.

---

#### E-3: Corrupted Treant Sprout (Level 6–9 encounter)
*A young treant (sapling form) that has been fully consumed by the Blight. Its bark is blackened, its leaves have become razor-edged. Unlike elder treants, it lacks restraint — it attacks any living thing indiscriminately.*

| Stat | Value |
|---|---|
| HP | 105 |
| AC | 15 (bark armour) |
| Attack Bonus | +6 |
| Damage (Slam) | 2d6 + 4 bludgeoning |
| Speed | 20 tiles/round |
| XP | 300 |
| Loot (Common) | Blighted Bark, Corrupted Sap |
| Loot (Uncommon, 15%) | Treant Heartwood (crafting: Blight-resistant armour) |

**Special Ability — Root Burst (Cooldown 24s):** Slams the ground, sending roots in a 3-tile radius. Targets within radius take 2d6 bludgeoning and are *Knocked Prone* (spend Movement to stand). CON Saving Throw DC 14 to avoid prone.

**Special Ability — Bark Regeneration (Passive):** Regenerates 5 HP per combat round while above 30% HP. Fire damage suppresses regeneration for 12 seconds.

**Encounter notes:** Solitary enemy. Alert radius: 8 tiles. Slow movement makes it avoidable — experienced players can bypass if not seeking XP.

**Spawn locations:** Darkwood Heart near Blight's Edge, Darkwood Depths near Root Altar.

---

#### E-4: Shadowvine Crawler (Level 8–11 encounter)
*A mass of animated dark vines that has achieved a rudimentary collective consciousness through the Blight. It moves like a swarm, constricts like a constrictor, and is nearly impossible to kill with conventional blows — fire and radiant damage are its weaknesses.*

| Stat | Value |
|---|---|
| HP | 130 |
| AC | 13 (but: slashing/piercing damage reduced by 5) |
| Attack Bonus | +7 |
| Damage (Constrict) | 2d8 + 5 bludgeoning; target is *Grappled* (auto) |
| Speed | 25 tiles/round |
| XP | 380 |
| Loot (Common) | Darkwood Vine, Blight Residue |
| Loot (Rare, 10%) | Crawler Sigil (trinket: +1 to Nature checks, +5 max HP) |

**Special Ability — Ensnare (Cooldown 30s):** Throws vines at up to 2 targets within 6 tiles. Targets must pass a STR Saving Throw DC 15 or be *Restrained* for 12 seconds.

**Special Ability — Divide (Passive):** When reduced to 50% HP, the Crawler splits into two Crawler Halves (each with 30 HP, AC 11, basic attack only, no special abilities). The halves do not inherit loot rolls — only one loot roll occurs at the original Crawler's death.

**Spawn locations:** Darkwood Depths, near Ravenswood Ruins, Blight's Edge surrounds.

---

#### E-5: Darkwood Wraith (Level 9–13 encounter)
*The corrupted spirit of a Verdant Pact ranger who died defending the forest from the Blight's first incursion. It retains tactical intelligence — it flanks, retreats to reposition, and targets casters preferentially. It cannot be physically grappled.*

| Stat | Value |
|---|---|
| HP | 115 |
| AC | 15 (incorporeal — miss chance 25% on non-magical weapons) |
| Attack Bonus | +8 |
| Damage (Spectral Strike) | 2d6 + 5 necrotic |
| Speed | 35 tiles/round (passes through obstacles) |
| XP | 420 |
| Loot (Uncommon) | Wraith Essence |
| Loot (Rare, 15%) | Ghost-Touched Blade (weapon: +1 attack, deals necrotic on crit) |

**Special Ability — Life Drain (Cooldown 18s):** Single-target, range 4 tiles. Target takes 3d6 necrotic damage. The Wraith heals for half the damage dealt. CON Saving Throw DC 14 for half damage.

**Special Ability — Phase Step (Passive):** Can move through solid terrain (trees, rocks, walls) but must end its movement in unoccupied space. Cannot be *Restrained*.

**Special Ability — Shadow Fade (Recharge 6):** Becomes *Invisible* for 6 seconds or until it attacks. Drops invisibility immediately on using any ability.

**Encounter notes:** Spawns singly or in pairs near Ravenswood Ruins. Highly dangerous solo — strongly recommended for grouped players at Level 9–11. At Level 12+, manageable solo with a Cleric/Mage toolkit.

**Spawn locations:** Darkwood Depths, Ravenswood Ruins interior (overworld), night-only spawns in Darkwood Heart.

---

#### E-6: Blightbear (Level 11–15 encounter — Zone Mini-Boss)
*A cave bear twice the size of any natural specimen, the alpha of the Darkwood's corrupted wildlife. The Blight has fused with its skeleton, giving it armoured plating across its back and shoulders. It is territorial, aggressive, and patrols the Root Altar area.*

| Stat | Value |
|---|---|
| HP | 340 |
| AC | 17 (Blight-plated hide) |
| Attack Bonus | +9 |
| Damage (Swipe) | 2d10 + 6 slashing |
| Damage (Bite) | 2d8 + 6 piercing |
| Speed | 30 tiles/round |
| Respawn Timer | 3 hours (server-side, announced in zone chat) |
| XP | 1,200 |
| Loot (Uncommon, guaranteed) | Blightbear Hide |
| Loot (Rare, 60%) | Claws of the Deepwood (weapon or armour component) |
| Loot (Epic, 10%) | Blightbear's Heart (trinket: +15 max HP, +1 CON modifier, soulbound) |

**Special Ability — Blight Roar (Cooldown 30s):** AoE roar in 8-tile radius. All targets take 2d6 necrotic and are *Frightened* for 6 seconds (Frightened: cannot move toward the Blightbear). WIS Saving Throw DC 16 negates the Frightened condition (damage still applies on fail).

**Special Ability — Blight Charge (Cooldown 24s):** Charges in a line up to 10 tiles. All targets in the line take 3d8 bludgeoning and are *Knocked Prone*. DEX Saving Throw DC 15 to avoid prone (damage still applies).

**Special Ability — Armoured Hide (Passive):** Slashing and piercing damage reduced by 4 (minimum 1). Fire and lightning damage bypass this reduction entirely.

**Phase 2 (Below 50% HP) — Blight Frenzy:** Attack bonus increases to +10. Gains an additional Bonus Action attack (Bite) each round. Blight Roar recharge becomes 18s.

**Encounter notes:** Intended as 2–4 player content at Level 11–13, or solo at Level 14–15 with good gear. World boss rules apply: loot distributed to all players who dealt ≥5% damage. Zone chat notification 30 seconds before respawn.

**Spawn locations:** Root Altar (Darkwood Depths), permanent spawn point — patrols a 15-tile radius around the altar.

---

### Enemy Summary Table

| ID | Name | Level Range | HP | AC | Key Mechanic | Group Size |
|---|---|---|---|---|---|---|
| E-1 | Darkwood Stalker | 5–7 | 52 | 13 | Shadow Step teleport | 2–4 (pack) |
| E-2 | Thornweb Spider | 7–10 | 78 | 14 | Web Trap (Restrain) | 1–2 |
| E-3 | Corrupted Treant Sprout | 6–9 | 105 | 15 | Root Burst, Bark Regen | 1 |
| E-4 | Shadowvine Crawler | 8–11 | 130 | 13 | Divide, Ensnare | 1 |
| E-5 | Darkwood Wraith | 9–13 | 115 | 15 | Incorporeal, Phase Step | 1–2 |
| E-6 | Blightbear | 11–15 | 340 | 17 | Blight Frenzy (Phase 2) | Boss (solo/group) |

---

## 6. NPC Concept List

### Greywood Crossing (Darkwood Edge)

| Name | Role | Faction | Notes |
|---|---|---|---|
| **Ranger Wren** | Quest Giver (Gateway) | Verdant Pact | Young ranger stationed at the Crossing. Gives Q-1, Q-2. Warm but worried. Potential recurring character. |
| **Brynn Mossveil** | Innkeeper / Merchant | Neutral | Runs the waystation inn. Sells basic food/rest. Side quest: *"Brynn's Last Barrel"* (ale delivery — comedy side quest, low stakes). |
| **Merchant Callum** | General Vendor | Neutral | Sells Level 5–8 gear (Common/Uncommon quality), crafting materials, torches. Rotating stock (6-hour cycle). |
| **Old Hob** | Lore NPC | Neutral | Former woodcutter, missing a hand. Gives context on how the forest changed. Does not give quests — pure environmental lore character. Memorable dialogue hook: *"I've been cutting wood in that forest for thirty years. The trees grew back. Now they don't."* |

### Darkwood Sanctuary (Darkwood Heart — Hidden)

| Name | Role | Faction | Notes |
|---|---|---|---|
| **Archdruid Sylvenne** | Primary Quest Giver (Q-3, Q-4) | Verdant Pact | Elder druid who has watched the Blight spread for years. Gives the Druid's Seal (Q-3). Authoritative, pragmatic, carries sadness. Central NPC for Verdant Pact faction storyline. |
| **Herbalist Dusk** | Merchant | Verdant Pact | Sells zone-specific herbs, Uncommon alchemy reagents, anti-poison consumables. Rare bait stock (for the Sunken Glade fishing spot). |
| **Scout Tam** | Side Quest Giver (Q-5) | Verdant Pact | Young Pact scout who asks players to investigate something she found in the ruins. Nervous energy — this is her first real mission. |

### Aetheric Order Outpost (Darkwood Depths)

| Name | Role | Faction | Notes |
|---|---|---|---|
| **Scholar-Commander Vehn** | Quest Giver (Rival Q-3 path) | Aetheric Order | The Order wants the Druid's Seal for their own containment experiments. Vehn can offer an alternative Q-3 resolution: deliver the seal to the Order instead of using it to unlock the Vault. Morally ambiguous — his goals are also defensible. |
| **Alchemist Pell** | Merchant | Aetheric Order | Sells fire/light resistance gear, arcane reagents, and scrolls. Slightly overpriced vs. the Sanctuary herbalist — Aetheric Order aesthetic. |
| **Garrison Guard Otha** | Combat Tutorial NPC | Aetheric Order | Gives an optional group challenge quest: defend the outpost from a Shadowvine Crawler assault. Unlocks a cosmetic reward (Aetheric Order tabard) if completed. |

### Wandering / Rare NPCs

| Name | Role | Notes |
|---|---|---|
| **Thessa's Ghost** | Passive Lore NPC | Appears near the Whispering Stones at night only. References the zone-lore continuity from the alpha Whispering Forest. Non-hostile. |
| **The Wandering Rootbinder Cultist** | Hidden NPC (Secret Quest Trigger) | Found only by players who have completed all 9 Whispering Stones. Gives a cryptic item (Rootbinder Shard) that unlocks additional dialogue with Grand Archivist Selemeth in the City. No quest marker — discovery only. |

---

## 7. Quest Hooks

These are design-level hooks for the Quest Writer to develop into full scripts. Each includes the hook premise, NPC owner, and reward outline. Full dialogue trees are out of scope for this GDD.

### Q-1: The Goblin Retreat (Gateway Quest)
**NPC:** Ranger Wren (Greywood Crossing)
**Hook:** Wren has noticed the goblin clans abandoned their camps at the forest border — not because they were driven out by players, but because something scared them into the open. She asks the player to investigate the Goblin Outpost in Darkwood Edge and bring back any evidence of what they left behind.
**Objective:** Explore the fallen Goblin Outpost. Collect the "Scrawled Warning Note" (quest item, goblin-scrawled: *"Go deeper — die. Stay here — also die. We go south."*). Return to Wren.
**Reward:** 250 XP, 10 Silver, Greywood Crossing unlocked as respawn point. Reveals Darkwood Sanctuary location on minimap.
**Design note:** This quest is the zone's gateway — it should be completable at Level 5, be primarily exploration-based with minimal mandatory combat, and set the tone for the Blight threat.

---

### Q-2: What the Stalkers Carry (Investigation Quest)
**NPC:** Ranger Wren (Greywood Crossing)
**Hook:** Wren has recovered a collar from a dead Darkwood Stalker — it bears an Aetheric Order crest. The Order had apparently been using the wolves for controlled Blight exposure experiments. She asks the player to find out more.
**Objective:** Track 5 Darkwood Stalkers and loot them for Blight Collar Fragments. Return to Wren. Then visit Scholar-Commander Vehn at the Aetheric Order Outpost for his side of the story.
**Reward:** 400 XP, 15 Silver, Stalker Fang×3 (crafting mat). Unlocks the Aetheric Order Outpost on minimap.
**Design note:** This quest introduces the moral ambiguity of the Order — Vehn has a reasonable argument for his experiments but used unethical methods. It bridges the Verdant Pact/Aetheric Order faction tension without forcing a choice yet.

---

### Q-3: The Druid's Seal (Zone Progression Quest)
**NPC:** Archdruid Sylvenne (Darkwood Sanctuary) — *or* Scholar-Commander Vehn (Aetheric Order Outpost)
**Hook:** The lower wing of the Blighted Vault can only be unlocked by the Druid's Seal — an ancient artifact held by Sylvenne. Both Sylvenne and Vehn want to control access to it for different reasons.

**Path A (Verdant Pact):** Sylvenne gives the Seal freely if the player has completed Q-1 and Q-2 and commits to using it to cleanse the Vault's inner sanctum. Reward: Seal + Verdant Pact Reputation +200 + 500 XP.

**Path B (Aetheric Order):** Vehn asks the player to steal or persuade Sylvenne to hand over the Seal for Order containment research. Reward: Seal + Aetheric Order Reputation +200 + 500 XP + Arcane Lens (Uncommon trinket).

**Design note:** This is the zone's faction choice pivot. The player can only complete one path per character. Choosing either path does not lock out the other faction's quests — but changes NPC dialogue throughout the zone.

---

### Q-4: Bark and Bone (Lore Quest — Verdant Pact path)
**NPC:** Archdruid Sylvenne (Darkwood Sanctuary)
**Hook:** Sylvenne believes the Corrupted Treant Sprouts can be saved — the corruption hasn't fully consumed their root system. She asks the player to collect Corrupted Sap from 4 Treant Sprouts (requires killing them) and a Rootbinder Trace sample from Blight's Edge for her research.
**Objective:** Kill 4 Corrupted Treant Sprouts (loot Corrupted Sap). Interact with the Blight's Edge central dead tree (collect sample). Return to Sylvenne.
**Reward:** 600 XP, 20 Silver, Blight-Resistant Cloak (Uncommon: +2 AC, resistance to necrotic damage while in Darkwood zones). Sylvenne provides lore insight into the Rootbinder's influence — advances Act 1 narrative.

---

### Q-5: What Scout Tam Found (Mystery/Combat Quest)
**NPC:** Scout Tam (Darkwood Sanctuary)
**Hook:** Tam found a cache of Aetheric Order equipment hidden inside Ravenswood Ruins — she thinks the Order has been operating inside the ruins without the Pact's knowledge. She asks the player to investigate and retrieve proof.
**Objective:** Enter Ravenswood Ruins (overworld, not dungeon). Locate the hidden cache (requires interacting with a specific destructible wall — environmental puzzle). Defend the area from 3 waves of Shadowvine Crawlers that spawn upon disturbing the cache. Collect the Order's Research Journal. Return to Tam.
**Reward:** 550 XP, 18 Silver, Research Journal (can be handed to either Sylvenne or Vehn for different faction rep outcomes). Tam becomes a permanent friendly NPC in the Sanctuary with ambient zone gossip dialogue.
**Design note:** The environmental puzzle (destructible wall) should be signalled by a visible crack texture and a faint audio cue — not a quest marker. Rewards observant players.

---

### Q-6 (Bonus): The Blightbear Hunt (Optional World Boss Quest)
**NPC:** Notice Board (Greywood Crossing and Darkwood Sanctuary)
**Hook:** A standing bounty on the Blightbear — posted by both factions (rare cooperation). Resets weekly (7-day timer).
**Objective:** Kill the Blightbear (E-6). Collect the Blightbear Bounty Token (auto-looted by all qualifying participants). Return to Notice Board.
**Reward:** 800 XP, 35 Silver, 1× Zone-specific gear piece (level-appropriate Rare quality, randomised from loot table). Weekly first-kill bonus: +500 XP + Bounty Hunter title (temporary, 7-day display).
**Design note:** This quest drives repeated weekly engagement with the zone mini-boss. The notice-board format avoids needing an NPC to be present while still creating a social rallying point.

---

## 8. Loot Table Outline

### 8.1 Zone Drop Tiers

| Tier | Quality | Typical Source | Drop Rate |
|---|---|---|---|
| Common | Grey | Any enemy, basic chest | 60–80% |
| Uncommon | Green | Pack leaders, rare chests, specific enemy drops | 15–25% |
| Rare | Blue | Elite enemies (E-5, E-6), dungeon chests | 8–15% |
| Epic | Purple | Blightbear (10%), Blighted Vault dungeon | 1–5% (overworld) |

### 8.2 Zone-Specific Named Items

| Item | Type | Stats | Source | Quality |
|---|---|---|---|---|
| Darkwood Stalker Cloak | Light Armour | AC +2, DEX +1, Speed +2 tiles | Crafted (2× Shadowfur Pelt + 1× Darkwood Vine) | Uncommon |
| Thornweb Bracers | Light Armour | AC +1, DEX +1, immunity to Web Trap | Thornweb Spider (20% drop) | Uncommon |
| Treant Heartwood Chestplate | Medium Armour | AC +3, CON +1, fire resistance | Crafted (3× Treant Heartwood + Corrupted Sap) | Rare |
| Ghost-Touched Blade | Weapon (Sword) | ATK +1, deals necrotic on crit, ignores 25% physical resistance | Darkwood Wraith (15% drop) | Rare |
| Claws of the Deepwood | Weapon (Fist/Claws) OR Armour Component | +2 ATK or +3 AC (crafter's choice) | Blightbear (60% drop) | Rare |
| Blightbear's Heart | Trinket | +15 max HP, +1 CON modifier (soulbound) | Blightbear (10% drop) | Epic |
| Blight-Resistant Cloak | Cloak | +2 AC, necrotic resistance in Darkwood zones | Quest Q-4 reward | Uncommon |
| Crawler Sigil | Trinket | +1 Nature checks, +5 max HP | Shadowvine Crawler (10% drop) | Rare |
| Verdant Spring Herb (×3) | Crafting Material | Used in Uncommon alchemy recipes | Verdant Spring (30-min respawn) | Uncommon Mat |
| Petrified Websilk | Crafting Material | Used in light armour crafting (DEX focus) | Thornweb Spider | Common Mat |
| Blighted Bark | Crafting Material | Used in Blight-resistance gear recipes | Corrupted Treant Sprout | Common Mat |
| Wraith Essence | Crafting Material | Used in arcane weapon enchanting (necrotic) | Darkwood Wraith | Uncommon Mat |

### 8.3 Reward Tiers by Enemy

| Enemy | Common Drop | Uncommon Drop | Rare Drop |
|---|---|---|---|
| Darkwood Stalker | Stalker Fang, Shadowfur Pelt | — | — |
| Thornweb Spider | Petrified Websilk, Venom Gland | Thornweb Bracers (20%) | — |
| Corrupted Treant Sprout | Blighted Bark, Corrupted Sap | Treant Heartwood (15%) | — |
| Shadowvine Crawler | Darkwood Vine, Blight Residue | — | Crawler Sigil (10%) |
| Darkwood Wraith | Wraith Essence | Ghost-Touched Blade (15%) | — |
| Blightbear | Blightbear Hide (guaranteed) | Claws of the Deepwood (60%) | Blightbear's Heart (10%) |

### 8.4 Fishing Loot

| Fishing Spot | Fish (Common) | Fish (Uncommon) | Fish (Rare) | Restriction |
|---|---|---|---|---|
| Mossglen Stream | Silverscale, Mudfish | Forest Trout | — | None |
| Sunken Glade | Gloomfin, Mudfish | Moonbass, Forest Trout | Blightfin Eel | Night only (18:00–06:00) |

> Blightfin Eel: Used in alchemy (high-tier reagent) and as a cooking ingredient (+10 max HP buff, 1hr). Market value: ~50 Silver each.

---

## 9. MMO Scaling Considerations

| Concern | Design Decision |
|---|---|
| Zone shard capacity | `darkwood-edge` / `darkwood-heart` / `darkwood-depths`: 50 players per shard. `darkwood-crossroads` (PvP): 100 players per shard. Overflow triggers new shard; manual shard switch via Party join. |
| Enemy respawn | Standard enemies: 5-minute respawn. Pack leaders: 10-minute. Corrupted Treant Sprouts: 8-minute (slow spawn matches slow movement). Blightbear: 3-hour server-side respawn with zone-chat announcement at T-30 seconds. |
| Resource node respawn | Mossglen Stream fishing: 10-minute node cooldown per player. Verdant Spring herb: 30-minute zone-wide respawn. Crafting mat drops: no node — all from enemy kills. |
| World boss loot distribution | Blightbear loot: distributed to all players who contributed ≥5% of total damage. Epic drop (Blightbear's Heart) has one roll per kill, winner is random among qualifying players. Common/Rare rolls are individual. |
| Blight's Edge world state | The Blight's Edge corruption "creep" (visual tile spread) is a server-side world state flag. Starts at radius 2; grows to radius 5 if the Root Altar is active and no players have completed the zone's weekly cleansing event (Root Surge — see below). This is a lightweight state system — one integer per zone shard. |
| Root Surge world event | Weekly zone-wide event: the Root Altar activates, spawning waves of enemies. All players in the shard are notified. Completing the event (defend the Aetheric Order outpost + defeat Blightbear during the event window) resets the Blight's Edge corruption level. If the event fails, Blight's Edge spawns 2 additional Shadowvine Crawlers per respawn cycle until the next week. Intended as a light cooperative engagement driver. |
| PvP (darkwood-crossroads) | Standard faction PvP rules: 3-minute uncontested capture, 30-second server poll, zone-chat flip notification. Control points: Darkwood Lumber Mill, Rare Herb Garden. Controlling faction bonus: +20% crafting mat drop rate from all Darkwood enemies, Darkwood Quartermaster NPC unlocked in their faction camp. |
| Night/day cycle | Sunken Glade fishing: night-only (server-authoritative). Darkwood Wraith night spawns in `darkwood-heart` (added spawn group at night, not the only group). Thessa's Ghost NPC: night-only. All governed by server-authoritative game clock (1 real hour = 2 in-game hours). |
| Dungeon vs. overworld balance | Blighted Vault (dungeon) loot is strictly better than overworld Darkwood drops. The overworld zone remains relevant via crafting mats (not available in the dungeon), fishing, faction questing, and the Blightbear. |

---

## 10. Technical Notes for CTO

| Item | Specification |
|---|---|
| Zone registry entries | 4 new zone entries: `darkwood-edge`, `darkwood-heart`, `darkwood-depths`, `darkwood-crossroads`. Add to zone registry with bidirectional `connections` as specified in §3.1. |
| Biome enum values needed | `darkwood-edge` → `forest`. `darkwood-heart` → `forest` (dense). `darkwood-depths` → `forest` (corrupted). `darkwood-crossroads` → `forest/clearing` (PvP). No new biome enums required — existing `forest` covers these. |
| Sub-zone: Greywood Crossing | Implement as standalone zone or sub-zone of `darkwood-edge` (same pattern as Thornhaven/Verdant Canopy Village). Recommend standalone for consistency. Zone ID: `greywood-crossing`. |
| Sub-zone: Darkwood Sanctuary | Hidden zone — not visible on map or minimap until Quest Q-1 completion triggers the `REVEAL_ZONE` event for that player. Implement as a player-specific map reveal flag (not a zone lock). Zone ID: `darkwood-sanctuary`. |
| Dungeon entry | Blighted Vault: new dungeon entry POI in `darkwood-depths` zone. Dungeon ID: `blighted-vault`. Lower wing gated by player inventory check (Druid's Seal item). Implement as: on dungeon entry, check player inventory for `item_druids_seal`; if absent, display prompt: *"The inner sanctum is sealed. The Druid's Seal is required."* and block passage at lower-wing doorway tile. |
| Blight's Edge world state | Single integer per shard: `blight_radius` (range 2–5). Modified by: Root Surge event outcome (reset to 2 on success; +1 on failure, cap 5). Applied as a visual shader radius on the central dead tree tile — confirm with Asset Designer on corruption shader implementation. Broadcast to all clients in shard on change via WebSocket. |
| Root Surge world event | Weekly timer (server-side cron, not player-triggered). Announce in zone chat 10 minutes before start. Spawn waves: 3 waves × 8 Shadowvine Crawlers over 12 minutes, then Blightbear spawns at the Root Altar. Success condition: all 3 waves defeated + Blightbear defeated within 20 minutes of event start. Track via server-side event flag per shard per week. |
| Night-only content | Sunken Glade fishing and Wraith night spawns: server-authoritative time check (same system as Crystal Lake in the overworld map). Thessa's Ghost NPC: implement as a night-only NPC schedule entry. |
| Blightbear loot distribution | Use world boss loot model: track damage contribution per player (% of total HP dealt). Distribute loot rolls to all players at ≥5% contribution threshold. Epic drop: single roll, random from qualifying pool. |
| Fishing spots | Two new fishing POI entries: `darkwood-mossglen-stream` (Common/Uncommon, no restriction, cap 8) and `darkwood-sunken-glade` (Uncommon/Rare, night-only, cap 6). Tile coordinates TBD pending tile map authoring. |
| Destructible wall (Q-5) | Ravenswood Ruins has one destructible wall tile (visual: cracked stone). Interaction: `destroy_wall` action. Triggers: spawn 3 waves of Shadowvine Crawlers (wave 1: 2 Crawlers; wave 2: 3 Crawlers; wave 3: 4 Crawlers + 1 pack leader with +10 HP). Quest item `order_research_journal` available after wave 3. |
| Environmental light mechanic | Deep Canopy tiles: apply darkness overlay (shader). Torches (inventory item) or Light cantrip (class ability, Mage/Cleric) remove the overlay in a 4-tile radius. CTO to confirm whether this is a client-side shader toggle or a server-broadcast visibility state. Recommend client-side with item/ability state as the toggle input. |
| Enemy special ability timings | All cooldown values in this GDD are in real-time seconds. Server combat tick is 100ms (10 ticks/sec) — enemy AI ability cooldown tracking should be in ticks (divide seconds by 0.1). E.g., Blightbear Blight Roar: 30s = 300 ticks. |
| Enemy pack AI | Darkwood Stalker pack flee logic: if pack members ≤1, remaining Stalker has 70% chance to flee (speed boost: +10 tiles/round for 12 seconds). AI state machine: idle → alert (8-tile radius) → attack → flee. |
| Faction reputation system | Verdant Pact and Aetheric Order reputation affected by Q-3 path choice. Rep values per quest defined in §7. CTO to confirm reputation system is in scope for this zone (may be pre-existing from overworld map faction envoys). |

---

## 11. Open Questions

| # | Question | Priority | Owner |
|---|---|---|---|
| OQ-1 | **Naming reconciliation** — The overworld map (v1.0) names this region "Thornwood Forest" with zone IDs `thornwood-*`. This GDD uses "Darkwood Forest" and `darkwood-*` IDs. CEO to confirm the canonical zone name before zone registry seeding. If Thornwood is retained, all zone IDs, NPC names referencing "Darkwood," and dungeon name should be updated. | Critical | CEO |
| OQ-2 | **Blighted Vault dungeon GDD** — The Blighted Vault is referenced as the zone dungeon but its full spec (boss design, boss mechanic, room layout) is out of scope for this GDD. Should this be a follow-up RPG ticket assigned to the Game Designer, or will Quest Writer and Asset Designer handle it collaboratively? | High | CEO / Game Designer |
| OQ-3 | **Environmental light mechanic** — The Deep Canopy darkness overlay is a new mechanic not previously designed. CTO to confirm: (a) is this client-side shader with item/ability toggle, or server-broadcast visibility; (b) is the Light cantrip already implemented as a Mage/Cleric ability, or does it need to be added? | High | CTO |
| OQ-4 | **Blight's Edge world state** — The `blight_radius` flag is a lightweight per-shard world state. Is the current server architecture designed to handle per-shard persistent world state flags, or does this require new infrastructure? Flagged as potentially in-scope based on the existing Open Question OQ-6 from the overworld map GDD (Temple ending world state). | High | CTO |
| OQ-5 | **Faction reputation system scope** — Verdant Pact and Aetheric Order reputation tracking is referenced in the quest rewards. The overworld map GDD references faction envoys but does not fully specify the reputation system. Is reputation tracking implemented? Does this zone need to wait on a reputation system GDD, or can the quest rewards be simplified to gold/XP for now? | Medium | CTO / CEO |
| OQ-6 | **Asset Designer coordination** — The Blight's Edge corruption shader, the night-only bioluminescent visual, and the Deep Canopy darkness overlay all require custom visual effects. I will open a coordination comment with Asset Designer on this ticket. | High | Asset Designer |
| OQ-7 | **Thessa's Ghost** — This NPC references the alpha content (zone-lore.md, Whispering Forest hermit "Thessa"). Inclusion is intentional as a lore continuity nod. Quest Writer should confirm if Thessa's ghost should give additional lore dialogue or remain a pure atmospheric character. | Low | Quest Writer |

---

## 12. Version History

| Version | Date | Author | Summary |
|---|---|---|---|
| v1.0 | 2026-04-19 | Game Designer | Initial draft — full zone layout, 6 enemy stat blocks, NPC roster, 6 quest hooks, loot tables, MMO scaling, CTO technical notes. Awaiting CEO naming confirmation and CTO feasibility review. |
