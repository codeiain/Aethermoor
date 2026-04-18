# UI Component Style Guide

**Version:** 0.1.0
**Last Updated:** 2026-04-14
**Status:** Draft

---

## 1. Overview

This document defines the visual language, component standards, and interaction patterns for all UI elements in Aethermoor. It is the single source of truth for how the game's interface should look and feel. All UI components built by the CTO or future frontend engineers must conform to these standards.

The visual style is **fantasy pixel-art RPG** — warm, parchment-toned, with medieval decorative elements. UI should feel like it belongs in the world: aged wood, worn stone, ink on vellum — but remain clean and functional on a small mobile screen.

---

## 2. Design Goals

| Goal | Detail |
|------|--------|
| Thematic coherence | UI should feel like it belongs in Aethermoor's world, not like a modern app dropped in. |
| Functional clarity | Decorative elements must never impede readability or usability. |
| Consistent components | Every button, panel, and icon follows the same rules — no one-off styles. |
| Mobile legibility | Text and icons must be readable at 375px width under varied lighting conditions. |
| Performance-aware | UI assets are sprite-sheet based; avoid DOM-heavy effects on mobile. |

---

## 3. Colour Palette

### 3.1 Base Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `colour-parchment` | `#F5E6C8` | Panel backgrounds, tooltips |
| `colour-parchment-dark` | `#D9C89A` | Panel borders, dividers |
| `colour-ink` | `#2B1D0E` | Primary text |
| `colour-ink-faded` | `#6B4F35` | Secondary text, labels |
| `colour-stone` | `#5A5248` | Dark panel backgrounds (character sheet) |
| `colour-stone-light` | `#857E76` | Stone panel borders |
| `colour-gold` | `#C8960C` | Highlights, active states, quest icons |
| `colour-gold-light` | `#FFD966` | Hover states, selected tabs |
| `colour-sky` | `#3A6B9E` | Mana bar, magic UI elements |
| `colour-ember` | `#C8401A` | HP bar, danger states |
| `colour-moss` | `#4A7C50` | Daily quest badge, success states |
| `colour-void` | `#1A1022` | Endgame zone UI accents, background behind overlays |

### 3.2 Semantic Colour Mapping

| Semantic | Token | Usage |
|----------|-------|-------|
| Primary action | `colour-gold` | CTA buttons, confirm actions |
| Destructive action | `colour-ember` | Delete, flee, abandon |
| Success | `colour-moss` | Completed state, level-up |
| Info | `colour-sky` | Tooltips, passive info panels |
| Background overlay | `colour-void` @ 60% opacity | Behind full-screen overlays |

### 3.3 Rarity Colours

Used for item names and borders:

| Rarity | Hex | Display Name |
|--------|-----|-------------|
| Common | `#C0C0C0` | White/Grey |
| Uncommon | `#44AA44` | Green |
| Rare | `#4444FF` | Blue |
| Very Rare | `#AA44FF` | Purple |
| Legendary | `#FF8800` | Orange/Gold |

---

## 4. Typography

### 4.1 Fonts

| Role | Font | Notes |
|------|------|-------|
| UI Headings | **Cinzel** (Google Fonts, serif) | Fantasy-themed serif. Use for panel titles, zone names. |
| UI Body | **Lato** (Google Fonts, sans-serif) | Clean, highly legible. Use for descriptions, dialogue, tooltips. |
| Numbers / Stats | **Roboto Mono** (monospace) | Stat values, damage numbers, XP counters. Ensures alignment. |
| Pixel label | Pixel art bitmap font (custom, TBD) | Used for in-world labels on tiles only (not UI panels). |

### 4.2 Type Scale

| Token | Size | Weight | Usage |
|-------|------|--------|-------|
| `text-title` | 20pt | 700 | Panel titles (Inventory, Quest Log) |
| `text-heading` | 16pt | 600 | Section headings, NPC names |
| `text-body` | 14pt | 400 | Descriptions, dialogue, quest text |
| `text-label` | 12pt | 500 | Icon labels, stat row labels |
| `text-tiny` | 10pt | 400 | Cooldown countdown, rarity tags — use sparingly |

