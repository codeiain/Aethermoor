# Crafting System Design — Project AETHERMOOR

**Document:** crafting/crafting-system.md
**Issue:** RPGAA-36 (new task)
**Version:** 1.0
**Date:** 2026-04-16
**Author:** Game Designer

---

## 1. Overview

The Crafting System is a core AETHERMOOR gameplay pillar that allows players to craft weapons, armour, consumables, housing items, and trade goods through six distinct professions. Crafting serves as a meaningful alternative progression path — players who prefer non-combat activities (fishing, crafting, housing) are economically viable and can contribute meaningfully to party and guild success.

**Design Intent:**
- Every crafted item must be **worth crafting** — there is always a reason to craft over buying from vendors or the Auction House
- Crafting provides a **long-term gold sink** that stabilises the economy
- Crafting must work on **mobile with one-handed input** — no complex drag-chains required
- Crafting progression rewards **consistent engagement** over RNG grinds

---

## 2. Design Goals

| Goal | Rule |
|---|---|
| Meaningful craft | Every recipe produces items with clear use cases — no vanity-only items at low levels |
| Economic integration | Crafted items compete with drops and vendor goods; crafted gear has distinct advantages |
| Mobile-first | Full crafting flow completable in 6 taps or fewer on mobile |
| Profession identity | Each profession feels distinct; no generic "craft everything" outcome |
| Gold sink | Crafting costs (materials + fees) absorb gold from the economy |
| Social hook | Crafting creates trade opportunities between professions |

---

## 3. Professions

### 3.1 Profession Overview

Every player chooses **two primary professions** at character creation (can be changed once per 30 days via a profession trainer for a fee). Each profession has a distinct gathering or source activity, a set of craftable item categories, and a mastery track.

| Profession | Gathering Method | Craftable Categories | Primary Role |
|---|---|---|---|
| **Blacksmithing** | Mining ore nodes | Weapons, Heavy Armour, Shields, Tool Upgrades | Combat gear for melee/DPS |
| **Tailoring** | Harvesting cloth from enemies | Light Armour, Bags, Cloaks, Barding | Combat gear for casters/rogues |
| **Alchemy** | Gathering herbs + fishing byproducts | Potions, Elixirs, Antidotes, Weapon Coatings | Consumable support |
| **Cooking** | Gathering plants + fishing catches | Food buffs, Party feasts, Recovery items | Sustained combat buffs |
| **Enchanting** | Disenchanting loot + gathering crystals | Weapon enchants, Armor runes, Consumable enchantments | Gear enhancement |
| **Woodcrafting** | Harvesting wood nodes | Bows, Staves, Housing furniture, Tool handles | Versatile utility |

**Dual-profession constraint:** A player cannot equip two gathering professions (Blacksmithing + Woodcrafting) or two processing professions (Alchemy + Cooking) as their two primaries. This prevents "gather-only" players and encourages trade between players.

### 3.2 Profession Switching

| Option | Cost | Cooldown |
|---|---|---|
| Change one profession | 500g | 30 days |
| Reset both professions | 1,500g | 60 days |
| Emergency reset (GM request) | 5,000g | None |

---

## 4. Gathering System

### 4.1 Gathering Nodes

Gathering nodes are world objects that respawn on a timer. Players interact with nodes by approaching and pressing the interact key (or tapping on mobile).

| Node Type | Professions | Respawn Time | Locations |
|---|---|---|---|
| Ore Vein | Blacksmithing | 15 minutes | Mountains, caves, near forges |
| Herb Patch | Alchemy | 10 minutes | Forest edges, gardens, wilderness |
| Wood Bundle | Woodcrafting | 12 minutes | Forest, near trees, lumber areas |
| Cloth Drops | Tailoring | On enemy kill (guaranteed) | Any combat zone |
| Fish Catch | Cooking + Fishing | Per cast | Fishing spots (see Fishing spec) |
| Crystal Cluster | Enchanting | 20 minutes | Dungeon floors, magical zones |

**Node interaction:**
- Mobile: Tap the node → auto-gather after 2-second channel (can be interrupted)
- Desktop: Press E / click → immediate gather
- Yields 1–3 units of the material per gather
- Gathering has no fail state

