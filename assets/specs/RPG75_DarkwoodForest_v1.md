# RPG-75 Darkwood Forest — Asset Spec (Draft v1)

## Overview

Zone 2 art assets for the Darkwood Forest. All assets match the Starter Zone's 32×32 pixel-art SVG
style with a darker, more foreboding colour palette. Output format: SVG placeholder sprites and
tileset tiles; final export as sprite sheets compatible with the Phaser tilemap system (32×32 tile
grid, 16×16 sub-pixel detail for characters).

---

## Colour Palette

| Role               | Hex       | Notes                              |
|--------------------|-----------|------------------------------------|
| Dark soil          | `#1A1209` | Base ground tile                   |
| Mid soil           | `#2A1E0E` | Ground variation / path highlight  |
| Pale soil          | `#3C2B14` | Ground specks, path edge           |
| Dark bark          | `#1C1208` | Tree trunk shadow                  |
| Mid bark           | `#2B1B0C` | Tree trunk base                    |
| Bark highlight     | `#4A3218` | Tree trunk lit edge                |
| Dark canopy        | `#0E1A08` | Tree crown shadow                  |
| Mid canopy         | `#172A0E` | Tree crown fill                    |
| Canopy highlight   | `#243B10` | Tree crown lit edge                |
| Undergrowth dark   | `#0D1507` | Undergrowth base                   |
| Undergrowth mid    | `#1A2A0E` | Undergrowth fill                   |
| Murky water dark   | `#0D1A17` | Water base                         |
| Murky water mid    | `#121F1A` | Water fill                         |
| Murky water sheen  | `#1E2E28` | Water surface highlight            |
| Path dark          | `#2D2218` | Path base                          |
| Path mid           | `#3D3020` | Path fill                          |
| Path highlight     | `#4E3E2A` | Path edge stones                   |
| Arcane purple      | `#7B4FC8` | Ruin glow, wraith accents          |
| Eerie green        | `#4FC87B` | Mushroom bioluminescence           |
| Bone white         | `#D0C8B0` | Skull props, ruin highlights       |
| Skin (NPC)         | `#C8A87A` | NPC face / hand                    |
| Fog grey           | `#3A4540` | Fog overlay (opacity 0.35)         |

---

## Tileset: Darkwood Ground Tiles

All tiles: 32×32 px, seamlessly tileable on a 32 px grid.

### `darkwood_ground_tile_v0.svg`
Dark compressed earth. Base tile for most of the forest floor.
- Fill: gradient `#1A1209` → `#2A1E0E`
- Texture specks: 4–6 circles r=1–1.5, colours `#3C2B14` / `#0F0C05`, opacity 0.5–0.7
- Tile edges must be flush (no bleed)

### `darkwood_tree_tile_v0.svg`
Forest tree tile (top-down view, trunk + crown). Occupies a single 32×32 cell.
- Trunk: 8×8 px centred, `#2B1B0C`
- Crown: 28×28 circle/rect with jagged top, `#172A0E`
- Crown highlight: single 4×4 lighter patch, `#243B10`

### `darkwood_undergrowth_tile_v0.svg`
Low ferns and roots overlay. Semi-transparent; layers over ground tile.
- Base: transparent
- Fern shapes: 3–4 small irregular rects/ellipses, `#1A2A0E` / `#0D1507`
- Root lines: 2–3 thin horizontal rects, `#2B1B0C`, opacity 0.6

### `darkwood_path_tile_v0.svg`
Packed-earth forest path. Slightly lighter than ground; worn stone edges.
- Fill: gradient `#2D2218` → `#3D3020`
- Edge stones: 2–3 rects 2×3 px at left/right edges, `#4E3E2A`
- Centre wear: 1–2 faint horizontal rects, `#3D3020`, opacity 0.5

### `darkwood_water_tile_v0.svg`
Murky stagnant water / bog.
- Fill: `#0D1A17`
- Surface ripple: 2 thin horizontal ellipses, `#1E2E28`, opacity 0.5
- Floating debris: 1–2 tiny dark specs, `#0A1510`

---

## Enemy Sprites (4 enemies)

All sprites: 32×32 px SVG (single idle frame placeholder). Final sprite sheets will include idle (4
frames), attack (3 frames), death (3 frames) at the same dimensions.

### `darkwood_shadow_wolf_idle_v0.svg`
Shadow Wolf — level 5–8, fast melee, bleeds darkness.
- Body: low hunched quad silhouette, `#1A1A2E` with `#2D2D4A` highlights
- Eyes: 2 px × 2 px pair, `#C84FC8` (violet glow)
- Fur spikes: jagged rect strips along spine, `#0D0D1C`