**Rule:** Never go below 12pt for any text the player needs to read. 10pt only for decorative or low-importance number overlays.

---

## 5. Spacing System

Uses an 8pt base grid. All spacing values are multiples of 8 (or 4 for fine-grained adjustments):

| Token | Value |
|-------|-------|
| `space-1` | 4pt |
| `space-2` | 8pt |
| `space-3` | 12pt |
| `space-4` | 16pt |
| `space-5` | 24pt |
| `space-6` | 32pt |
| `space-8` | 48pt |

Panels: inner padding `space-4` (16pt). Rows within panels: `space-2` (8pt) gap between items.

---

## 6. Component Specs

### 6.1 Buttons

#### Primary Button (CTA)
- Background: `colour-gold`
- Border: 2px `colour-parchment-dark`
- Text: `colour-ink`, `text-heading` weight
- Height: 56pt (mobile), 48pt (web)
- Border-radius: 4pt
- Pressed state: brightness -10%, slight inset shadow
- Disabled: `colour-parchment-dark` background, `colour-ink-faded` text

#### Secondary Button
- Background: `colour-parchment`
- Border: 2px `colour-parchment-dark`
- Text: `colour-ink`, normal weight
- Height: 48pt (mobile), 40pt (web)
- Same radius and press behaviour

#### Destructive Button
- Background: `colour-ember`
- Text: `colour-parchment` (white-ish)
- Height: same as Primary
- Used for: Abandon Quest, Drop Item, Flee Combat

#### Icon Button (Hotbar)
- Size: 56×56pt (mobile), 48×48pt (web)
- Background: `colour-stone` with `colour-stone-light` border
- Active/Selected: `colour-gold` border, brightness +5%
- Cooldown: radial sweep overlay in `colour-void` @ 70% opacity

### 6.2 Panels

#### Standard Panel (Parchment)
- Background: `colour-parchment`
- Border: 2px `colour-parchment-dark`, with optional 4px outer `colour-stone` shadow
- Corner: 6pt border-radius
- Inner padding: `space-4`
- Decorative corner motif: small pixel-art corner flourish (sprite, optional on small panels)

#### Dark Panel (Stone) — Character Sheet, Spellbook
- Background: `colour-stone`
- Border: 2px `colour-stone-light`
- Text: `colour-parchment`
- Same inner padding and radius

#### Tooltip Panel
- Background: `colour-void` @ 90% opacity
- Text: `colour-parchment`
- Max width: 220pt
- Show on: tap-and-hold (mobile), hover (web)
- Dismiss: tap elsewhere or mouse-out

### 6.3 Progress Bars

#### HP Bar
- Fill: `colour-ember`
- Background track: `colour-stone`
- Height: 12pt
- Border-radius: 6pt (pill shape)
- Low HP pulse: when HP < 25%, add a slow pulse animation (opacity 100%→70%→100%, 1.5s cycle)

#### Mana / Spell Slot Bar
- Fill: `colour-sky`
- All other properties: same as HP bar

#### XP Bar
- Fill: `colour-gold`
- Shown on Character Sheet only (not main HUD)

#### Cooldown Radial
- Circular radial overlay on top of hotbar icon
- Fill: `colour-void` @ 70% opacity, sweeps clockwise from top
- Number countdown in `colour-parchment`, `text-tiny`, centred on icon

### 6.4 Item Slot / Equipment Slot

- Size: 48×48pt minimum
- Background: `colour-stone`
- Empty: darker `colour-stone` with faint item-type icon in `colour-stone-light`
- Filled: item sprite centred; rarity-colour border (see Section 3.3)
- Selected: `colour-gold-light` outer border glow

### 6.5 Tab Bar

- Height: 40pt
- Active tab: `colour-parchment` background, `colour-gold` bottom border 3px, `text-heading` text
- Inactive tab: transparent, `colour-ink-faded` text
- Background strip: `colour-parchment-dark`

