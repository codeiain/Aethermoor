# Beta Zones — World Expansion Design

**Document:** beta-zones.md
**Milestone:** Beta
**Version:** 1.0
**Date:** 2026-04-15
**Author:** Game Designer

---

## 1. Overview

Beta introduces three new zones that expand the world beyond the Alpha seed area (Millhaven, Whispering Forest, Sunken Crypt B1). These zones are designed to cover the three core zone types the MMO needs at scale:

| Zone | Type | Level Range | Location |
|---|---|---|---|
| **Crossroads** | Town Hub | All levels (social zone) | Central overworld — east of Millhaven |
| **Thornback Wastes** | Wilderness / Overworld | 6–12 | South of Crossroads — arid badlands |
| **Ashenveil Dungeon** | Dungeon | 8–15 | Beneath Thornback Wastes |

**Design intent:** Crossroads gives players a true MMO social hub to graduate into after Millhaven. Thornback Wastes gives mid-game players a dangerous open-world space. Ashenveil is the first "real" dungeon — harder than Sunken Crypt B1 and requiring party coordination.

---

## 2. Zone 1 — Crossroads

### 2.1 Zone Type
Town Hub — shared persistent space, no combat, full MMO social features active.

### 2.2 Biome
Arid plains crossroads — stone road junction where four overworld paths converge. A frontier town grown up around a caravanserai and a postal waystation. Dusty, busy, slightly lawless.

### 2.3 Level Range
All levels. Crossroads is accessible from level 5 via the Ashgate Road east of Millhaven. It is the game's primary mid-game hub and serves as the natural graduation point from Millhaven's starter experience.

### 2.4 Narrative Hook
> *Crossroads wasn't planned — it just happened. A caravanserai here, a waystation there, a few brave merchants who decided the middle of nowhere was worth fighting over. Now it's the busiest place between three kingdoms, and nobody is quite sure who runs it. There's a guild hall, a proper market, a shrine, and two inns — which is one more than anyone expected to need. The road east leads into the Wastes. The road west leads home. Most people who come to Crossroads are heading somewhere. Some of them never leave.*

### 2.5 Zone Entry Text (displayed on player arrival)
> *You've reached the Crossroads. The smell of roasting meat and axle grease is oddly comforting. Merchants argue over stall placement. A notice board outside the Guild Hall is thick with posted jobs. Somewhere inside the caravanserai, someone is playing a lute very badly. This is exactly the kind of place where things happen.*

### 2.6 NPC Population

| Name | Role | Location | Dialogue Hook |
|---|---|---|---|
| **Madame Solis** | Innkeeper & Quest Giver | The Wayward Wheel Inn — (18, 12) | *"Room, bath, or information? I sell all three. The last one's the most expensive, but it's worth it."* |
| **Hendrick "Henny" Foss** | Merchant Guild Rep & Quest Giver | Guild Hall entrance — (24, 10) | *"You want work, you post here. You want to be found, you post here. You want to disappear — well, you probably shouldn't have come to Crossroads."* |
| **Brother Ormund** | Shrine Keeper & Lorekeeper | Wayshrine — (10, 16) | *"The old roads run deep here. Four paths, four winds, four old names. I tend the shrine. I translate the names. Not everything inscribed here is a blessing."* |
| **Tara** | Blacksmith & Merchant | Smithy — (30, 14) | *"I work fast and I work true. If you want pretty, go back to Millhaven. If you want it to hold in a fight, I'm your smith."* |
| **The Auctioneer** | Auction House Operator | Market Hall — (20, 20) | *"Welcome to the floor. Post your goods, set your floor price, let the market decide. Five percent fee — non-negotiable."* |
| **Captain Renna** | Guard Captain & Quest Giver | Crossroads Gate — (5, 10) | *"We maintain order here because nobody else will. If you're making trouble, leave. If you want to help us keep the peace, that's a different conversation."* |
| **Old Kael** | Retired Adventurer & Lorekeeper | Caravanserai common room — (15, 22) | *"I've been to the Wastes. Twice. First time was bravado. Second time was to find what I lost the first time. Don't ask what I lost."* |

### 2.7 Zone Features
- **Auction House** — player-to-player market (see social-mmo-systems.md)
- **Guild Hall** — guild registration, notice board, party board
- **Two Inns** — The Wayward Wheel (affordable), The Merchant's Rest (upscale, costs more, bonus crafting proficiency buff)
- **Wayshrine** — fast travel anchor point; players who die respawn here if Crossroads was their last resting point
- **Bank** — shared account storage, 50-slot personal vault (upgradeable via gold)
- **Notice Board** — daily and repeatable quest board (randomly generated fetch/kill quests)
- **Crafting Workshops** — shared crafting stations for all 6 professions