### `darkwood_bog_troll_idle_v0.svg`
Bog Troll — level 8–12, slow heavy hitter, regenerates.
- Body: wide squat biped, `#1A3A1A` / `#2A4A2A`
- Skin texture specks: `#0D2010`, opacity 0.7
- Eyes: 2 wide rects, `#F5C842` (yellow)
- Moss patches on shoulders: `#1A2A0E`

### `darkwood_wraith_idle_v0.svg`
Wraith — level 10–14, ranged magic, phases through obstacles.
- Body: tall wispy vertical shape, `#2A1A4A` fading to transparent at base
- Robe hem: soft edge with opacity gradient
- Arcane sigil on chest: simple cross/star shape, `#7B4FC8`
- Eye sockets: 2 px rects, `#C8A0FF`

### `darkwood_giant_spider_idle_v0.svg`
Giant Spider — level 6–10, web-slinger, venom stacks.
- Body: oval thorax + oval abdomen, `#1A0A0A` / `#2A1010`
- Legs: 8 thin 1 px lines extending from thorax, `#2A1010`
- Eyes: 6 tiny 1 px dots arranged in arc, `#F54F4F` (red)
- Web strand: 1 thin diagonal line from abdomen, `#C8C8C8`, opacity 0.5

---

## Environmental Props

Single-cell decorative objects (32×32 or 16×32 for tall props).

### `darkwood_dead_tree_v0.svg`
Leafless gnarled dead tree (32×48 — tall prop, spans 1×1.5 tiles).
- Trunk: 6 px wide, `#1C1208`, leans 5° left
- Branches: 3–4 bent rects extending at 30–60°, `#2B1B0C`
- No foliage. Bare branch tips: `#3C2B14`

### `darkwood_ruins_v0.svg`
Collapsed stone wall segment (32×24 — short prop).
- Stone blocks: 4–6 rects 8–12 × 6–8 px, `#2A2A2A` / `#3A3A3A`
- Mortar lines: 1 px gaps, `#1A1A1A`
- Arcane glyph on top stone: tiny cross shape, `#7B4FC8`, opacity 0.6
- Vine accent: 2 thin curved lines, `#1A2A0E`

### `darkwood_glowing_mushroom_v0.svg`
Bioluminescent mushroom cluster (16×24 — small prop).
- Cap: semicircle 12 px wide, `#1A3A20` with `#4FC87B` edge highlight
- Stem: 4×8 px rect, `#0F2A15`
- Glow halo: large circle 20 px r, `#4FC87B`, opacity 0.15

---

## NPC Sprites (2 NPCs)

All NPCs: 32×32 px SVG (idle facing down, single frame). Final sheets include idle (2 frames),
talking (2 frames).

### `darkwood_hermit_npc_v0.svg`
Forest Hermit — quest giver, reclusive mage who knows the forest's secrets.
- Silhouette: stooped elder in robes
- Robe: `#2A1A4A` (dark purple)
- Skin: `#C8A87A`
- Staff: 2 px × 20 px rect, `#4A3218`, topped with `#7B4FC8` orb (4 px circle)
- Hair/beard: long white `#E8E0D0` rects

### `darkwood_merchant_npc_v0.svg`
Travelling Merchant — vendor, sells forest-specific equipment. Wary, hooded.
- Silhouette: stocky figure with pack
- Cloak: `#3A2810` (dark brown)
- Hood: `#2A1E10`
- Pack: 8×10 px rect on back, `#4A3820`
- Skin: `#C8A87A`

---

## Zone Transition Asset

### `darkwood_zone_entry_v0.svg`
Entry/exit marker — stone archway at the boundary between Starter Zone and Darkwood Forest (64×64 px
— wide prop, spans 2 tiles).
- Two stone pillars: 8 px wide × 40 px tall each, `#2A2A2A`, separated by 48 px
- Arch lintel: 64×8 px rect across top, `#2A2A2A`
- Carved warning symbol on lintel: simple skull 8×8 shape, `#D0C8B0`
- Faint purple aura around archway: ellipse 60×48, `#7B4FC8`, opacity 0.12
- Ground worn path through arch: 16×8 px rect, `#3D3020`

---

## Phaser Integration Notes

- All tiles: 32×32 px grid, exported as tileset sprite sheet (PNG, rows of 10 tiles)
- Character sprites: 32×32 px frames, sprite sheet columns = animation frames
- Props with non-32 heights: place as static sprites, not tilemap tiles
- Zone entry marker: 64×64, static sprite, placed at map boundary (world coords TBD by Game Designer)
- Palette is intentionally desaturated vs Starter Zone — adjust Phaser scene tint if needed: `0x8899AA`
