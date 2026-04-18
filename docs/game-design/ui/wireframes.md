# AETHERMOOR — UI Wireframes & HUD Specification v1.0

**Author:** Game Designer
**Date:** 2026-04-14
**Status:** Draft v1.0
**Engine:** Phaser.js (canvas) + React (overlay UI shell)
**Target Platforms:** Mobile (iOS/Android via WebView), Tablet, Web (desktop browser)
**Reference:** GDD v0.4 (RPGAA-2), World Map v1.0 (RPGAA-11)

---

## Table of Contents

1. Screen Inventory
2. HUD Layout — Main Gameplay Screen
3. Key Screen Layouts — Game World, Inventory, Character Sheet
4. Secondary Screen Layouts — Quest Journal, Map, Social, Auction House, Login/Registration, Character Select, Character Creation, Settings
5. Component Style Guide
6. Mobile-First Constraints
7. Navigation Flow Map
8. MMO Considerations
9. Technical Notes for CTO
10. Open Questions
11. Version History

---

## 1. Screen Inventory

All screens/views in the AETHERMOOR application. The app is a single-page React shell; Phaser.js renders the game world on a `<canvas>` that fills the background when in gameplay mode.

| # | Screen Name | Trigger | Platform Notes |
|---|---|---|---|
| 1 | Splash / Loading | App launch | Full-screen, canvas hidden |
| 2 | Login / Registration | On launch (unauthenticated) | Full-screen overlay |
| 3 | Character Select | Post-login, up to 3 slots | Full-screen overlay |
| 4 | Character Creation | New slot selected | Full-screen overlay (multi-step) |
| 5 | Game World (HUD) | Character selected, loading complete | Phaser canvas + HUD overlay |
| 6 | Inventory | Hotbar/menu trigger | Panel overlay (does not pause game) |
| 7 | Character Sheet | Menu trigger | Panel overlay (does not pause game) |
| 8 | Quest Journal | Menu trigger | Panel overlay |
| 9 | World Map / Minimap | M key / minimap tap | Map overlay (mobile: full-screen; desktop: windowed) |
| 10 | Social Panel | Party/Guild icon tap | Side-drawer overlay |
| 11 | Auction House | AH NPC interaction | Full panel (game paused/blurred) |
| 12 | Settings | Gear icon | Full panel |
| 13 | Dialog / NPC | NPC interaction | Bottom-sheet dialogue box |
| 14 | Cutscene / Lore | Story triggers | Full-screen, canvas letterboxed |
| 15 | Death Screen | Player HP = 0 | Full-screen overlay |

---

## 2. HUD Layout — Main Gameplay Screen

The HUD is a **React DOM layer** mounted over the Phaser canvas (CSS `position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none`). Interactive HUD elements use `pointer-events: auto` selectively to pass touches/clicks through to Phaser where needed.

### 2.1 Layout Zones (All Platforms)

```
┌─────────────────────────────────────────────────────┐
│ [A] Zone Name + Level        [B] Quest Tracker       │  ← TOP BAR (React overlay)
├──────────────────────────────────────────────────────┤
│                                                      │
│                                                      │
│                  PHASER CANVAS                       │
│               (game world renders here)              │
│                                                      │
│  [F] Virtual Joystick (mobile only, bottom-left)    │
│                                                      │
├──────────────────────────────────────────────────────┤
│ [C] HP/MP Bars + Avatar  [D] Hotbar   [E] Minimap   │  ← BOTTOM BAR (React overlay)
└─────────────────────────────────────────────────────┘
```

### 2.2 HUD Element Definitions

#### [A] Zone Name + Level Indicator (Top-Left)
- **Position:** Top-left, 12px from left, 12px from top (safe area inset aware)
- **Content:** Zone name (e.g., "Thornwood Heart") + zone level range (e.g., "Lv. 7–11")
- **Size:** Auto-width, ~24px height label
- **Visibility:** Fades in on zone entry, fades out after 4 seconds; re-shows on hover/tap
- **Mobile:** Always visible (no fade) to orientate players

#### [B] Quest Tracker (Top-Right)
- **Position:** Top-right, 12px from right, 12px from top (safe area inset aware)
- **Content:** Active quest name + current step description (max 2 lines, truncated)
  - Up to 3 tracked quests displayed (one highlighted, others collapsed)
- **Width:** Max 240px (desktop/tablet), 180px (mobile)
- **Tap/Click:** Opens Quest Journal panel
- **Dismiss:** X button on each entry; tap tracked quest to cycle active