---

## 3. Zone 2 — Thornback Wastes

### 3.1 Zone Type
Wilderness / Open Overworld — shared zone (capped at 50 players per instance), enemy encounters, resource nodes, secrets.

### 3.2 Biome
Arid badlands — cracked earth, sun-bleached sandstone mesas, dried river beds, scattered ruins of a pre-Sundering settlement. Sparse scrub vegetation clings to shadowed rock faces. The heat shimmers. Visibility is deceptive.

### 3.3 Level Range
6–12 (enemies scale within this range; rare elite encounters reach 14).

### 3.4 Narrative Hook
> *The Thornback Wastes take their name from the creature that owns them — a species of armoured lizard the size of a cart horse, covered in bone-like dorsal spines. The Wastes are also home to something older: the ruins of a Sundering-era settlement called Dunemark, now half-buried by drifting sand. Scholars from Crossroads have theorised that the Ashenveil dungeon lies beneath Dunemark — their maps suggest the crypt entrances emerge from the ruins' foundations. No scholar has yet gone to check. The lizards eat scholars.*

### 3.5 Zone Entry Text
> *The heat hits you first. Then the silence — or what passes for silence here. Wind scrapes dried earth across the mesa faces. Something skitters in the rocks above you. The ruins of Dunemark are visible to the east — rooftops barely clearing the sand, archways filled with drift. The Crossroads road runs straight and cracked through the middle of all of it. A sign where the road forks: "Dunemark — ½ league. Proceed at own risk."*

### 3.6 NPC Population

| Name | Role | Location | Dialogue Hook |
|---|---|---|---|
| **Rook** | Salvager & Quest Giver | Dunemark ruins entrance — (22, 18) | *"I'm not an archaeologist. I'm a businessman who happens to work in old buildings. There's a difference. Mostly legal."* |
| **Sergeant Vance** | Crossroads garrison scout & Quest Giver | Waste patrol post — (10, 14) | *"Three of my scouts went missing near the eastern mesa two days ago. I can't spare more men. I'm authorized to pay an independent contractor."* |
| **The Thornback Watcher** | Environmental NPC (ambient lore) | Mesa overhang — (35, 8) | *"He doesn't speak. He watches. When asked why, he points east, toward the crypt."* |
| **Dust Sister Mave** | Traveling Alchemist & Merchant | Mobile camp, rotates between (5, 20) and (40, 15) | *"I follow the thornbacks. They root out the good herbs when they dig their nests. Dangerous work. Worth it if you know what to look for."* |
| **The Nomad** | Faction Quest Giver (Faction: Desert Brotherhood) | Oasis waypoint — (28, 30) | *"We've held this water for three generations. The crypt creatures are coming up closer every season. This year, we need help."* |

### 3.7 Enemy Types

| Enemy | Level Range | Description |
|---|---|---|
| **Thornback Lizard** | 6–9 | *The zone's iconic creature. Armoured dorsal spines make it hard to hit from behind. Charges in a straight line — sidestep or get knocked prone. Drops Thornback Hide (crafting material).* |
| **Thornback Alpha** (Elite) | 10–12 | *A larger, older Thornback. Red-crested. Signals other Thornbacks to attack in concert. Has a poison bite attack. Required kill for a Beta zone quest.* |
| **Dunemark Remnant** | 7–10 | *Spectral echoes of Sundering-era settlers, haunting the ruins. Intangible — most physical attacks pass through them. Weak to Arcane and Holy damage. Drop Spectral Dust (crafting, alchemy).* |
| **Sand Asp** | 6–8 | *Burrowing serpent. Emerges from the ground without warning (visual: sand ripple approaching player tile). Fast, venomous. Avoidable if you watch the ground. Low XP but predictable spawns make them good early grinding.* |
| **Dunemark Colossus** (Named) | 14 | *A massive animated stone construct reawakened from the ruins. Appears once per zone instance, randomly. Drops Sundering-Era Keystone (rare crafting material — used in high-tier weapon recipes). One guaranteed spawn per week per player.* |

### 3.8 Resource Nodes (Gathering)
- **Desiccated Root** (Herbalism) — alchemy ingredient, moderate rarity
- **Sandstone Vein** (Mining) — construction/crafting material
- **Bloodthorn Cactus** (Herbalism) — rare healing ingredient
- **Ancient Bronze** (Mining) — Sundering-era metal, rare — drops from ruins specifically