### 4.2 Material Tiers

| Tier | Colour | Drop Quality | Used For |
|---|---|---|---|
| Common | Grey | High quantity | Basic recipes, vendor goods |
| Uncommon | Green | Moderate quantity | Standard gear, Uncommon items |
| Rare | Blue | Low quantity | Rare gear, Epic items |
| Epic | Purple | Very low quantity | Epic gear, Legendary consumables |
| Legendary | Orange | Exceptional rarity | Legendary items, high-tier housing |

---

## 5. Crafting Workflow

### 5.1 Crafting Station Locations

| Station | Professions | Locations |
|---|---|---|
| Forge | Blacksmithing | Every town blacksmith, player Housing (with Crafter's Bench) |
| Loom | Tailoring | Every town tailor, player Housing |
| Alchemy Table | Alchemy | Every town alchemist, player Housing |
| Campfire / Kitchen | Cooking | Every town inn, player Housing, world campsites |
| Enchanting Pedestal | Enchanting | City of Aethermoor only (central location), player Housing |
| Woodworking Bench | Woodcrafting | Every town general store, player Housing |

### 5.2 Crafting UI Flow

**Mobile (6-tap maximum):**

```
Tap Crafting Station NPC
  → Select Profession tab (1 of 2)          [TAP 1]
  → Scroll to recipe (tap category header)   [TAP 2]
  → Tap recipe                               [TAP 3]
  → (If materials sufficient: "Craft" button enabled)
     Tap Craft                               [TAP 4]
  → Confirm craft quantity (tap +/- or 1x)    [TAP 5]
  → Tap Craft again                          [TAP 6]
  → Results shown, auto-return to recipe list
```

**Recipe requiring missing materials:**
```
Tap recipe
  → "Missing Materials" panel slides up from bottom
  → Tap each missing material to highlight source location on minimap
  → Tap "Gather" to exit crafting UI and navigate to nearest node
  → Return to complete
```

### 5.3 Recipe Structure

Each recipe defines:

```json
{
  "recipeId": "blacksmithing_iron_sword",
  "name": "Iron Longsword",
  "profession": "blacksmithing",
  "minProfessionLevel": 1,
  "materials": [
    { "materialId": "iron_ore", "quantity": 3 },
    { "materialId": "oak_handle", "quantity": 1 }
  ],
  "tools": ["forge"],        // optional, station provides this
  "craftTime": 5,           // seconds (real-time)
  "yield": 1,               // items produced
  "expertiseBonus": "strength",  // stat bonus applied to crafted item
  "resultItemId": "iron_longsword"
}
```

### 5.4 Craft Time

| Recipe Tier | Craft Time | Design Intent |
|---|---|---|
| Common | 3 seconds | Near-instant; basic supply replenishment |
| Uncommon | 10 seconds | Moderate time investment; fair for mobile |
| Rare | 30 seconds | Meaningful commitment; party can wait |
| Epic | 2 minutes | Considerable investment; high stakes |
| Legendary | 5 minutes | Major undertaking; announced in chat |

**Crafting while offline:** Crafting cannot be started offline. Crafting queues are not supported in MVP. All crafting requires the player to be online and at a crafting station.

---

## 6. Profession Progression

### 6.1 Profession Level

Each profession has a level from 1–20. Level is earned through crafting (not gathering — gathering XP is separate).

| Profession Level | Title | Unlocks |
|---|---|---|
| 1–4 | Apprentice | Basic Common + Uncommon recipes |
| 5–9 | Journeyman | Advanced Uncommon + first Rare recipes |
| 10–14 | Expert | Rare + Epic recipes |
| 15–18 | Master | Epic + Legendary recipes |
| 19–20 | Grand Master | Legendary recipes + recipe invention |

### 6.2 Profession XP

XP is earned per craft based on recipe tier:

| Recipe Tier | Profession XP per Craft |
|---|---|
| Common | 10 XP |
| Uncommon | 30 XP |
| Rare | 100 XP |
| Epic | 400 XP |
| Legendary | 2,000 XP |

**XP to level:** `100 * currentLevel^1.5` (same formula as character XP, different curve exponent)

| Level | XP Required | Total XP |
|---|---|---|
| 1 → 2 | 100 | 100 |
| 5 | 558 | 1,568 |
| 10 | 1,283 | 5,527 |
| 15 | 2,588 | 15,677 |
| 20 | 4,347 | 33,713 |

### 6.3 Recipe Discovery

Players do not start with all recipes. Recipes are unlocked through:

| Method | Recipes Unlocked |
|---|---|
| Starting profession level 1 | 5 starter recipes |
| Level milestones (every 2 levels) | 2–4 new recipes per unlock |
| Discovery via gather | 1% chance when gathering materials to discover a hidden recipe |
| World lore scrolls | 5% chance when reading a lore scroll in a town library |
| Trainer purchase | Buy known recipes from profession trainer for 50–500g each |
| Guild research (Lvl 10+) | Guild can research recipes shared with all members |

**Design intent:** Discovery creates moments of surprise and delight. A player gathering herbs might stumble upon a rare potion recipe. This rewards exploration without gating core content.

### 6.4 Quality / Craftsmanship

Crafted items have a **Quality** roll that determines stat bonuses above the item's base values.

**Quality Formula:**
```
Quality = baseItemStats + craftsmanshipBonus
craftsmanshipBonus = floor(professionLevel / 4) * primaryStatBonus

Example: Iron Longsword (base: 8–12 damage, +1 STR)
  Crafted by Level 8 Blacksmith
  craftsmanshipBonus = floor(8/4) * 1 = 2 * 1 = +2 STR bonus
  Final stats: 8–12 damage, +3 STR
```

**Exceptional Craft (critical success):**
- 5% base chance on any craft
- **Master+ (Level 16+): 15% exceptional chance** — shown in tooltip before craft confirmation
- **Grand Master (Level 20): 100% exceptional guarantee** — minimum Exceptional quality at max profession level
- Doubles the craftsmanship bonus
- Shows a special "Exceptional!" particle effect and message in zone chat
- Item gains a special prefix (e.g. "Exceptional Iron Longsword")

---

## 7. Item Categories by Profession

### 7.1 Blacksmithing

| Item Category | Examples | Materials Used | Crafting Station |
|---|---|---|---|
| Melee Weapons | Swords, axes, maces, daggers | Ore + wood handles | Forge |
| Heavy Armour | Plate armour, chainmail, helmets | Ore + cloth lining | Forge |
| Shields | Buckler, kite shield, tower shield | Ore + wood | Forge |
| Tool Upgrades | Reinforced pickaxe, reinforced axe | Ore | Forge |
| Ammunition | Arrows (metal-tipped), bolts | Ore | Forge |
| Consumables | Whetstone (+weapon damage 10 min), Rustproof Oil | Ore | Forge |

### 7.2 Tailoring

| Item Category | Examples | Materials Used | Crafting Station |
|---|---|---|---|
| Light Armour | Leather armour, robes, mage robes | Cloth + leather | Loom |
| Bags | Inventory bags (add slots), reagent pouches | Cloth + leather | Loom |
| Cloaks | Capes, hoods, guild banners | Cloth | Loom |
| Barding | Mount armour (endgame) | Cloth + ore | Loom |
| Consumables | Bandages (heal out of combat), Silk Rope | Cloth | Loom |

### 7.3 Alchemy

| Item Category | Examples | Materials Used | Crafting Station |
|---|---|---|---|
| Health Potions | Minor, Standard, Major, Superior | Herbs | Alchemy Table |
| Mana Potions | Minor, Standard, Major, Superior | Herbs + crystals | Alchemy Table |
| Elixirs | Elixir of Strength (+3 STR 30 min), etc. | Rare herbs | Alchemy Table |
| Antidotes | Cures Poisoned, Burning, Frozen | Rare herbs | Alchemy Table |
| Weapon Coatings | Fire Oil (weapon deals +2d6 fire), Frost Oil | Rare herbs | Alchemy Table |
| Scents | Beast Scent (attracts/fends enemies), Underwater Breathing | Herbs + fish | Alchemy Table |

### 7.4 Cooking

| Item Category | Examples | Materials Used | Crafting Station |
|---|---|---|---|
| Combat Food | Steak (+10 STR 30 min), Fish Pie (+5 DEX 30 min) | Meat + vegetables | Campfire/Kitchen |
| Party Feasts | Grand Feast (all stats +5 for 1 hour) | Multiple ingredients | Kitchen (guild hall) |
| Recovery Items | Hearty Stew (restores 50% HP instantly), Mana Broth | Meat + herbs | Campfire |
| Beverages | Ale (+morale — cosmetic chat effects), Tea | Plants | Campfire |
| Fishing Baits | Special baits for rare fish | Fish + herbs | Kitchen |

### 7.5 Enchanting

| Item Category | Examples | Materials Used | Crafting Station |
|---|---|---|---|
| Weapon Enchantments | Sharpness (+1d4 damage), Fire Aspect (burn on hit) | Crystals + reagent | Enchanting Pedestal |
| Armour Enchantments | Protection (+1 AC), Thorns (damage attackers) | Crystals + reagent | Enchanting Pedestal |
| Consumable Enchantments | Enchanted Scroll (one-use buff item) | Crystals + parchment | Enchanting Pedestal |
| Disenchantment | Break down unwanted gear into crystals | Any enchanted item | Enchanting Pedestal |

**Disenchanting:**
- Unwanted magical items can be disenchanted (right-click / long-press menu)
- Returns 1–3 Enchanting Crystals (quantity based on item rarity)
- Crystals used for all enchanting recipes
- Cannot disenchant Legendary items — must be sold or kept

### 7.6 Woodcrafting

| Item Category | Examples | Materials Used | Crafting Station |
|---|---|---|---|
| Ranged Weapons | Shortbows, Longbows, Composite bows | Wood + string (cloth) | Woodworking Bench |
| Staves | Arcane staves, Healing staves | Wood + crystal | Woodworking Bench |
| Housing Furniture | Chairs, tables, beds, shelves, garden plots | Wood + fabric | Woodworking Bench |
| Tool Handles | Axe handles, pickaxe handles, hammer handles | Wood | Woodworking Bench |
| Shields (wooden) | Wooden buckler, reinforced wooden shield | Wood | Woodworking Bench |
| Musical Instruments | Lute, drum (Bard cosmetics + minor buffs) | Wood + cloth | Woodworking Bench |

---

## 8. Economy Integration

### 8.1 Crafting as an Economic Pillar

Crafting serves three economic functions:

1. **Alternative to drops:** Crafted gear is competitive with dungeon drops, giving players who prefer crafting a viable path to equip their characters
2. **Crafted superior items:** Certain item categories (consumables, housing furniture, bags) are **only craftable** — they cannot be obtained from drops, only from vendors or players
3. **Gold sink:** Crafting costs (ore cost + trainer recipe fees + enchantment fees) drain gold from the economy

### 8.2 Crafted vs. Dropped Item Comparison

| Factor | Crafted | Dropped |
|---|---|---|
| Stat variance | Fixed stats + craftsmanship bonus | Random stat ranges |
| Quality | Predictable based on crafter skill | Random rarity from loot tables |
| Customisation | Enchantable, upgradeable | Limited enchantment slots |
| Uniqueness | None (recipe is known) | Named/unique items from bosses |
| Cost | Material cost + time | Free (if you get the drop) |
| Market availability | Always available to craft | Random, scarce |

**Design balance:** Boss drops are **slightly stronger** than top-tier crafted equivalents (the 5–10% advantage compensates for the RNG nature of drops). Crafted gear is the **reliable, consistent** alternative.

### 8.3 Gold Sinks via Crafting

| Sink | Amount | Frequency |
|---|---|---|
| Recipe unlock from trainer | 50–500g per recipe | One-time |
| Material gathering cost (vendor purchase fallback) | 5–200g per material | Per craft |
| Enchantment fee | 10% of item value | Per enchant |
| Profession reset | 500–5,000g | Rare |
| Housing crafting station upgrade | 1,000–10,000g | One-time |

### 8.4 Player-to-Player Crafting Services

Skilled crafters (Grand Masters) can offer **crafting services** to other players:

- Player A brings materials to a Grand Master crafter
- Grand Master charges a fee (negotiated in chat or via guild)
- Grand Master crafts the item at their quality bonus (higher profession level = better quality)
- Item is tradeable or mailed to the customer

This creates an in-game economy of crafting services and rewards dedicated crafters.

**Item Binding Rules (CEO Decision):**
- Crafted items are **BOE (Bind-on-Equip)** — items are tradeable until equipped
- Once equipped to a character, items cannot be traded or sold on Auction House
- This supports the player trading economy while preventing item duplication exploits

---

## 9. Integration with Other Systems

### 9.1 Crafting + Housing

- Crafters with a Crafter's Bench in their home can craft from home
- Home crafting stations are upgraded versions (+1 to craftsmanship bonus)
- Housing decorative items (furniture, trophies) are crafted by Woodcrafting
- Guild halls have shared crafting stations accessible to all members

### 9.2 Crafting + Fishing

- Cooking uses fish as a primary ingredient
- Alchemy uses fish byproducts (fish oil, fish scales) as reagents
- Special fishing baits are crafted with Alchemy + Cooking combined

### 9.3 Crafting + Combat

- Weapon coatings from Alchemy add damage types to weapons
- Combat food provides stat buffs before encounters
- Health/mana potions are always in demand
- Ammunition (arrows, bolts) from Blacksmithing must be restocked

### 9.4 Crafting + World Events

- World Events occasionally introduce **event-specific recipes** (e.g., Frostbloom Elixir during winter event)
- Event recipes are unlocked by participating in the event
- Event-crafted items are cosmetic variants or seasonal bonuses

---

## 10. MMO Considerations

### 10.1 Server Authority

All crafting is server-authoritative:
- Recipe validation: server checks profession level, known recipes, materials
- Craft execution: server resolves craft time, rolls quality, generates item
- Material deduction: server deducts materials from inventory atomically
- Item generation: server assigns item ID and stats

### 10.2 Crafting Queue

MVP: **No crafting queue.** Player must be present and online during craft time. This keeps crafting social and meaningful.

Post-MVP (Future): Guild crafting queues where guild members submit materials and a designated crafter executes when available.

### 10.3 Anti-Exploit

- Material costs are deducted server-side before craft begins (no refund on failure — there is no failure state in MVP)
- Craft time is enforced server-side — cannot AFK in a zone and claim to have crafted an item
- Profession level is server-authoritative
- Exceptional Craft critical chance is server-side only (never revealed to client)

### 10.4 Scalability

- Crafting stations are world objects; many players can use the same station simultaneously
- No per-station capacity limit in open world zones
- Town crafting NPCs support unlimited concurrent users (stateless interaction)
- Home crafting benches are private instances

---

## 11. UI/UX Specification

### 11.1 Crafting Panel (Mobile)

```
┌─────────────────────────────────────┐
│  CRAFTING          [X] Close       │
├─────────────────────────────────────┤
│  [BS]  [Tail]  [Alch]  [Cook]       │
│  [Enc]  [WC]                       │
│         (tabs)                      │
├─────────────────────────────────────┤
│  ┌─────────────────────────────┐   │
│  │ IRON LONGSWORD              │   │
│  │ Requires: Iron Ore x3       │   │
│  │          Oak Handle x1      │   │
│  │ Result: 8-12 DMG, +1 STR    │   │
│  │ [CRAFT] (or [MISSING x2])  │   │
│  └─────────────────────────────┘   │
│  ... scrollable recipe list ...    │
└─────────────────────────────────────┘
```

### 11.2 Crafting Progress Bar

When crafting is in progress:
```
┌─────────────────────────────────────┐
│  Crafting: Iron Longsword           │
│  [████████░░░░░░░░░]  4s / 10s   │
│  Tap to cancel                     │
└─────────────────────────────────────┘
```

### 11.3 Crafting Station NPC Interaction

- Town crafting NPCs have a "Craft" dialogue option (distinct from "Trade")
- Tap "Craft" to open the crafting panel
- Panel remembers last-used profession tab

---

## 12. API Endpoints (CTO Reference)

| Endpoint | Method | Purpose |
|---|---|---|
| `GET /crafting/recipes/{profession}` | GET | List all known recipes for a profession |
| `POST /crafting/validate` | POST | Validate whether player can craft a specific recipe (returns missing materials) |
| `POST /crafting/craft` | POST | Execute a craft (server-authoritative) |
| `GET /crafting/professions/{playerId}` | GET | Get player's profession levels |
| `POST /crafting/professions/change` | POST | Change one profession (30-day cooldown enforced server-side) |
| `POST /crafting/disenchant` | POST | Disenchant an item, return crystals |
| `GET /crafting/gathering-nodes?zoneId={id}` | GET | List gathering node locations in zone |

**Craft Request Body:**
```json
{
  "playerId": "uuid",
  "recipeId": "blacksmithing_iron_sword",
  "quantity": 1
}
```

**Craft Response Body:**
```json
{
  "success": true,
  "itemId": "uuid",
  "itemName": "Iron Longsword",
  "rarity": "uncommon",
  "qualityBonus": 2,
  "isExceptional": false,
  "newProfessionXp": 30,
  "newProfessionLevel": 1
}
```

---

## 13. Technical Notes

### 13.1 Data Model

**PlayerProfession table (PostgreSQL):**
```
player_id        UUID (FK)
profession       VARCHAR(20)  -- blacksmithing, tailoring, alchemy, cooking, enchanting, woodworking
level            INT (1-20)
xp               INT
recipes_known    UUID[]      -- array of known recipe IDs
last_changed_at  TIMESTAMP
```

**Recipe table (PostgreSQL, seed data):**
```
recipe_id        VARCHAR(50) PRIMARY KEY
profession       VARCHAR(20)
min_level        INT
materials        JSONB        -- [{materialId, quantity}, ...]
craft_time_sec   INT
result_item_id   VARCHAR(50)
hidden           BOOLEAN      -- undiscovered recipes
```

**CraftingMaterial table (PostgreSQL, seed data):**
```
material_id      VARCHAR(50) PRIMARY KEY
name             VARCHAR(100)
tier             INT (1-5)
profession       VARCHAR(20)  -- which profession gathers this
```

### 13.2 Implementation Notes

- Crafting is a **stateless REST endpoint** — no WebSocket needed for the craft itself (real-time progress can be polled or pushed via WebSocket notification)
- Gathering nodes are world objects stored in the Game World Service zone data
- Profession change cooldown must be enforced server-side (not client-side)
- Exceptional craft RNG must use a CSPRNG server-side
- Crafting services between players use the existing trade system with a "crafting fee" field

---

## 14. CEO Design Decisions (2026-04-16)

| # | Decision | Rationale |
|---|---|---|
| 1 | **Exceptional craft chance: VISIBLE** — 15% at Master+ (Level 16+), shown in tooltip before craft confirmation | Players prefer transparent systems; enables strategic crafting decisions |
| 2 | **Crafted items: BOE (bind-on-equip)** — items bind when equipped, not on pickup | Supports player trading economy, consistent with standard MMO convention |
| 3 | **Grand Master Level 20: quality guarantee of Exceptional** — minimum Exceptional quality at max profession level | Milestone reward for dedicated crafters; encourages long-term progression |
| 4 | **Craft-time notifications: REST polling acceptable** — CTO may add SSE later if UX data demands | MVP simplicity; polling is sufficient for Alpha |

## 15. Open Questions

| # | Question | Owner |
|---|---|---|
| 1 | Should Alchemy/Enchanting use a mini-game (e.g., reagent timing) to add skill expression? MVP: No mini-game. Post-MVP: consider | CTO |

---

## 16. Version History

| Version | Date | Summary |
|---|---|---|
| 1.1 | 2026-04-16 | Added CEO design decisions (BOE, visible exceptional chance, GM quality guarantee, REST polling). Removed from open questions. |
| 1.0 | 2026-04-16 | Initial complete draft — all 15 sections. Authored by Game Designer. |