#### [C] HP/Mana Bars + Avatar (Bottom-Left)
- **Position:** Bottom-left corner, 12px from left, bottom safe-area-inset + 12px
- **Layout:**
  ```
  ┌────┐  ██████████░░░░  HP 120/150
  │ AV │  ████░░░░░░░░░░  MP  40/90
  └────┘  
  ```
  - Avatar: 40×40px player portrait (class icon fallback), 2px pixel-border
  - HP bar: 120px wide (desktop/tablet), 96px (mobile), 10px tall, red fill
  - MP bar: Same width, 8px tall, blue fill
  - Numeric labels: `HP ###/###` and `MP ###/###`, right-aligned, 10px font
  - **Target frame:** When targeting an enemy/NPC, a second HP bar appears above the player frame showing target HP + name (enemy frame, 160px wide, no MP bar)
- **Platform adjustments:**
  - Mobile portrait: Avatar 32×32px, bars 80px wide
  - Stack vertically if bottom bar too crowded on 360px-wide screens

#### [D] Hotbar (Bottom-Center)
- **Position:** Bottom-center, centered horizontally, bottom safe-area-inset + 12px
- **Desktop/Tablet layout:** 10 slots in a single row
  ```
  ┌──┬──┬──┬──┬──┬──┬──┬──┬──┬──┐
  │1 │2 │3 │4 │5 │6 │7 │8 │9 │0 │
  └──┴──┴──┴──┴──┴──┴──┴──┴──┴──┘
  ```
  - Each slot: 44×44px, 2px gap, 2px pixel border
  - Number key label top-left (12px font), cooldown overlay (radial timer)
  - Item/ability icon (32×32px centered)
  - Keyboard shortcut: 1–9, 0

- **Mobile layout:** 6 primary slots + expandable tray
  ```
  ┌──┬──┬──┬──┬──┬──┐  [+]
  │1 │2 │3 │4 │5 │6 │  expand
  └──┴──┴──┴──┴──┴──┘
  ```
  - Primary 6 slots: 48×48px (minimum touch target)
  - [+] expand button: reveals slots 7–10 in a secondary row above
  - Slot labels omitted on mobile (no keyboard)

- **Cooldown display:** Radial grey overlay on icon, countdown number center-bottom
- **Out-of-mana indicator:** Blue tint + MP icon flash on affected slots
- **Right-click / long-press:** Opens slot context menu (assign ability, assign item, clear)

#### [E] Minimap (Bottom-Right)
- **Position:** Bottom-right, 12px from right, bottom safe-area-inset + 12px
- **Size:** 96×96px circular cropped (desktop/tablet); 72×72px (mobile portrait)
- **Content:**
  - Zone tile-map birds-eye (pre-rendered, low-res)
  - Player marker: white arrow at center, rotates with player facing
  - Nearby players: blue dots (party: green dots)
  - Quest objective markers: yellow star icons
  - Dungeon/POI icons: anchor, skull, chest (per zone POI type)
  - North indicator: 'N' label at top edge
- **Zoom levels:** 3 levels (tap minimap cycles through: Close / Normal / Far)
- **Tap/Click:** Opens full World Map overlay
- **Toggle:** Map button (M key / minimap icon tap) hides/shows minimap

#### [F] Virtual Joystick (Mobile Only)
- **Position:** Bottom-left, dynamic — appears where thumb first touches the left half of screen; disappears when released (floating joystick pattern)
- **Size:** 120px outer ring, 48px inner handle, semi-transparent (40% opacity)
- **Behaviour:** 8-directional input passed to Phaser movement system; dead zone = 10px
- **Platform:** Mobile and tablet only; hidden on desktop

#### [G] Right-Side Action Buttons (Mobile/Tablet Only)
- **Position:** Bottom-right cluster, above minimap
- **Buttons (48×48px each, 8px gap):**
  ```
  [ATK]
  [INT]  [JUMP/DODGE]
  ```
  - **ATK:** Primary attack (maps to Hotbar slot 1 action)
  - **INT:** Interact / examine (contextual)
  - **DODGE:** Roll/dodge (maps to character dodge ability or spacebar equivalent)
- **Desktop:** These actions are keyboard-only (Z = attack, E = interact, spacebar = dodge)

#### [H] Menu Icon Row (Top-Right, below quest tracker or separate)
- **Position:** Right side, mid-screen or top-right below quest tracker
- **Icons (32×32px, stacked vertically on mobile; horizontal row on desktop):**
  - Bag icon → Inventory
  - Scroll icon → Quest Journal
  - Person icon → Character Sheet
  - Globe icon → World Map
  - People icon → Social Panel
  - Gear icon → Settings