### 3.9 Secrets & Points of Interest
- **The Sunken Oasis** — hidden sub-zone accessible only by solving a tile puzzle in the ruins (push three stone pillars onto pressure plates). Contains a rare loot chest and the Nomad faction NPC.
- **Dunemark Inscription Wall** — large readable environmental object explaining the pre-Sundering settlement's history (lore collectible). Rewards 50 XP.
- **Crypt Crack** — a fissure in the earth at the eastern mesa face. Players can peer down and hear sounds from Ashenveil. Required to trigger the dungeon entrance unlock quest.

---

## 4. Zone 3 — Ashenveil Dungeon

### 4.1 Zone Type
Dungeon — private party instance (1–4 players). Instanced on entry. Five floors, boss at floor 5.

### 4.2 Biome
Collapsed pre-Sundering crypt beneath Dunemark — obsidian walls fused with volcanic rock, ember-lit sconces, rivers of slow-moving ash. Evidence of a catastrophic fire event that sealed the crypt during the Sundering. The dungeon has two distinct visual halves: upper floors (char and ash) and lower floors (deeper, stranger — ancient construction unlike human craft).

### 4.3 Level Range
Recommended: 8–15 (balanced for L10 party). Solo possible but difficult. Hard mode (Level 13–15) available as a toggle on entry.

### 4.4 Narrative Hook
> *The Ashenveil was sealed during the Sundering by a fire that burned for forty days. The scholars of Crossroads know this because Brother Ormund translated the runes above the entrance. The rune at the very top of the arch, the one they haven't translated yet, concerns him. His best guess is that it means either "purified" or "contained." He hopes it is "purified." The Dunemark Remnants suggest otherwise.*

### 4.5 Dungeon Layout — 5 Floors

#### Floor 1 — The Char Halls (Entry)
- **Rooms:** 6 rooms, linear with one optional branch
- **Mechanic:** Smouldering floors — certain tiles deal 5 fire damage per second. Pathfinding puzzle to reach the key chest.
- **Enemies:** Ashenveil Crawlers (ash-covered undead, move fast)
- **Mini-boss:** The Ember Warden — armoured skeleton, fire resistance, area denial (throws burning objects)
- **Loot:** Common–Uncommon loot table. Key item: Floor 2 Key

#### Floor 2 — The Ash Garden
- **Rooms:** 8 rooms, branching — two optional side rooms (one with a lore object, one with a gold cache)
- **Mechanic:** Ash storms — periodic wind events that blind players (vision cone reduced to 3 tiles) for 5 seconds. Enemies use this to reposition.
- **Enemies:** Ash Sprites (airborne, fast), Dunemark Shade (melee, heavy)
- **Mini-boss:** Ashveil Twins — two Shades that share a health pool across their two bodies. Must be killed within 10 seconds of each other or the surviving twin is fully healed.
- **Loot:** Uncommon–Rare loot table. Key item: Floor 3 Key

#### Floor 3 — The Obsidian Labyrinth
- **Rooms:** 10 rooms, maze layout — compass item found here reveals the map
- **Mechanic:** Mirror tiles — some walls are reflective. Certain projectile attacks (including Archmage spells) bounce. Players can use this; enemies do too.
- **Enemies:** Refracted Phantoms (creatures that appear at multiple mirror-reflected positions simultaneously — only the real one takes damage)
- **Mini-boss:** The Obsidian Sentinel — golem that is immune until all four mirror totems in the room are destroyed
- **Loot:** Rare loot table. Key item: Floor 4 Key + Dungeon Compass (reveals floor 3–4 maps)

#### Floor 4 — The Sealed Chambers
- **Rooms:** 6 rooms — each chamber is locked. Chamber keys are held by the floor's patrol enemies.
- **Mechanic:** Sealed Hunger — the air here drains Mana. Casters lose 10 mana per 5 seconds while on this floor. Party must be efficient; long fights are costly.
- **Enemies:** Ashenveil Hunters (ranged, high damage), Sealed Revenant (tank enemy — blocks doorways until destroyed)
- **Loot:** Rare–Epic loot table. Key item: Boss Key

#### Floor 5 — The Pyre Chamber (Boss Room)
- **Room:** Single large chamber, circular, with a raised central dais
- **Mechanic:** Rising Ash — ash level in the room rises throughout the fight, eventually restricting movement to the central dais (forces melee range)
- **Boss:** The Ashenveil Keeper
- **Loot:** Epic loot table (guaranteed 1 epic per player first clear), dungeon-exclusive cosmetic (Embered Armor skin)

