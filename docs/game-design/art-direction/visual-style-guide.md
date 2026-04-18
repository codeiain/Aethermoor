# AETHERMOOR — Art Direction Spec: Visual Style Guide v1.0

**Author:** Game Designer
**Date:** 2026-04-15
**Status:** Draft v1.0
**Source GDD:** v0.4 | **Source UI Style Guide:** v0.1.0
**Ticket:** RPGAA-32

---

## Table of Contents

1. [Overview](#1-overview)
2. [Design Goals](#2-design-goals)
3. [Core Visual Style](#3-core-visual-style)
4. [Reference Games & Mood Board](#4-reference-games--mood-board)
5. [Character Design Guidelines](#5-character-design-guidelines)
6. [Tile & Environment Style](#6-tile--environment-style)
7. [UI Art Style](#7-ui-art-style)
8. [Asset Delivery Spec](#8-asset-delivery-spec)
9. [MMO Considerations](#9-mmo-considerations)
10. [Technical Notes for CTO](#10-technical-notes-for-cto)
11. [Open Questions](#11-open-questions)
12. [Version History](#12-version-history)

---

## 1. Overview

This document defines the complete visual art direction for Project AETHERMOOR. It is the single source of truth for how the game looks — for the CTO replacing prototype placeholder textures, and for any future artists creating pixel art assets.

The prototype currently uses programmatically generated placeholder textures (flat-colour grass, wall tiles, player dot). This spec defines the visual language that replaces all placeholders and guides every future asset.

**Art Direction in One Sentence:**
> AETHERMOOR looks like a late-SNES era secret that somehow became an MMO — warm, detailed, hand-crafted pixel art that rewards exploration with beauty.

---

## 2. Design Goals

| # | Goal | Player Experience Created |
|---|------|--------------------------|
| 1 | **Instant readability** | Players immediately understand what tiles they can walk on, what is an obstacle, and where enemies are — even on a small phone screen |
| 2 | **World feels handcrafted** | Every zone should feel like a human artist placed each tile — not procedurally generated — even when procedural tools assist |
| 3 | **Zones have distinct personalities** | Millhaven and the Sunken Crypt should feel like different worlds. Colour, tile palette, lighting style, and ambient detail all vary by zone |
| 4 | **Characters read at a distance** | Player characters and enemies must be distinguishable from each other and from the environment at normal zoom — silhouette design is primary |
| 5 | **Consistent aesthetic register** | Dark fantasy meets cosy adventure — not grimdark, not saccharine. Think Zelda: Link's Awakening DX meets the original Baldur's Gate in pixel-art form |
| 6 | **Mobile-legible** | All assets must remain readable and beautiful when rendered on a 375px-wide mobile screen at 2× pixel scaling |
| 7 | **Technically efficient** | Asset design must minimise draw calls. Sprite sheets, tile atlases, and palette sharing are mandatory. The CTO cannot afford individual texture uploads per tile |

---

## 3. Core Visual Style

### 3.1 Tile Resolution

| Property | Value | Source |
|----------|-------|--------|
| Base tile size | **32×32 pixels** | Confirmed by Board |
| Character sprite base | **32×32 pixels** (fits within one tile) | — |
| NPC portrait base | **48×48 pixels** | Confirmed in UI Style Guide |
| UI icon base | **16×16 pixels** (scaled 2× to 32×32 display) | Confirmed in UI Style Guide |
| Display scale | 2× (mobile), 2× or 3× (web/tablet at user choice) | — |

**Rationale:** 32×32 gives enough detail for personality (expressions, clothing detail, class silhouettes) while remaining crisp at 2× scale on a 375px screen. At 2×, each tile renders at 64×64 CSS pixels — a 375px screen holds ~5.8 tiles wide, sufficient for top-down readability without feeling cramped.

### 3.2 Colour Depth & Palette Rules

**Global Rules:**
- Max **16 colours per sprite** (not counting transparency / colour index 0)
- Colours are sampled from a **shared global palette** (defined in Section 3.3) — sprites must not introduce colours outside this palette
- **No gradients** — all shading is achieved through dithering (checkerboard or Bayer patterns) or palette ramps
- **No anti-aliasing** — pixels must be hard-edged. All rendering must use nearest-neighbour scaling
- **One light source per tile set:** top-left for exterior zones; top for interior/dungeon zones
- **Transparency:** single index alpha only — no partial transparency in sprites. UI can use canvas-level alpha compositing for overlays, not sprite alpha

### 3.3 Global Palette

The global palette is shared across all game sprites and tiles. Individual zone sub-palettes are subsets of this master palette, with up to 4 zone-specific accent colours added via palette-swap.

#### Core Chromatic Palette

| Slot | Name | Hex | Primary Use |
|------|------|-----|-------------|
| 01 | Void | `#0D0814` | Deep shadow, dungeon void |
| 02 | Midnight | `#1A1022` | Dark background, deep water |
| 03 | Shadow | `#2B1D0E` | Ink, tree trunk shadow |
| 04 | Earth Dark | `#3D2B1A` | Dirt, bark dark |
| 05 | Earth | `#5C3D1E` | Soil, leather |
| 06 | Stone Dark | `#3A3530` | Wall shadow, stone deep |
| 07 | Stone | `#5A5248` | Wall mid, rock |
| 08 | Stone Light | `#857E76` | Wall highlight, gravel |
| 09 | Bone | `#B8AFA0` | Undead, old stone, parchment-tile |
| 10 | Parchment Dark | `#D9C89A` | UI borders (matches UI guide) |
| 11 | Parchment | `#F5E6C8` | UI backgrounds (matches UI guide) |
| 12 | Snow | `#EEF2F5` | Snow caps, highlight |
| 13 | Bark | `#6B4F35` | Tree trunks, wooden structures |
| 14 | Bark Light | `#9A7250` | Log highlight |
| 15 | Moss Dark | `#2E4D2E` | Dark foliage, swamp |
| 16 | Moss | `#4A7C50` | Grass mid (matches UI success) |
| 17 | Grass | `#6AAB55` | Grass bright |
| 18 | Leaf Light | `#9FCC7A` | Leaf highlight |
| 19 | Water Deep | `#1A3D5E` | Deep water, ocean |
| 20 | Water | `#2B6899` | River mid (near sky in UI guide) |
| 21 | Water Light | `#5A9EC2` | Water highlight, ice |
| 22 | Cyan | `#88D4E8` | Crystal, magic water |
| 23 | Sky | `#3A6B9E` | Mana colour (matches UI guide) |
| 24 | Sky Light | `#6CA0CC` | Sky highlight |
| 25 | Gold Dark | `#8C6400` | Treasure shadow, coin dark |
| 26 | Gold | `#C8960C` | Gold, XP, highlight (matches UI) |
| 27 | Gold Light | `#FFD966` | Gold shimmer (matches UI hover) |
| 28 | Ember Dark | `#7A1A00` | Fire shadow, blood dark |
| 29 | Ember | `#C8401A` | HP red, fire mid (matches UI) |
| 30 | Flame | `#FF7733` | Fire bright |
| 31 | Amber | `#FFB347` | Torch light, warm glow |
| 32 | Rune Blue | `#4455FF` | Magic rune (matches UI rare) |
| 33 | Purple | `#7744AA` | Poison, shadow magic |
| 34 | Purple Light | `#AA44FF` | Arcane, very rare (matches UI) |
| 35 | Pink | `#DD88AA` | Charm, life magic accent |
| 36 | Transparency | — | Always colour index 0 / fully transparent |

> **Zone Accent Slots:** Each zone may add up to 4 palette entries beyond the 36 above, documented in the zone's tile spec. These must be declared in the zone's tile atlas metadata.

---

## 4. Reference Games & Mood Board

### 4.1 Primary References

| Game | Platform | What to Borrow | What to Avoid |
|------|----------|----------------|---------------|
| **The Legend of Zelda: Link's Awakening DX** (1998) | Game Boy Color | Zone personality, tile density, character silhouette clarity, dungeon atmosphere, sense of wonder in environmental detail | The simplicity of the original 8-colour palette — we have more colours to work with |
| **The Legend of Zelda: A Link to the Past** (1991) | SNES | Dungeon tile language, shadow treatment, overworld biome differentiation | Nothing — this is our tile bible |
| **Stardew Valley** (2016) | PC/Mobile | Town coziness, character expression in small sprites, warm palette for safe zones | The soft/pastel aesthetic that reads as modern indie — we want a slightly older-school feel |
| **Final Fantasy Tactics Advance** (2003) | GBA | Character class readability at small size, equipment visible in sprite, clean unit silhouettes | The isometric projection — we are top-down |
| **Secrets of Mana** (1993) | SNES | Lush overworld foliage, layered nature environments, bright colour contrast between zones | The ring-menu UI — already designed differently |

### 4.2 Overall Tone Description

**"Warm Dark Fantasy"** — the world is dangerous and mysterious, but not oppressive. Safe zones (towns, inns) feel genuinely welcoming: warm lantern light, cheerful colours, busy NPCs. Dangerous zones (dungeons, wastelands, crypts) feel threatening but beautiful: eerie colour palettes, detailed environmental storytelling, visible decay.

The game should feel like it exists in a world that was once grander — ancient ruins alongside thriving towns, old magic beside everyday commerce. Pixel art achieves this through: worn textures (dithered walls), environmental decay details (cracks, vines, rubble), and contrast between old-dark and new-bright tile elements within the same zone.

**Anti-goals:**
- Not grimdark (no gore, no despair aesthetics)
- Not saccharine (avoid overly pastel or "cute" — we want depth)
- Not modern indie (avoid the Undertale/Celeste visual language — we want pre-2000s SNES nostalgia)

---

## 5. Character Design Guidelines

### 5.1 Player Character — General Rules

All player characters are 32×32 base sprites. Overworld sprites must read their class at a glance.

**Silhouette Priority Rule:** Every class must be identifiable by silhouette alone (no colour). The shape — weapon, armour profile, headgear — must differ enough that two adjacent players of different classes are instantly distinguishable.

**Sprite States Required Per Character:**

| State | Frames | Notes |
|-------|--------|-------|
| Idle (facing down) | 2 | Subtle bob or breathing |
| Idle (facing up) | 2 | Back of character visible |
| Idle (facing left) | 2 | Profile view |
| Idle (facing right) | 2 | Mirrored from left or unique |
| Walk (4 directions) | 4 per direction = 16 total | Standard walk cycle |
| Attack (facing down) | 3 | Weapon swing or cast |
| Attack (facing up) | 3 | — |
| Attack (facing left) | 3 | — |
| Attack (facing right) | 3 | — |
| Hurt | 2 | Flash white + recoil frame |
| Death | 4 | Collapse animation |
| **Total frames per character** | **~50–52 frames** | Packed in a single sprite sheet per class |

> **Colour customisation:** Player characters support palette-swap for skin tone (4 options) and hair colour (8 options). These swaps operate on 2 reserved palette slots per character sprite — the base asset uses placeholder colours that the CTO replaces at runtime via shader uniform. Document the exact palette indices in the asset delivery spec (Section 8).

### 5.2 Player Character — Class Silhouette Guide

| Class | Silhouette Key Features | Primary Colours | Weapon Visible in Sprite |
|-------|------------------------|-----------------|--------------------------|
| **Warrior** | Broad armoured shoulders, helmet with visor or plume, large shield on back in idle | Steel grey, Ember red trim | Sword at hip |
| **Mage** | Tall pointed hat (or hood), robes with long sleeves, staff visible over shoulder | Deep purple, Gold rune accent | Staff over shoulder |
| **Rogue** | Slim profile, hood low over face, daggers visible at belt, short cape | Dark green, Bone accent | Dual daggers at hip |
| **Cleric** | Robed but with visible holy symbol on chest, simple helm, mace at belt | White/Bone robe, Gold holy symbol | Mace at hip |
| **Ranger** | Medium height, hooded cloak, bow slung across back, quiver visible | Earth brown, Moss green | Bow across back |
| **Paladin** | Heaviest armour silhouette of all classes, full-face helm, large two-handed sword or sword+tower shield | Gold-trimmed silver armour, Ember glow at joints | Two-handed sword or sword on back |

> **Design constraint:** No two classes may share the same silhouette profile. The Warrior and Paladin are both armoured — differentiate via the Paladin's tower shield width and glowing joint detail. At 32×32, glow is achieved by using a 1px lighter colour frame on the armour border, not actual glow effects.

### 5.3 NPC Archetypes — Silhouette Guide

NPCs are also 32×32 sprites. They use the same animation skeleton but require fewer states (idle 4-dir + talk state only for most NPCs).

| Archetype | Silhouette Key Features | Notes |
|-----------|------------------------|-------|
| **Merchant** | Rotund profile, wide-brimmed hat, bag or crate prop | Warm, approachable colours. Belly detail on idle bob |
| **Quest Giver** | Taller, upright stance, scroll or item held in hand | Distinguishable golden exclamation detail above head (UI overlay, not sprite) |
| **Guard** | Full armour, spear or halberd visible, helmet with plume | Zone-matched armour colour (Millhaven guard = blue, Aethermoor guard = gold) |
| **Townsperson** | Minimal, varied — apron, farmer hat, civilian clothes | Must clearly read as "not enemy". Warm colour family. No weapons |
| **Inn Keeper** | Apron, wide silhouette, lantern prop | Always behind a counter prop — counter is a map tile |

### 5.4 Enemy Archetypes — Silhouette Guide

Enemies must be visually distinct from players and NPCs at a glance. Use the "threat language" rule: enemies lean into dangerous shapes — sharp edges, darker palettes, hunched postures.

| Archetype | Silhouette Key Features | Palette Guidance |
|-----------|------------------------|-----------------|
| **Grunt** | Smaller than a player character. Hunched posture. One simple weapon | Earth/Shadow palette. Low palette count — designed for high-density spawns |
| **Elite** | Same height or taller than player. More armour, visible glow or rune effect. Distinct weapon | Richer palette than grunt. One accent colour unique to elite type |
| **Boss** | 64×64 sprite minimum (2×2 tile footprint). Imposing, fills zone emotionally | Zone-matched palette but desaturated and darker. Glow/rune effect on key body part. Unique silhouette not reused elsewhere |

**Enemy sprite states required:**

| State | Frames |
|-------|--------|
| Idle | 2 |
| Walk (4 directions) | 4 per direction |
| Attack | 3 |
| Hurt | 2 |
| Death | 4 |
| **Total per grunt/elite** | ~48 frames |

Boss enemies may have additional states (charge, roar, phase transition) — specify per boss in the dungeon bestiary.

---

## 6. Tile & Environment Style

### 6.1 Tile Categories

All world tiles are 32×32 pixels. Tiles are organised into themed tile sets — one tile set per zone-biome group. Each tile set is a single atlas texture (see Section 8).

#### 6.1.1 Ground Tiles

| Category | Variants Required | Notes |
|----------|------------------|-------|
| Grass | Base, Light variant, Dark variant, Edge (8-direction transitions) | Millhaven Fields, Thornwood |
| Stone/Cobblestone | Base, Worn, Cracked, Edge transitions | City streets, dungeon floors |
| Water | Shallow, Deep, Animated ripple (2 frames), River edge | Millhaven Docks, Crystal Caves |
| Dirt | Base, Path, Rocky dirt | Overworld roads, cave floors |
| Sand | Base, Wet, Transition to stone | Beach zones, desert |
| Dungeon Floor | Stone slab, Flagstone, Cracked flagstone, Rubble | Sunken Crypt, Ruins |
| Snow | Base, Icy, Footprint variant (decorative) | Frostpeak Mountains |
| Corrupted | Void-cracked stone, Glowing rune ground | Aether Wastes |

#### 6.1.2 Wall Tiles

| Category | Variants Required | Notes |
|----------|------------------|-------|
| Dungeon Wall | Solid, Cracked, Mossy, Torchlit (holds torch sprite) | One tile-set per major dungeon biome |
| Forest Wall (tree mass) | Solid canopy, Canopy edge (8-dir), Dark canopy (night) | Trees rendered as top-down canopy, trunk at base |
| Town Wall | Stone building, Wooden building, Door frame (open/closed variants) | Millhaven and City tiles differ in palette |
| Mountain | Rock face solid, Rock face ledge, Snow cap | Frostpeak, Crystal Caves |
| Water Wall (cliff into water) | Rocky cliff, Mossy cliff | Coastal zones |

> **Tilemap rule:** All walls must have both a "solid" variant and a "shadow receiver" variant. The CTO renders a 1-tile-height shadow below all wall tiles using a darkened transparent overlay — this is a rendering pass, not a separate tile.

#### 6.1.3 Object Tiles (Decorative & Interactive)

| Object | Size | Animated? | Interactive? |
|--------|------|-----------|-------------|
| Tree (oak) | 1×2 tiles (trunk + canopy) | No | No (solid wall) |
| Tree (pine) | 1×2 tiles | No | No |
| Barrel | 1×1 | No | Yes (smashable — 2 break frames) |
| Wooden Crate | 1×1 | No | Yes (smashable) |
| Chest (closed) | 1×1 | No | Yes (opens → 3 frame animation) |
| Chest (open, empty) | 1×1 | No | No |
| Door (closed) | 1×1 | No | Yes (opens → 2 frame animation) |
| Door (open) | 1×1 | No | No |
| Torch (wall) | 1×1 | Yes (3 frame flicker) | No |
| Campfire | 1×1 | Yes (4 frame burn) | No |
| Sign post | 1×1 | No | Yes (display text) |
| Dungeon stairs (down) | 1×1 | No | Yes (zone transition) |
| Dungeon stairs (up) | 1×1 | No | Yes (zone transition) |
| Gravestone | 1×1 | No | Yes (readable epitaph — Sunken Crypt lore) |
| Crystal growth | 1×1 | Yes (slow 4-frame shimmer) | No |
| Pressure plate | 1×1 | Yes (2 states: raised/depressed) | Yes (puzzle trigger) |
| Lever | 1×1 | Yes (2 states) | Yes (puzzle trigger) |

### 6.2 Lighting Style

**Chosen Style: Dithered Shadow with Torch-Based Warm Overlay**

- No real-time dynamic lighting (too expensive for MMO with many concurrent players)
- Lighting is baked into tile art — tiles in "lit" zones use normal palette; tiles in "dark" zones use a pre-darkened sub-palette
- Dungeon darkness is simulated by: (a) a darkened base palette for dungeon tile sets, and (b) a CSS/canvas radial gradient overlay centred on the player that reveals a pool of light (~6 tile radius)
- Torch/campfire objects emit a warm circle of visibility (3 tile radius, pre-calculated) — the CTO implements this as a second gradient mask layer
- Exterior zones (overworld, towns): full lighting. No darkness overlay. Time of day shifts are handled via colour palette tint (warm amber at dusk, cool blue at night)

**Dithering standard:** Use 2×2 checkerboard dithering (Bayer pattern) for all shaded transitions between lit and shadow areas within a tile. No smooth gradient pixels.

### 6.3 Zone Visual Themes

#### Millhaven (Cosy Town — Region 1 Starter Town)

| Property | Value |
|----------|-------|
| Palette mood | Warm, golden hour. Lots of Amber, Parchment, Moss |
| Ground tiles | Cobblestone path, Grass edges, Flower decorative details |
| Wall tiles | Wooden building walls, Thatched-style roof tops (decorative, non-collision), Stone chimney |
| Ambient objects | Hanging flower baskets (1×1 decorative), Well (1×1 interactive), Notice board (1×1) |
| Lighting | Full bright, warm amber tint at dusk/night cycle |
| Atmosphere intent | Player's first impression — should feel like home. Busy, friendly, safe |
| Signature tile | Cobblestone with moss growing in cracks — weathered but cared for |

#### Whispering Forest (Eerie Dark — Region 2, Thornwood Heart)

| Property | Value |
|----------|-------|
| Palette mood | Desaturated greens, muted blues, shadow-heavy. Very little warm colour |
| Ground tiles | Dark moss, Exposed root ground, Muddy path |
| Wall tiles | Dense dark canopy, Gnarled tree trunks, Hanging vine objects |
| Ambient objects | Skull on stake (environmental story), Ancient rune stone (readable lore), Firefly particle (animated 2-frame pixel dot) |
| Lighting | Dithered shadow. 5-tile player visibility radius in heart zone. Firefly objects provide tiny warm pinpoints |
| Atmosphere intent | Unease and mystery. Player should feel watched. Exploration is rewarded (lore scrolls, hidden paths) |
| Signature tile | Gnarled tree root ground tile — roots weave across the walkable path |

#### Sunken Crypt (Undead Dungeon — Region 1, Waterlogged Crypts)

| Property | Value |
|----------|-------|
| Palette mood | Stone, Bone, Rune Blue, muted Ember for torchlight |
| Ground tiles | Cracked flagstone, Standing water (shallow, animated), Rubble piles |
| Wall tiles | Crumbling stone blocks, Wall torch holders, Iron grate (bars) |
| Ambient objects | Gravestone (lore readable), Coffin (closed, smashable), Hanging chains (decorative), Wall crack with seeping water |
| Lighting | Heavy dungeon darkness. 4-tile player radius. Wall torches add 3-tile warm pools at fixed positions |
| Atmosphere intent | Classic dungeon dread. Sounds (design note: dripping water, distant moan) reinforce the visual. Environment tells the story of an ancient noble family's tomb flooded by underground rivers |
| Signature tile | Cracked stone floor with shallow water filling the crack — animated 2-frame ripple |

---

## 7. UI Art Style

> **Note:** The full UI component system is defined in `ui/style-guide.md`. This section defines only the **pixel-art asset specifications** for UI elements — what needs to be drawn, not how components are laid out.

### 7.1 HUD Elements to Commission

| Asset | Size | Notes |
|-------|------|-------|
| HP bar frame | 9-slice, 96×16px | Parchment dark border, stone track interior |
| Mana bar frame | 9-slice, 96×16px | Same shape, slightly different border decoration (arcane sigil at left end) |
| Hotbar slot frame | 56×56px | Stone dark background, worn border. Rarity colour replaces border when item equipped |
| Hotbar background strip | 9-slice, 512×64px | Stone panel, to hold all hotbar slots |
| Minimap frame | 9-slice, 128×128px | Circular or square (TBD — see Open Questions), parchment border with compass rose motif |
| Player HP/Name floating label bg | 9-slice, 64×12px | Dark panel for floating player name above character head |

### 7.2 Inventory & Panel Assets

| Asset | Size | Notes |
|-------|------|-------|
| Inventory panel frame | 9-slice, 320×400px | Parchment panel, decorative corner flourishes |
| Equipment slot (empty) | 48×48px | Stone background, faint outline of item type (helmet silhouette, boot silhouette, etc.) |
| Divider horizontal | 256×4px | Parchment dark horizontal rule with dot motif at centre |
| Character portrait frame | 64×64px | Circular or oval frame with fantasy border |
| Tab active indicator | 4×4px + 9-slice header | Gold underline treatment |
| Scroll bar track | 9-slice, 8×64px | Stone texture, scroll thumb in gold |

### 7.3 Icon Style

All icons are 16×16 pixel art, scaled to display size:

| Style Rule | Detail |
|-----------|--------|
| Palette | Icons use the global palette — max 8 colours per icon (excluding transparency) |
| Border | 1px dark outline on all icons (colour: `#0D0814` Void) |
| Shading | Top-left light source consistent with tile art |
| Recognisability | Silhouette must communicate item category before colour is processed |
| Consistency | All swords look like swords (angled blade, hilt guard); all potions look like potions (round body, cork, liquid fill colour varies by potion type) |

**Icon categories to commission:**

| Category | Count (Estimate) | Examples |
|----------|-----------------|----------|
| Weapons | ~20 | Sword, Dagger, Staff, Bow, Mace, Axe, Spear, Wand |
| Armour | ~15 | Helm, Chest, Legs, Boots, Gloves, Shield, Ring, Amulet |
| Potions/Consumables | ~10 | HP potion, Mana potion, Antidote, Scroll |
| Quest items | ~10 | Varies per quest — generic sacred relic, letter, key, gem |
| Currency | 3 | Copper coin, Silver coin, Gold coin |
| Ability/Spell | ~30 | One per class ability — see combat/spell design docs |
| Status effects | ~12 | Poison, Burn, Frozen, Stunned, Blessed, Cursed, Regenerating, Hasted, Slowed, Shielded, Feared, Charmed |
| Minimap markers | ~8 | Player, Party member, Enemy (red), NPC (yellow), Quest objective, Chest, Dungeon entrance, Waypoint |

### 7.4 Colour Language Confirmation

The following colour assignments are **confirmed** (aligned with UI Style Guide):

| Semantic | Colour | Hex |
|----------|--------|-----|
| Health / HP | Ember red | `#C8401A` |
| Mana / MP | Sky blue | `#3A6B9E` |
| XP / Experience | Gold | `#C8960C` |
| Stamina (if added) | Moss green | `#4A7C50` |
| Quest objective marker | Gold | `#FFD966` |
| Enemy health bar | Ember red | `#C8401A` |
| Friendly/Party health bar | Moss green | `#4A7C50` |
| Rarity: Common | Silver grey | `#C0C0C0` |
| Rarity: Uncommon | Green | `#44AA44` |
| Rarity: Rare | Blue | `#4444FF` |
| Rarity: Very Rare | Purple | `#AA44FF` |
| Rarity: Legendary | Orange/Gold | `#FF8800` |

---

## 8. Asset Delivery Spec

### 8.1 File Formats

| Asset Type | Format | Notes |
|-----------|--------|-------|
| All sprite sheets | PNG-32 (RGBA) | Lossless. No JPEG ever. |
| Tile atlases | PNG-32 (RGBA) | Same |
| UI sprite sheet | PNG-32 (RGBA) | Same |
| Atlas metadata | JSON (TexturePacker format) | See Section 8.3 |

### 8.2 Naming Convention

All files use **kebab-case**. Structure:

```
assets/
  sprites/
    characters/
      player-warrior.png           # Full sprite sheet for Warrior class
      player-warrior.json          # Atlas metadata
      player-mage.png
      player-mage.json
      ... (one pair per class)
      npc-merchant.png
      npc-merchant.json
      enemy-goblin-grunt.png
      enemy-goblin-grunt.json
      enemy-skeleton-elite.png
      enemy-skeleton-elite.json
      boss-waterlogged-warden.png  # Boss sprite (64×64)
      boss-waterlogged-warden.json
    effects/
      combat-effects.png           # All floating combat text frames, hit sparks
      combat-effects.json
  tiles/
    millhaven-town.png             # Tile atlas for Millhaven zone
    millhaven-town.json
    thornwood-forest.png
    thornwood-forest.json
    sunken-crypt.png
    sunken-crypt.json
    ... (one pair per zone biome group)
    objects-global.png             # Shared objects (chests, doors, barrels) across zones
    objects-global.json
  ui/
    ui-icons.png                   # All non-item UI icons
    ui-icons.json
    item-icons.png                 # All inventory item icons
    item-icons.json
    npc-portraits.png              # All NPC portrait sprites (48×48)
    npc-portraits.json
    hud-elements.png               # HP bar, mana bar, hotbar frames
    hud-elements.json
    panel-elements.png             # Inventory panels, tab frames, dividers
    panel-elements.json
```

### 8.3 Atlas / Sprite Sheet Format

All atlases use **TexturePacker JSON (Array format)** — compatible with Phaser.js out of the box via `this.load.atlas()`.

Each JSON file must include:

```json
{
  "meta": {
    "image": "filename.png",
    "size": { "w": 512, "h": 512 },
    "scale": "1",
    "aethermoor_version": "1.0",
    "palette_slots": [0, 1]
  },
  "frames": [
    {
      "filename": "player-warrior-idle-down-0",
      "frame": { "x": 0, "y": 0, "w": 32, "h": 32 },
      "rotated": false,
      "trimmed": false,
      "spriteSourceSize": { "x": 0, "y": 0, "w": 32, "h": 32 },
      "sourceSize": { "w": 32, "h": 32 }
    }
  ]
}
```

**Frame naming convention:** `{sprite-id}-{state}-{direction}-{frame}`
- `player-warrior-idle-down-0`
- `player-warrior-walk-left-2`
- `enemy-goblin-grunt-attack-up-1`
- `tile-millhaven-grass-base`
- `tile-millhaven-cobble-edge-nw`

### 8.4 Palette Swap Slots (Player Characters)

Each player character sprite must reserve exactly **two palette index groups** for runtime swapping:

| Slot Group | Default Colour | What It Controls |
|-----------|---------------|-----------------|
| Palette A (skin) | `#C8A882` (medium tone) | Skin colour — 4 pixels reserved |
| Palette B (hair) | `#3D2B1A` (dark brown) | Hair colour — 4 pixels reserved |

The CTO implements swapping via a Phaser.js shader uniform at character creation. Do not use these palette slots for any other visual element in the sprite.

**Available skin tones:** Light (`#F0D8B0`), Medium (`#C8A882`), Tan (`#9C6E40`), Dark (`#5A3A1A`)
**Available hair colours:** Black (`#1A0E0A`), Dark Brown (`#3D2B1A`), Brown (`#6B4F35`), Auburn (`#8C3A1A`), Red (`#C8401A`), Blonde (`#D9C89A`), White (`#EEF2F5`), Teal (`#2B6899`)

### 8.5 Tile Atlas Packing Rules

- Max atlas texture size: **2048×2048 pixels** per atlas
- Pack tiles in rows of 16 (512px wide at 32×32)
- Each zone biome group gets its own atlas — do not mix Millhaven and Sunken Crypt tiles in the same atlas
- Objects that appear across multiple zones (chests, doors, barrels) go in `objects-global` atlas
- Leave 1px padding around each tile in the atlas to prevent texture bleeding at 2× scale

---

## 9. MMO Considerations

| Concern | Design Response |
|---------|----------------|
| **Many players on screen simultaneously** | Character sprites must remain readable even when 10–20 are stacked in a zone. The silhouette-first design rule (Section 5.1) is specifically for this. At high density, the CTO may reduce non-local player opacity to 70% |
| **Palette memory** | All characters share the global palette. Zone-specific accent colours (max 4 per zone) are swapped at zone-load time, not per-entity. This keeps GPU texture memory manageable |
| **Enemy spawns at scale** | Grunt enemies (Section 5.4) are deliberately low-palette (max 6 colours) to keep texture atlas size small for high-density enemy zones |
| **Boss sprites (64×64)** | Boss sprites are loaded only when a player is in the dungeon instance. Not preloaded for all players |
| **Animated tiles** | Limit animated tiles to 2–4 frames. High-frame animations (torches, water) must be packed consecutively in the tile atlas to allow the CTO's animation system to step frames by index without separate draw calls |
| **Name labels above players** | Player name floating labels use a shared bitmap font render — not canvas text API. The CTO should pool label objects. Art spec: label background from `hud-elements` atlas, monospace pixel font |
| **Social presence legibility** | Guild tag colour is applied as a tinted border on the player name label background. Colour is set by guild — the CTO enforces a contrast minimum against the dark label background |

---

## 10. Technical Notes for CTO

1. **Phaser.js loader:** Use `this.load.atlas(key, imageUrl, jsonUrl)` for all sprite sheets and tile atlases. Frame keys follow the naming convention in Section 8.3.

2. **Tilemap format:** Zone tilemaps are authored in **Tiled** (JSON format) and loaded via `this.make.tilemap({ key: 'zone-id' })`. Each zone's tile atlas key must match the tilemap's tileset name property.

3. **Nearest-neighbour scaling:** Ensure `game.config.render.pixelArt = true` in Phaser config. This enables nearest-neighbour filtering globally. Do not set individual textures — the global config covers all.

4. **Palette swap shader:** A custom fragment shader is needed for player skin/hair swap. Input: sprite texture + two palette colour uniforms. Output: pixels matching the reserved palette slots are replaced with uniform values. This is a one-time implementation; all character sprites share the same shader.

5. **Dungeon darkness overlay:** Implement as a Phaser `Graphics` object rendering a full-screen dark rectangle at ~85% opacity, then `erase` the player visibility circle using `Graphics.fillCircle` with blend mode `ERASE`. Torch positions are static per zone load — add additional erase circles for each torch in range.

6. **Animated tiles:** Use Phaser's built-in Tilemap animation via `tilemap.setTileAnimationData()`. Animation frames must be consecutive in the tile atlas — document exact frame indices per animated tile in the zone atlas JSON metadata under a custom `aethermoor_animations` key.

7. **Atlas max size:** Keep all atlases at or under 2048×2048. Most mobile GPUs cap non-power-of-two textures at 2048. Verify at integration time.

8. **Character sprite sheets:** Each class is a separate atlas — do not combine classes into one texture. This allows streaming: load only the classes present in the current zone.

9. **Object interaction z-ordering:** Objects taller than 1 tile (trees, signs) must render above the player when the player is south of them, and below when the player is north. The CTO should use Phaser's `setDepth()` with the entity's `y` coordinate as the depth value.

10. **File delivery:** All assets are committed to the repository under `assets/` in the project root. The CTO references assets by their relative path from the Phaser boot scene. Do not embed asset data as base64.

---

## 11. Open Questions

| # | Question | Owner | Priority | Status |
|---|----------|-------|----------|--------|
| 1 | **Minimap frame shape:** Should the minimap be circular (more immersive, harder to implement) or square (simpler, more readable)? | CEO | Medium | Open |
| 2 | **Night/Day cycle palette tint:** Should the CTO apply a global colour tint to simulate dusk/night, or should we bake separate night-palette tile sets? Baked sets are more work but more visually controlled | CEO | High | Open |
| 3 | **Pixel font for in-world labels:** A custom bitmap pixel font is specified for tile-world labels (zone name pop-ups, gravestone text). Do we commission this or use a free pixel font (e.g., Press Start 2P from Google Fonts)? License check needed | CEO | Medium | Open |
| 4 | **Firefly particle system:** Whispering Forest uses firefly particles (Section 6.3). This requires a lightweight particle system. Does the CTO want this as animated sprites or as Phaser's built-in ParticleEmitter? | CTO | Low | Open |
| 5 | **Boss sprite pipeline:** Are boss sprites (64×64) considered a different production tier than regular enemies? Should we plan a separate budget/timeline for boss art? | CEO | Medium | Open |
| 6 | **Player customisation beyond skin/hair:** The spec currently defines skin tone and hair colour as the only palette-swap customisation. Should we add a clothing colour slot (cosmetic gear tinting)? This is scope expansion — flagged for CEO decision before implementation | CEO | Low | Open |

---

## 12. Version History

| Version | Date | Summary |
|---------|------|---------|
| 1.0 | 2026-04-15 | Initial release — full art direction spec covering core visual style, global palette (36 colours), 5 reference games, all 6 class silhouettes, NPC/enemy archetypes, tile categories, 3 zone visual themes, UI asset list, full delivery spec with naming conventions and atlas rules |