- **Mobile:** Icons grouped in a 2×3 grid accessible via a "≡" hamburger button (to conserve screen space)

#### [I] Chat Bar (Bottom, above hotbar or separate)
- **Position:** Bottom-left area, above HP bars; or a collapsible panel
- **Desktop:** Always visible, 320px wide, 5 lines visible, scrollable
- **Mobile:** Collapsed by default; chat bubble icon top-left expands to overlay chat panel
- **Input:** Text field with send button; mobile keyboard raises safely (chat panel scrolls up)
- **Channels:** General / Party / Guild / Whisper — tab-selectable

#### [J] Player Name + Level Badge
- **Position:** Above player avatar (atop HP bar area) or floating above the sprite in-canvas
- **Content:** Player name + Level number
- **Note:** In-canvas player name/level label rendered by Phaser above sprite at all times; the React HUD does not duplicate this

---

## 3. Key Screen Layouts

### 3.1 Game World (HUD Active) — Full Layout Summary

**Mobile Portrait (360×780px example)**
```
┌───────────────────────────────────┐
│ [Zone: Thornwood Heart Lv7-11]    │ ← 44px top bar (safe area)
│                    [Quest Tracker]│
│                                   │
│                                   │
│       PHASER CANVAS               │ ← Fills screen
│       (top-down tile world)       │
│                                   │
│                                   │
│  [Virtual Joystick area]          │
│  (appears on touch)               │
│                                   │
│                     [ATK][INT]    │
│                         [DODGE]   │
│ ┌──┐ ████░  MP ████░    [Minimap] │
│ │AV│ HP bars                      │ ← 72px bottom HUD
│ └──┘ [1][2][3][4][5][6][+] [≡]   │
└──────────────────────────────[---]┘ ← Home gesture bar (safe)
```

**Desktop (1280×800px)**
```
┌────────────────────────────────────────────────────────────────┐
│ [Zone Name — Lv Range]              [Quest Tracker — 240px]    │ ← 40px
│                                     [Bag][Scroll][Person][Map] │
│                                                                 │
│                                                                 │
│                       PHASER CANVAS                            │ ← flex fill
│                                                                 │
│                                                                 │
│ ┌──┐ ████████░  HP  ┌──┬──┬──┬──┬──┬──┬──┬──┬──┬──┐ ◉Minimap │
│ │AV│ ████░░░░  MP  │1 │2 │3 │4 │5 │6 │7 │8 │9 │0 │  96px   │ ← 64px
│ └──┘               └──┴──┴──┴──┴──┴──┴──┴──┴──┴──┘          │
│ [Chat: General ▼                    ]                          │
└────────────────────────────────────────────────────────────────┘
```

---

### 3.2 Inventory Screen

**Trigger:** Bag icon tap / 'I' key
**Type:** Panel overlay — game continues in background (no pause)
**Breakpoints:** Mobile = full-screen slide-up sheet; Tablet/Desktop = right-side panel (420px wide)

**Layout:**
```
┌─────────────────────────────────────────────────┐
│ INVENTORY             Weight: 42/100   [X Close] │  ← Header
├──────────────────────────────────────────────────┤
│ [EQUIPPED]                                       │  ← Tab bar
│ Head    ┌──┐  ┌──┐  ┌──┐  ┌──┐  ┌──┐            │
│ Body    │  │  │  │  │  │  │  │  │  │            │
│ Hands   └──┘  └──┘  └──┘  └──┘  └──┘            │
│ Legs    Row 1 of 5-col grid, 6 rows (30 slots)   │
│ Feet    ┌──┐  ┌──┐  ┌──┐  ┌──┐  ┌──┐            │
│ Weapon  │  │  │  │  │  │  │  │  │  │            │
│ Off-hand└──┘  └──┘  └──┘  └──┘  └──┘            │
│ Ring×2                                           │
│ Neck                                             │
│                                                  │
│ [Sort]  [Filter: ▼ All]            Gold: 1,240g  │  ← Footer
└──────────────────────────────────────────────────┘
```

**Equipment panel** (left strip, 80px wide on desktop/tablet; top strip on mobile):
- Slots: Head, Chest, Hands, Legs, Feet, Main Hand, Off-Hand, Ring×2, Neck, Back
- Each slot: 44×44px icon with slot-type label below
- Equip: tap item in grid → context menu appears → "Equip" / "Use" / "Drop" / "Compare"
- Compare: hovering/long-pressing item shows comparison tooltip vs. equipped item