### 4.6 Boss — The Ashenveil Keeper

| Attribute | Value |
|---|---|
| HP | 1,800 (standard) / 2,700 (hard mode) |
| AC | 17 |
| Phase 1 (100–60% HP) | Standard melee + fire breath cone (60° arc, 3 tiles, 30 fire damage); repositions every 20 seconds |
| Phase 2 (60–30% HP) | Summons 4 Ash Crawlers; fire breath becomes 120° arc; ash rise rate doubles |
| Phase 3 (30–0% HP) | Enrage — movement speed +50%; fire breath becomes 360° pulse every 8 seconds; Crawlers are relentlessly replaced |
| Kill reward (first clear) | 1,200 XP + 1 Epic item from dungeon loot table + 500g + Ashenveil Dungeon clear achievement |
| Kill reward (repeat) | 600 XP + Rare item + 200g |

### 4.7 Dungeon-Exclusive Loot (Ashenveil Gear Set)

| Item | Slot | Rarity | Effect |
|---|---|---|---|
| Emberveil Blade | Weapon (melee) | Epic | +3 STR attack; 15% chance to apply Burning (5 fire damage/sec × 3 sec) on hit |
| Ashenveil Staff | Weapon (magic) | Epic | +4 INT; fire spells deal +20% damage |
| Keeper's Pauldrons | Shoulder | Rare | +10% fire resistance; +8 max HP |
| Ember Crown | Head | Rare | +2 INT; +2 WIS; glow cosmetic effect |
| Soot-Black Cloak | Back | Uncommon | +5% dodge chance; ash visual trail cosmetic |
| Embered Armor Skin | Cosmetic | Unique | Full armor visual replacement — blackened metal with ember glow at joints |

### 4.8 Dungeon Quests

| Quest | NPC | Description | Reward |
|---|---|---|---|
| *Into the Ashenveil* | Rook (Thornback Wastes) | Enter and clear the dungeon for the first time | 400 XP, 250g, Uncommon chest |
| *The Sealed Chambers* | Sergeant Vance | Find the missing scouts on floors 3–4 | 600 XP, 400g, rare weapon |
| *What Burns Beneath* | Brother Ormund | Find and read the Lore Inscription on Floor 2 | 200 XP, Lore codex entry unlocked |
| *The Keeper Must Fall* | Henny Foss (Crossroads) | Kill the Ashenveil Keeper | 1,000 XP, 600g, Guild reputation +50 |

---

## 5. MMO Considerations

| Consideration | Design Decision |
|---|---|
| Crossroads player cap | Unlimited — town hub is designed for high density; server handles it as a single persistent shard |
| Thornback Wastes instance cap | 50 players per instance; auto-instances when cap reached |
| Ashenveil instance model | Private instance per party (1–4 players); hard mode is a separate instance pool |
| Boss spawn uniqueness | Dunemark Colossus (named enemy) spawns once per instance per reset — not affected by other players' kills |
| Dungeon lockout | One loot-eligible clear per 24 hours per player (repeatable for XP/gold only after lockout) |

---

## 6. Technical Notes

- Ashenveil ash-rise mechanic: server tracks ash level as a float 0.0–1.0 per instance; broadcast to clients every 2 seconds; clients animate tile flooding accordingly
- Ashenveil Twins shared health pool: one HP value server-side, both entities read it; desync prevention via server-authoritative damage resolution
- Refracted Phantoms (Floor 3): server resolves which "real" phantom takes damage; clients display all reflections as visually identical
- Thornback Wastes zone instancing: use same shard auto-split logic as Whispering Forest from Alpha
- Crossroads Auction House: persistent market data in PostgreSQL; see social-mmo-systems.md for trade spec

---

## 7. Open Questions

| # | Question | Owner |
|---|---|---|
| 1 | Should Ashenveil have a checkpoint system between floors, or is full-dungeon-restart the intended consequence of a wipe? | CEO |
| 2 | Hard mode Ashenveil — should this be a separate queue or a toggle on entry? Recommend: toggle on entry before instance launches | CEO to confirm |
| 3 | Should Crossroads have a PvP duelling arena (flagged opt-in zone within the hub)? Future scope or Beta? | CEO |
| 4 | Dunemark Colossus weekly spawn — should this be account-wide or per-character? | CEO |

---

## 8. Version History

| Version | Date | Summary |
|---|---|---|
| 1.0 | 2026-04-15 | Initial Beta zone designs: Crossroads, Thornback Wastes, Ashenveil Dungeon |