### 6.6 Dialogue Response Options

- Full-width tap targets
- Height: 48pt minimum
- Background: transparent, `colour-parchment-dark` divider between options
- Text: `colour-ink`, `text-body`
- Pressed: `colour-gold-light` background flash (50ms)
- Always prefixed with `→ ` to indicate tappable action

### 6.7 Floating Combat Text

- Damage: `colour-ember` bold, `text-heading` size
- Critical hit: `colour-gold` bold, `text-title` size, slightly larger
- Miss: `colour-ink-faded` italic, `text-body` size
- Heal: `colour-moss` bold, `text-heading` size
- Spawn position: above the affected entity, drifting upward over 1.5 seconds then fading
- Do not stack: offset successive events left/right to avoid overlap

---

## 7. Icons and Sprites

### 7.1 Icon Sizes

| Context | Icon Size |
|---------|-----------|
| Hotbar action | 40×40pt (within 56pt button) |
| Inventory item | 32×32pt (within 48pt slot) |
| Minimap markers | 12×12pt |
| Condition status | 16×16pt |
| Quest type badge | 10×10pt dot |

### 7.2 Sprite Sheet Organisation

All UI icons are packed into a single sprite sheet:
- `ui-icons.png` — all non-item UI icons (minimap markers, condition icons, quest badges)
- `item-icons.png` — all item/equipment icons (32×32 per item)
- `npc-portraits.png` — all NPC portrait sprites (48×48 per NPC)

Avoid individual icon files — all icon rendering must reference the sprite sheet to minimise draw calls.

### 7.3 Pixel Art Rules

- All sprites: 16×16 pixel base grid (scaled up 2× or 3× for display)
- Limited palette: max 16 colours per sprite, not counting transparency
- No anti-aliasing or sub-pixel rendering — pixels must be crisp
- Consistent light source: top-left for all environment sprites

---

## 8. Animation Standards

| Animation | Duration | Easing |
|-----------|----------|--------|
| Panel slide-in (bottom sheet) | 250ms | ease-out |
| Panel slide-out | 200ms | ease-in |
| Overlay fade-in | 150ms | linear |
| Button press flash | 50ms | linear |
| Floating combat text rise | 1500ms | ease-out |
| HP bar change | 300ms | ease-out |
| Cooldown sweep | real-time (no ease) | linear |
| Low HP pulse | 1500ms cycle | ease-in-out |
| Level-up burst | 600ms | ease-out |

**Rule:** No animation should block user input. All animations are decorative; gameplay is never gated on an animation completing.

---

## 9. Platform Adaptations

| Property | Mobile | Tablet | Web |
|----------|--------|--------|-----|
| Panel type | Bottom sheet / full overlay | Side drawer or overlay | Fixed side panel |
| Button heights | 56pt | 48pt | 40pt |
| Hotbar slots | 4 | 6 | 8 |
| Font scale | 100% | 110% | 100% |
| Hover states | Not used | Not used | Active |
| Drag-and-drop | Long-press-drag | Long-press-drag | Click-drag |

---

## 10. Open Questions

| # | Question | Owner | Priority |
|---|----------|-------|----------|
| 1 | Is Cinzel font licensed for game use? Need to confirm Google Fonts license compatibility. | CTO | High |
| 2 | Should we support a "dark mode" for the UI (inverse parchment/stone themes)? | CEO | Low |
| 3 | Should floating combat text be a user-toggle? Some players find it distracting. | CEO | Low |
| 4 | Are we building UI in a game framework (Phaser/PixiJS overlays) or in native HTML/CSS over a canvas? This affects which of the above are implemented as sprites vs DOM elements. | CTO | Critical |

---

## 11. Version History

| Version | Date | Summary |
|---------|------|---------|
| 0.1.0 | 2026-04-14 | Initial draft — colour palette, typography, spacing, all component specs, animation standards |