**Inventory grid:**
- Desktop: 5 columns × 6 rows = 30 slots per page (paginated or scrollable)
- Mobile: 4 columns × 7 rows (slot size 56×56px for touch comfort)
- Slot capacity: 30 base + 10 per Bag expansion item (up to 3 bags = 60 max)
- Stack display: quantity badge bottom-right of slot (e.g., "×12")

**Filters:** All / Weapons / Armour / Consumables / Quest Items / Materials / Misc

---

### 3.3 Character Sheet

**Trigger:** Person icon / 'C' key
**Type:** Panel overlay — no game pause
**Breakpoints:** Mobile = full-screen; Tablet/Desktop = right-side panel (480px wide)

**Layout:**
```
┌───────────────────────────────────────────────────┐
│ CHARACTER SHEET                         [X Close]  │ ← Header
├─────────────────┬─────────────────────────────────┤
│ [Portrait 80px] │  Kael Ironborn               │   │
│ Level 12        │  Warrior — Human             │   │
│ [Class Icon]    │  Guild: The Iron Vanguard     │   │
├─────────────────┴─────────────────────────────────┤
│ ABILITY SCORES                                     │
│  STR  18 (+4)    DEX  12 (+1)    CON  16 (+3)     │
│  INT   9 (-1)    WIS  10 (+0)    CHA  11 (+0)     │
├────────────────────────────────────────────────────┤
│ COMBAT STATS                                       │
│  HP: 120/150    MP: 40/90    AC: 16                │
│  Speed: 30ft    Initiative: +1    Proficiency: +4  │
│  Attack Bonus: +8    Spell Save DC: —             │
├────────────────────────────────────────────────────┤
│ SKILLS (collapsed — tap to expand)                 │
│  ▼ Acrobatics +1  Athletics +8  Intimidation +4…  │
├────────────────────────────────────────────────────┤
│ [SPELLBOOK tab]  [FEATS tab]  [BACKGROUND tab]     │
│  (switches lower section content)                  │
├────────────────────────────────────────────────────┤
│ FEATS (level 12 example):                          │
│  • Great Weapon Master  • Sentinel  • +2 STR ASI   │
├────────────────────────────────────────────────────┤
│ XP: 23,400 / 30,000   [████████████░░░░░░░]       │
│ Next level: 6,600 XP remaining                     │
└────────────────────────────────────────────────────┘
```

**Tabs below combat stats:** Feats | Spellbook | Background | Proficiencies

**Mobile adjustments:**
- Ability scores displayed as 2×3 grid (2 columns, 3 rows) rather than 3×2
- Sections are collapsible accordions (tap header to expand/collapse)
- Swipe left/right to navigate tabs

---

## 4. Secondary Screen Layouts

### 4.1 Quest Journal

**Trigger:** Scroll icon / 'J' key
**Type:** Panel overlay (640px desktop; full-screen mobile)

```
┌──────────────────────────────────────────────────┐
│ QUEST JOURNAL                          [X Close]  │
├─────────────┬────────────────────────────────────┤
│ [Main]      │  ▶ The Aethermoor Awakening        │ ← Active quest header
│ [Side]      │  ─────────────────────────────     │
│ [Daily]     │  Step 3: Find the Resonance Stone  │
│ [Completed] │  in Crystal Caves (Zone: crystal-  │
│             │  caves-deep).                       │
│ QUEST LIST  │                                    │
│ ─────────── │  OBJECTIVES                        │
│ • The       │  ☐ Enter Crystal Caves Deep        │
│   Aether... │  ☑ Speak to Lore Keeper Aeryn      │
│ • Missing   │  ☐ Collect Resonance Stone (0/1)   │
│   Merchant  │                                    │
│ • Goblin    │  REWARDS                           │
│   Bounty    │  1,200 XP | 80g | [Aether Pendant] │
│ [+4 more]   │                                    │
│             │  [Track Quest]  [Abandon Quest]    │
└─────────────┴────────────────────────────────────┘
```

- Left: quest list filtered by selected tab; active quests show gold dot; tracked = star icon
- Right: selected quest detail (steps, objectives tick-list, rewards)
- Daily quests show reset timer (e.g., "Resets in 6h 42m")

---

### 4.2 World Map

**Trigger:** Globe icon / 'M' key / minimap tap
**Type:** Full-screen overlay (all platforms)

