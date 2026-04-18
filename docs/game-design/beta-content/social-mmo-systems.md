# Social & MMO Systems — Project AETHERMOOR

**Document:** social-mmo-systems.md
**Milestone:** Beta
**Version:** 1.0
**Date:** 2026-04-15
**Author:** Game Designer

---

## 1. Overview

Beta introduces the three foundational MMO social systems: **Party**, **Trade**, and **Chat**. These systems underpin all multiplayer interaction in AETHERMOOR and must be robust, low-friction, and designed for mobile-first input.

**Design intent:** Players should be able to group up, trade, and talk in under 3 taps on mobile. Social friction kills MMO communities. Every interaction in this spec prioritises discoverability and simplicity without sacrificing depth.

---

## 2. Design Goals

| Goal | Rule |
|---|---|
| Group up fast | Party invitation to in-group should be achievable in <10 seconds |
| Fair loot splitting | No loot disputes — system handles distribution transparently |
| Trust-based trade | No item scams — trade confirmation prevents fraud |
| Channel separation | Players in a dungeon should not be drowned in global chat noise |
| Mobile-first | All social UI must work on a 375px wide screen without overflow or hidden controls |

---

## 3. Party System

### 3.1 Overview

A **Party** is a temporary group of 1–4 players who share XP bonuses, loot eligibility, dungeon instances, and communication in the party channel.

### 3.2 Party Formation

**Invite flow:**

1. Player A taps on Player B's character (overworld) or name (player list / nearby panel)
2. Context menu appears: [Inspect] [Invite to Party] [Trade] [Whisper]
3. Player A selects "Invite to Party"
4. Player B receives a party invite notification (toast popup, 30-second timeout)
5. Player B accepts → both players are in a party
6. Party panel appears in HUD (left side, vertical stack, up to 4 member slots)

**Invite via name:** `/invite PlayerName` in chat also triggers the invite flow.

**Auto-decline after 30s:** If Player B does not respond, invite expires silently. No repeat notification.

### 3.3 Party Rules

| Rule | Detail |
|---|---|
| Max size | 4 players |
| Minimum size | 1 (solo "party" — no mechanical effect) |
| Party leader | First player in the party. Can be passed: [Leader] → [Pass Leadership] → select member |
| Dungeon instances | Party leader's instance is used — all members teleport to leader on dungeon entry |
| Zone instancing | Party members preferentially placed in the same zone instance (within cap) |
| Party disbanding | Auto-disbands if leader logs out for >5 minutes, or manually via [Leave Party] |
| Kick | Party leader can kick a member via the party panel → [Kick from Party] |

### 3.4 XP Splitting

XP is **not divided** — all party members receive full XP for kills, with a **party bonus**:

| Party Size | XP Bonus |
|---|---|
| 1 (solo) | +0% |
| 2 | +10% |
| 3 | +12% |
| 4 | +15% |

The party bonus is applied per-player. It does not require proximity — as long as players are in the same zone instance and in a party.

**Design note:** Shared full XP with a bonus rewards grouping without punishing players who fall behind or split briefly. This is intentional — punishing XP split creates resentment.

### 3.5 Loot Rules

Dungeons use **Round Robin loot distribution** by default. Overworld kills use **Free-for-All**.

#### Dungeon Loot (Round Robin)

- Each loot drop is assigned to one party member in rotating order
- The assigned player sees the loot window; other players see "[PlayerName] received [Item]"
- Assigned player may trade received loot to party members for 2 hours after pickup (trade-locked after that)
- Gold drops are **split equally** among all party members in the same room

#### Optional: Need/Greed Roll

Party leader can toggle **Need/Greed** mode on dungeon entry:

| Roll Type | Player eligibility | Outcome |
|---|---|---|
| **Need** | Player can use the item (class match) | Rolls 1–100; highest roll wins |
| **Greed** | Player cannot use but wants for selling | Rolls 1–100, but Greed rolls are always lower than Need rolls |
| **Pass** | Player declines | Item offered to next eligible player |

In case of tie, reroll automatically. Leader can also set **Loot Master** — all loot goes to leader who distributes manually (guild run use case).