```
┌────────────────────────────────────────────────────────┐
│ WORLD MAP — AETHERMOOR           [X Close]  [Legend ▼] │
│                                                         │
│  ┌────────────────────────────────────────────────┐    │
│  │    [Rendered overworld map image/tileset]       │    │
│  │                                                 │    │
│  │    ● You are here (Thornwood Heart)             │    │
│  │    ★ Quest objective                            │    │
│  │    ▲ Dungeon entrance                           │    │
│  │    ⌂ Town / safe zone                          │    │
│  │    ✦ Fast travel waypoint (unlocked)            │    │
│  └────────────────────────────────────────────────┘    │
│                                                         │
│  [Pinch-to-zoom / scroll wheel zoom]                    │
│  Zone name tooltip on tap/hover                         │
│  Fast travel: tap waypoint → confirm dialog → teleport  │
│                                                         │
│  LEGEND:  ● You  ★ Quest  ▲ Dungeon  ⌂ Town  ✦ Waypoint│
└────────────────────────────────────────────────────────┘
```

- Map is a pre-rendered layered canvas (Phaser scene or static image + SVG overlay)
- Undiscovered zones shown as greyed-out silhouette (fog-of-war)
- Zone tooltips on hover/tap: zone name, level range, biome, contested status
- Fast travel restricted to unlocked waypoints; cost: 5g or free for party leader

---

### 4.3 Social Panel

**Trigger:** People icon
**Type:** Right-side drawer (320px wide; full-screen on mobile)

**Tabs:** Party | Guild | Friends | Nearby

- **Party tab:** Party members (up to 5) with HP/MP bars, class icon, level. Invite/kick controls for leader.
- **Guild tab:** Guild name, rank, online members list (name, level, zone). Guild message of the day.
- **Friends tab:** Friends list — online/offline, last seen zone.
- **Nearby tab:** Players within current zone shard — names, levels, class icons. "Invite to Party" button.

---

### 4.4 Auction House

**Trigger:** AH NPC interaction in-world
**Type:** Full-panel overlay (game canvas blurred behind it)

```
┌────────────────────────────────────────────────────────┐
│ AUCTION HOUSE                              [X Close]   │
├──────────────┬─────────────────────────────────────────┤
│ [Browse]     │ SEARCH: [______________] [Search]        │
│ [My Listings]│ Filter: [All ▼] [Rarity ▼] [Level ▼]    │
│ [Sell]       ├─────────────────────────────────────────┤
│              │ ITEM             LEVEL  PRICE   BUYOUT  │
│              │ Aethersteel Sword  10   250g    500g    │
│              │ Verdant Robe       12   180g    350g    │
│              │ Iron Shield         5    45g     90g    │
│              │ …                                       │
│              ├─────────────────────────────────────────┤
│              │ [Selected item detail + stats]          │
│              │ Seller: TavernKeep | Expires: 23h 14m   │
│              │ [Bid: 260g] [Buyout: 500g]              │
└──────────────┴─────────────────────────────────────────┘
```

- Sell tab: drag item from inventory (or tap-select on mobile) → set minimum bid + buyout price + duration (12h / 24h / 48h) → post (listing fee: 1% of buyout)
- My Listings: shows active listings with time remaining and bid status; cancel button
- Mobile: full-screen, tabs at top, item list scrollable

---

### 4.5 Login / Registration

**Type:** Full-screen, Phaser canvas hidden

```
┌─────────────────────────────────┐
│         AETHERMOOR              │
│      [Animated logo area]       │
│                                 │
│  [Email / Username ___________] │
│  [Password        ___________] │
│                                 │
│  [       LOG IN       ]        │
│  [  Create Account  ]          │
│  [Continue with Google]        │
│  [Continue with Apple ]        │
│                                 │
│  Forgot password?               │
└─────────────────────────────────┘
```

- Full-screen, centered card on desktop (max 400px wide, auto-margins)
- Mobile: full-screen scroll, keyboard raises safely
- Registration: email + username + password (separate step) → email verify → redirect to Character Select

---

### 4.6 Character Select

**Type:** Full-screen overlay (3 character slots)

```
┌──────────────────────────────────────────────────────┐
│              SELECT YOUR CHARACTER                    │
│                                                       │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│  │   [Sprite]   │ │   [Sprite]   │ │    [+]        │ │
│  │  Kael        │ │  Sylvara     │ │   Create      │ │
│  │  Warrior 12  │ │  Mage 7      │ │   New         │ │
│  │  Last: 2h    │ │  Last: 3d    │ │               │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ │
│                                                       │
│  [Play as Kael]     [Delete Character]                │
└──────────────────────────────────────────────────────┘
```

- Slot sprites: animated idle sprite (Phaser canvas element or GIF)
- Slot info: class, level, last played
- Empty slots show + Create New
- Delete: requires confirmation dialog with character name re-type

---

### 4.7 Character Creation (Multi-Step)

**Type:** Full-screen, step wizard

| Step | Content |
|------|---------|
| 1 | Race selection — 6 races in a grid (Human, Elf, Dwarf, Halfling, Tiefling, Dragonborn) — each shows art + trait summary |
| 2 | Class selection — 5 classes in a grid (Warrior, Mage, Rogue, Ranger, Cleric) — art + role + starter stats |
| 3 | Ability Score generation — "Roll 4d6 drop lowest" button (animated dice roll); reroll up to 3 times; manual point-buy toggle |
| 4 | Name + appearance — character name input (3–16 chars, alphanumeric + space); portrait colour variant picker |
| 5 | Confirm — shows full character summary; [Create Character] button |

- Progress bar at top showing step 1/5
- Back/Next navigation; Next disabled until step requirements met
- Mobile: each step is full-screen, scrollable; dice roll is a big tap-friendly button

---

### 4.8 Settings

**Type:** Full panel (tabbed)

**Tabs:** Audio | Graphics | Controls | Account | Accessibility

- **Audio:** Master / Music / SFX / Voice sliders (0–100%)
- **Graphics:** Quality preset (Low/Medium/High/Ultra), particle effects toggle, shadow toggle, UI scale (80–140%)
- **Controls:** Desktop key rebind table; mobile joystick size/opacity sliders; hotbar layout toggle
- **Account:** Display name, email, password change, linked accounts (Google/Apple), logout
- **Accessibility:** Colourblind mode (Protanopia / Deuteranopia / Tritanopia), font size override, reduced motion toggle, chat text size

---

## 5. Component Style Guide

### 5.1 Colour Palette

| Token | Hex | Usage |
|---|---|---|
| `ui-bg-dark` | `#1A1020` | Panel backgrounds, overlays |
| `ui-bg-mid` | `#2C2040` | Card interiors, secondary panels |
| `ui-bg-light` | `#3E3060` | Hover states, selected rows |
| `ui-border` | `#7A5CB0` | Panel borders, slot outlines |
| `ui-border-gold` | `#D4A832` | Highlighted/active elements, gold frames |
| `ui-text-primary` | `#F0EAD6` | Main body text (cream parchment) |
| `ui-text-secondary` | `#A09070` | Labels, subtext, disabled |
| `ui-text-accent` | `#FFD700` | Gold — quest rewards, active quests |
| `hp-full` | `#C8372A` | HP bar fill |
| `hp-low` | `#FF6B2B` | HP bar < 25% (pulses) |
| `mp-full` | `#2A60C8` | MP bar fill |
| `xp-fill` | `#22A060` | XP bar fill |
| `rarity-common` | `#CCCCCC` | White / grey |
| `rarity-uncommon` | `#44CC44` | Green |
| `rarity-rare` | `#4488FF` | Blue |
| `rarity-epic` | `#CC44FF` | Purple |
| `rarity-legendary` | `#FF8800` | Orange |

### 5.2 Typography

| Role | Font | Size | Notes |
|---|---|---|---|
| Game title / logo | `AetherFont` (custom pixel font TBD by artist) | 32–64px | All caps |
| UI headings | `PressStart2P` (Google Fonts) | 12–16px | All caps, pixel-perfect |
| UI body / labels | `PressStart2P` | 8–10px | Scale with UI scale setting |
| Tooltip / subtext | `PressStart2P` | 8px | Muted colour |
| Chat messages | System sans-serif (legibility priority) | 13px | Not pixel font — readability |
| Numbers (HP/MP) | `PressStart2P` or monospace | 10px | Monospace for number alignment |

- **Minimum readable size:** 8px at 1× scale on mobile (ensure UI scale ≥ 100% on mobile defaults)
- **Note for CTO:** `PressStart2P` is a Google Fonts open-source pixel font — no licensing cost; load via CDN in React shell.

### 5.3 Button / Panel Styles