#### Overworld Loot (Free-for-All)
- Each player picks up their own loot from enemies they tag (dealt damage to)
- Gold and common items: first to tap/interact picks up
- Rare+ items: one copy generated per player who contributed damage (>10% of monster's total HP dealt)

**CTO note:** Tagging threshold (10% damage) prevents trivial loot-sniping. Track damage contributions server-side per combat event.

### 3.6 Party HUD

- Shown on left side of screen, vertical stack
- Each member card shows: Name, Class icon, HP bar (colour-coded: green >60%, yellow 30–60%, red <30%), Mana bar
- Tap member card: quick-target that member (for Warden heals, Bard buffs)
- Party leader icon (crown) shown next to leader name
- Distance indicator: greyed out card if member is in a different zone

---

## 4. Trade System

### 4.1 Overview

**Player-to-player trade** allows two players to exchange items and gold directly and securely. All trades are confirmed by both parties before completion — no item scams possible by design.

### 4.2 Trade Initiation

**From overworld:**
1. Tap on target player → context menu → [Trade]
2. Target player receives trade request (toast, 30-second timeout)
3. Target accepts → Trade Window opens on both screens

**From chat:**
`/trade PlayerName` sends a trade request

**Range restriction:** Both players must be in the same zone instance. No cross-zone trading (use Auction House for that).

### 4.3 Trade Window

The trade window is a two-panel modal:

```
┌─────────────────────────────────────────────┐
│  TRADE — Iain ↔ Maeve                       │
├──────────────────┬──────────────────────────┤
│  YOUR OFFER      │  THEIR OFFER             │
│  [Item slot × 6] │  [Item slot × 6]         │
│  [Gold: ____]    │  [Gold: 0g]              │
│                  │                          │
│  [ Confirm ]     │  [Waiting...]            │
└──────────────────┴──────────────────────────┘
```

- Each player can offer up to **6 items** and any amount of gold
- Items are dragged from inventory into the offer panel (or tapped on mobile → "Add to Trade")
- Gold is entered via a numeric input field
- **Both players must press [Confirm]** before trade completes
- If either player modifies their offer after the other has confirmed, the confirmed state resets (no bait-and-switch)
- Trade completes only when **both** players have pressed [Confirm] on the same, unchanged offer state

### 4.4 Trade Rules

| Rule | Detail |
|---|---|
| Range | Same zone instance only |
| Item limit | 6 items per side |
| Gold limit | No cap (players can trade any amount of gold) |
| Quest items | Cannot be traded (flagged server-side as soulbound-equivalent) |
| Dungeon-exclusive items | Tradeable for 2 hours after pickup (see loot rules above) |
| Soulbound items | Cannot be traded once equipped (flagged on equip) — Bound on Pickup (BoP) items never tradeable |
| Tax | No gold tax on direct player trades (Auction House charges 5% — direct trade is untaxed to encourage grouping) |
| Cancellation | Either player can press [Cancel] at any time before both have confirmed |

### 4.5 Anti-Scam Protections

- **Offer lock:** If Player A confirms and Player B modifies their offer, Player A's confirm is automatically cleared and they see a "[Offer changed — please re-confirm]" notification
- **Visual confirmation:** Before confirming, both panels are locked and a summary shows: "You are trading: [list]. You receive: [list]. This cannot be undone."
- **Accidental close protection:** Closing the trade window prompts: "Cancel this trade? Your items will not be exchanged." — requires explicit confirmation to close

### 4.6 Auction House (Crossroads)

The Auction House is an asynchronous player market. Accessible only from the Auction House NPC in Crossroads.

| Feature | Detail |
|---|---|
| Listing | Player selects item from inventory → sets buyout price → lists for 24, 48, or 72 hours |
| Fee | 5% of sale price deducted at time of sale (non-refundable; listing is free) |
| Expiry | Unsold items are mailed back to player via the in-game Mailbox in Crossroads |
| Currency | Gold only (no item-for-item AH trades) |
| Browsing | Search by item name, type, level range, rarity; sort by price |
| Purchase | Tap item → [Buyout] → confirms gold deduction and instant item grant to buyer |
| Mobile browsing | Swipeable card list; tap to expand item details; [Buy] button prominent |

---

## 5. Chat System

### 5.1 Overview

AETHERMOOR uses a **channel-based chat system** with four core channels. Each channel has a distinct colour prefix in the chat window.

### 5.2 Chat Channels

| Channel | Prefix Colour | Range | Command | Description |
|---|---|---|---|---|
| **Global** | Yellow | Server-wide | `/g <message>` or tab to Global | All players on the server shard see this |
| **Zone** | White | Current zone instance | `/z <message>` or tab to Zone | All players in the same zone instance |
| **Party** | Blue | Party members | `/p <message>` or tab to Party | Party members only, any zone |
| **Whisper** | Purple | Single target | `/w PlayerName <message>` | Private direct message, any zone |

**Default tab:** Zone chat. Players arrive in Zone chat by default. Reduces Global noise for new players.

### 5.3 Chat Window — UI Spec

**Layout (mobile portrait):**

```
┌───────────────────────────────────────────┐
│ [Global] [Zone] [Party] [Whisper]         │  ← channel tabs
├───────────────────────────────────────────┤
│ [Zara]: Anyone doing Ashenveil today?     │
│ [You→Maeve]: I'll trade the Ember Crown   │
│ [Party][Iain]: Buff incoming              │
│ [Global][Renn]: WTS Emberveil Blade 5kG  │
│                                           │
│                                           │
├───────────────────────────────────────────┤
│ [Message input field            ] [Send]  │
└───────────────────────────────────────────┘
```

- Chat window is collapsible on mobile (tap the chat icon in HUD) — collapses to a small badge showing unread count
- Tapping a player's name in chat opens their context menu: [Whisper] [Inspect] [Invite to Party] [Trade]
- Chat bubbles: optionally, short messages appear as floating text above player characters in Zone chat (can be disabled in Settings → Accessibility)

### 5.4 Chat Rules

| Rule | Detail |
|---|---|
| Message rate limit | 3 messages per 5 seconds per player (anti-spam) |
| Message length | Max 200 characters per message |
| Global cooldown | 5-second cooldown on Global messages (prevents global spam) |
| Whisper privacy | Whispers are never visible to other players; logged server-side for moderation |
| Profanity filter | On by default; can be disabled in Settings → Content |
| Mute | Any player can `/mute PlayerName` — hides all messages from that player across all channels |
| Unmute | `/unmute PlayerName` |
| Block | `/block PlayerName` — hides messages AND prevents trade/party requests from that player |
| Report | `/report PlayerName <reason>` — logs to moderation queue |

### 5.5 Notifications & Unread Badges

| Event | Notification |
|---|---|
| Whisper received | Purple badge on chat icon; audio ping (if sounds enabled) |
| Party chat (if chat collapsed) | Blue badge on chat icon |
| Party invite | Toast notification, 30-second timer |
| Trade request | Toast notification, 30-second timer |
| Zone/Global (if chat collapsed) | No badge — volume channels do not interrupt gameplay |

### 5.6 Future Channels (Post-Beta)

- **Guild channel** `/guild` — guild members only
- **Faction channel** `/faction` — faction members only
- **Trade channel** — dedicated item trade spam channel (separate from Global to keep Global social)

---

## 6. MMO Considerations

| Consideration | Design Decision |
|---|---|
| Party invitation cross-zone | Party invites work across zones — player joins from any zone |
| Chat server architecture | Chat handled via WebSocket on a dedicated chat microservice; messages do not go through game server |
| Party loot server authority | All loot distribution is server-resolved; client receives only the result — no client-side loot decisions |
| Trade atomic transaction | Trade completion is a single atomic DB transaction; partial state (one player gets item, other doesn't) must be impossible |
| Auction House persistence | AH data in PostgreSQL; player's gold and item state updated atomically on purchase |
| Whisper storage | Whispers logged for 30 days for moderation purposes; not accessible to players post-send |
| Mute/block persistence | Mute and block lists stored server-side per account — persist across sessions and devices |

---

## 7. Technical Notes

- Party invite timeout (30s) managed server-side; client shows countdown
- Round Robin loot assignment tracked server-side per dungeon instance; persists across floor transitions within the instance
- Trade window state is server-authoritative; both clients see the same offer state synced from server — prevents desync-based scams
- Chat rate limiting enforced server-side (not just client-side)
- `/mute` and `/block` filters applied server-side at message delivery — not just client-side suppression
- Party HUD HP/mana values pushed from server every 500ms during active combat; every 2s when idle

---

## 8. Open Questions

| # | Question | Owner |
|---|---|---|
| 1 | Should Global chat have a level gate (e.g., must be Level 3+ to post in Global) to reduce new-account spam/bots? | CEO |
| 2 | Should the Auction House be accessible remotely (from any zone via a menu), or Crossroads-only? Recommend: Crossroads-only to drive hub traffic | CEO to confirm |
| 3 | Should trade have a gold tax to act as a soft gold sink? Current recommendation: no — Auction House fee covers this | CEO |
| 4 | Whisper history — should players be able to view past whisper conversations in a message inbox? Nice QoL for Beta or post-Beta? | CEO |

---

## 9. Version History

| Version | Date | Summary |
|---|---|---|
| 1.0 | 2026-04-15 | Initial Social & MMO Systems spec — party, trade, chat |