**9-Patch Panels:**
- All UI panels use a 9-patch tileable pixel-art frame (dark `ui-bg-dark` fill, `ui-border` border, 2–4px border width)
- Corner assets: 8×8px pixel-art ornamental corners (matching SNES-era RPG aesthetic)
- CTO: implement as CSS `border-image` with the 9-patch sprite or as styled-components with explicit pixel borders

**Buttons:**
- Primary action (e.g., "Log In", "Equip"): `ui-border-gold` border, `ui-bg-mid` fill, `ui-text-accent` text — hover: `ui-bg-light`
- Destructive (e.g., "Delete Character"): `#8B0000` border, matching fill
- Disabled: greyed out at 40% opacity, `not-allowed` cursor

**Slot / Cell:**
- 44×44px (desktop) / 48×48px (mobile) pixel-art bordered cells
- Hover: `ui-bg-light` glow; Selected: `ui-border-gold` outline (2px)
- Rarity colour fills the bottom 4px of the slot frame

### 5.4 Icon Style

- All icons: 32×32px pixel art, consistent perspective (top-down/isometric-friendly)
- HUD icons (bag, scroll, person, map, etc.): 24×24px outlined in `ui-text-secondary`
- Status icons (poison, frozen, stunned): 16×16px pixel art above player sprite (Phaser layer)

### 5.5 Responsive Grid

| Breakpoint | Min Width | Columns | Gutter |
|---|---|---|---|
| Mobile portrait | 320px | 4 | 8px |
| Mobile landscape | 568px | 6 | 8px |
| Tablet | 768px | 8 | 12px |
| Desktop | 1024px | 12 | 16px |
| Wide | 1440px | 12 | 24px |

React UI panels use CSS Grid / Flexbox; Phaser canvas is `position: absolute` filling the viewport behind the React DOM shell.

---

## 6. Mobile-First Constraints

### 6.1 Touch Target Minimums

| Element | Minimum Size | Notes |
|---|---|---|
| Hotbar slots (mobile) | 48×48px | Per WCAG 2.5.5 (AAA) guideline |
| Menu icons | 44×44px | Apple HIG minimum |
| Inventory slots (mobile) | 56×56px | Larger for item accuracy |
| Buttons (destructive) | 48×48px | Prevent accidental presses |
| Chat send button | 44×44px | One-handed reachable |

### 6.2 Safe Area Insets

- React shell uses `env(safe-area-inset-top/bottom/left/right)` CSS variables throughout
- All HUD elements positioned with safe-area padding
- Bottom hotbar clears iOS home indicator bar (env(safe-area-inset-bottom) ≥ 34px on iPhone X+)
- Phaser canvas respects safe areas — game world fills full screen but interactive HUD avoids unsafe zones

### 6.3 Portrait vs. Landscape

| Mode | Default State | Behaviour |
|---|---|---|
| Portrait | Default on mobile | Full gameplay supported; hotbar 6 slots; minimap 72px |
| Landscape | Optional unlock in Settings | Hotbar expands to 8 slots; minimap 96px; side panels wider |
| Tablet | Defaults to landscape | Full 10-slot hotbar; map panel non-full-screen |

- **Orientation lock:** Game does NOT force landscape; supports both
- On orientation change: React layout re-flows; Phaser ScaleManager updates (FIT mode)

### 6.4 Performance Targets

| Metric | Target |
|---|---|
| Frame rate | 60fps on iPhone 12 / Pixel 6 (mid-range 2021+ devices) |
| React re-renders | HUD elements use `React.memo`; HP/MP update via RAF throttle (not per-frame React setState) |
| UI asset size | All UI sprite sheets ≤ 512×512px per atlas; separate atlas from world tiles |
| Initial load time | ≤ 3s on 4G for login screen; game world loads progressively |
| Touch input latency | Pointer event handlers on Phaser canvas; avoid React synthetic event overhead on canvas |

---

## 7. Navigation Flow Map

```
App Launch
    └─→ Loading Screen
          └─→ Login / Register
                └─→ Character Select
                      ├─→ [+ New Slot] → Character Creation → Character Select
                      └─→ [Play] → Loading (zone assets) → Game World (HUD Active)
                                      ├─→ Inventory Panel (overlay)
                                      ├─→ Character Sheet (overlay)
                                      ├─→ Quest Journal (overlay)
                                      ├─→ World Map (overlay)
                                      ├─→ Social Panel (drawer)
                                      ├─→ [AH NPC] → Auction House (overlay)
                                      ├─→ [NPC] → Dialogue (bottom sheet)
                                      ├─→ Settings (overlay)
                                      └─→ [HP=0] → Death Screen → Respawn → Game World
```

---

## 8. MMO Considerations

| Concern | Design Decision |
|---|---|
| HP/MP bar updates | Zone server pushes player stat deltas via WebSocket; React HUD subscribes to a Zustand/Jotai store updated by the WS handler — no polling |
| Party member HP bars | Party member states sent by Zone Server in zone update packets; displayed in Social > Party tab and optionally as small frames bottom-left of screen |
| Chat volume | Chat is rendered in a separate scrollable React component; new messages appended to a ring buffer (last 200 messages); older messages discarded client-side |
| Minimap player dots | Zone server sends a compact player position list (x/y only, no names) at 500ms interval; minimap dots updated client-side |
| Auction House load | AH data fetched via REST API on panel open (not live WebSocket) — acceptable 200–500ms delay for a market UI |
| Inventory sync | Inventory state fetched from REST on login and updated optimistically on client; server confirms or rolls back |
| 300-player town shards | City of Aethermoor supports 300 concurrent players — minimap will show ≤ 300 dots; dots capped at 64 visible on minimap at any zoom (farthest dots not drawn) |

---

## 9. Technical Notes for CTO

| Topic | Specification |
|---|---|
| React + Phaser boundary | Phaser renders to `<canvas id="game-canvas">` inside a `<div id="phaser-container">` at `z-index: 1`; React HUD mounted at `z-index: 10` via Portal to `document.body` |
| Input passthrough | HUD container is `pointer-events: none`; interactive elements use `pointer-events: auto` inline. Phaser receives all canvas touches not consumed by React |
| State management | Recommend Zustand for HUD state (HP, MP, hotbar, quest tracker) — lightweight, no boilerplate, works well with Phaser's event system |
| Font loading | `PressStart2P` loaded via `@font-face` in CSS; preload link in `<head>` to prevent FOUT |
| Safe area CSS | `padding: env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left)` on root HUD container |
| Orientation change | Listen to `window.addEventListener('resize', ...)` and trigger Phaser `scale.refresh()` + React layout re-render |
| Colour palette | Provide as CSS custom properties (`--ui-bg-dark: #1A1020` etc.) on `:root`; React components reference via `var(--token)` |
| Hotbar cooldown | Cooldown overlays rendered as CSS conic-gradient or SVG arc animated by `requestAnimationFrame`; not React state updates per-frame |
| Virtual joystick | Recommend `nipplejs` library (MIT licence) integrated with Phaser's input system; or custom Phaser pointer handler if dependency reduction preferred |
| 9-patch panels | CSS `border-image` with a 24×24px sprite (8px corners, 1px edge centres); provide sprite source when art is ready |
| Minimap rendering | Pre-render a low-res (128×128px) grayscale tilemap image server-side per zone; serve as static asset; overlay SVG/canvas for player dots in React |

---

## 10. Open Questions

| # | Question | Owner | Priority |
|---|---|---|---|
| OQ-1 | What is the final tile size — 16×16 or 32×32px? This affects minimap resolution, slot icon sizes, and atlas layout. | CEO decision | High |
| OQ-2 | Should the game force landscape on mobile, or fully support portrait? Portrait significantly constrains hotbar and HUD space. | CEO decision | High |
| OQ-3 | Virtual joystick library: `nipplejs` (MIT) vs. custom Phaser implementation? CTO to advise on preference. | CTO | Medium |
| OQ-4 | Is `PressStart2P` approved as the primary UI font, or does the art direction require a commissioned pixel font? | CEO / Art direction | Medium |
| OQ-5 | Minimap generation: server-side pre-rendered images vs. client-side Phaser mini-scene? Server-side is simpler but requires pipeline; Phaser mini-scene is real-time but performance cost. | CTO | Medium |
| OQ-6 | Death screen mechanic: respawn in-place (soul cost) vs. nearest town? Affects what UI to show on death. | CEO design decision | Medium |
| OQ-7 | Chat: does the game require voice chat integration (WebRTC), or text-only for launch? | CEO | Low |
| OQ-8 | Auction House currency: should the UI support multiple currencies (gold + premium currency), or gold-only at launch? | CEO | Low |

---

## 11. Version History

| Version | Date | Author | Changes |
|---|---|---|---|
| v1.0 | 2026-04-14 | Game Designer | Initial draft — all 5 deliverable sections complete; HUD, 3 key screens (Game World, Inventory, Character Sheet), all secondary screens, style guide, mobile constraints, navigation flow, MMO considerations, technical notes, open questions |


