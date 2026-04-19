# Alpha Starter Quests — Project AETHERMOOR
**Document:** starter-quests.md
**Version:** 1.0
**Date:** 2026-04-14
**Author:** Game Designer
**Related:** [RPGAA-21 — NPC & Quest System](/RPGAA/issues/RPGAA-21) | [RPGAA-14 — Combat Spec](/RPGAA/issues/RPGAA-14)

---

## Overview

Five starter quests covering all three alpha zones (Millhaven, Whispering Forest, Sunken Crypt B1).
All quests are designed for players at levels 1–3. Together they form a coherent introductory arc:
the player arrives in Millhaven, is drawn into the mystery of the forest, and descends into the crypt.

---

## Quest 1 — "A Town in Need" (Kill Quest)
**Zone:** Millhaven (town)
**Level:** 1
**Type:** Kill
**Quest Giver:** Captain Aldric — Guard Captain, Millhaven town gate (tile 12, 8)

### Summary
Goblins from the Whispering Forest have been raiding Millhaven's outlying farms at night. Captain Aldric asks the player to drive them back.

### Objectives
1. Kill 6 Goblin Raiders in the Whispering Forest (northern edge, tiles 5–20)
2. Return to Captain Aldric

### Dialogue Hook (Aldric)
> "Traveller — you've arrived at a bad time. Goblins from the Whispering Forest have been raiding our farms at night. I have no men to spare, but you look capable. Clear them out and I'll make it worth your while."

### Rewards
- **250 XP**
- **30 gold**
- Item: **Millhaven Guard's Cloak** (light armour, +1 AC, flavour: "Smells faintly of woodsmoke and resolve.")
- **+100 Millhaven reputation**

### Branch
- If player attempts Persuasion DC 10 ("Are there more coming?"), Aldric reveals the goblins are being driven out of the deep forest by something worse — flagging the story hook for Quest 3.

---

## Quest 2 — "Missing Supplies" (Fetch Quest)
**Zone:** Millhaven → Whispering Forest
**Level:** 1
**Type:** Collect + Deliver
**Quest Giver:** Sera — Innkeeper, the Tipped Flagon Inn, Millhaven (tile 8, 14)

### Summary
A merchant caravan was ambushed on the road to Millhaven. Sera's winter supplies — smoked fish, wool blankets, and a cask of spiced mead — were stolen by goblin bandits who have set up a small camp in the western Whispering Forest.

### Objectives
1. Travel to the Goblin Camp (Whispering Forest, west — tile 4, 18)
2. Collect **Crate of Smoked Fish** (ground pickup, goblin camp)
3. Collect **Bundled Wool Blankets** (ground pickup, goblin camp)
4. Collect **Cask of Spiced Mead** (ground pickup, goblin camp — guarded by 1 Goblin Chief, Elite enemy)
5. Return all 3 items to Sera at the inn

### Dialogue Hook (Sera)
> "My winter stock is gone. Those goblins took everything. If you find the supplies, I'll give you a room, a hot meal, and more besides."

### Notes
- Items are quest-specific pickups; they do not appear in normal inventory. UI shows a "Quest Items" section in inventory.
- Goblin Chief (Elite): HP 35, AC 14, Attack +4, 1d8+2 slashing. Drops the Mead Cask as a guaranteed pickup.

### Rewards
- **300 XP**
- **25 gold**
- Item: **Traveller's Ration Pack** ×5 (consumable: restores 4 HP, flavour: "Sera's cooking. Better than it looks.")
- **+75 Millhaven reputation**
- Unlocks: Sera offers a 10% discount on inn rooms permanently

---

## Quest 3 — "The Watcher in the Trees" (Talk / Explore Quest)
**Zone:** Whispering Forest
**Level:** 2
**Type:** Explore + Talk
**Quest Giver:** Old Maren — Lorekeeper, Millhaven library (tile 15, 10)
**Prerequisite:** Complete Quest 1 (Aldric's Persuasion branch *or* Maren mentions it unprompted after Quest 1 completes)

### Summary
Old Maren has heard the player's report of goblins fleeing from the deep forest. She suspects something ancient has stirred in the Sunken Crypt beneath the forest floor — a site of old magic she has studied for decades. She asks the player to find the Watcher Stone, a carved monolith at the heart of the forest, and read the inscription.

### Objectives
1. Speak to Old Maren (opens quest)
2. Find the Watcher Stone (exploration — Whispering Forest centre, tile 18, 22)
   - The area is guarded by 2 Thorn Sprites
3. **Skill Check — History DC 12:** Read the inscription on the Watcher Stone
   - **Pass:** Decipher the full warning ("When the Rot stirs below, the roots above will flee. Seek the Sunken Crypt before the seal breaks.")
   - **Fail:** Partially decode it; must return to Maren who translates for you (adds dialogue step but still completes)
4. Return to Old Maren and report

### Dialogue Hook (Maren)
> *"The goblins don't flee from men. They flee from something that frightens even them. In my books, there is mention of a Watcher Stone — the old ones carved warnings there in a tongue nearly forgotten. Find it. Read it. Come back and tell me what it says."*

### Rewards
- **400 XP**
- **20 gold**
- Item: **Maren's Map Fragment** (quest item that reveals Sunken Crypt B1 on the world map)
- **+150 Millhaven reputation**
- Unlocks: Quest 4 (Sunken Crypt)

---

## Quest 4 — "Into the Dark" (Kill / Dungeon Quest)
**Zone:** Sunken Crypt B1
**Level:** 2–3
**Type:** Kill + Explore
**Quest Giver:** Captain Aldric (follow-up from Quest 1) — returns after Quest 3 completes
**Prerequisite:** Quest 3 complete (Maren's Map Fragment in inventory)

### Summary
With the crypt now revealed on the map, Aldric asks the player to descend into Sunken Crypt B1 and find the source of the disturbance. Rumours speak of a Rot Shaman raising the dead in the crypt's lower chamber. He does not yet know about the Rot Lord (that's the main story boss) — this quest plants the hook.

### Objectives
1. Enter Sunken Crypt B1 (zone transition — travel to crypt entrance tile)
2. Kill 4 Skeleton Archers (found in the crypt corridors, B1 level)
3. Find the Shaman's Altar (exploration — Sunken Crypt B1, chamber 3)
4. Destroy the Altar (interact — 3-second channel, interrupted by nearby enemies)
5. Escape the crypt (return to entrance tile — triggered by altar destruction spawning 3 Crawling Corpses)
6. Report back to Aldric

### Dialogue Hook (Aldric)
> *"If Maren is right and there's something raising the dead under our feet, I want it stopped. I can't send soldiers into a crypt — morale would break. But you've already proven yourself. Will you go?"*

### Notes
- The Shaman's Altar is a destructible object (not an enemy). Interact prompt appears when no enemies are within 5 tiles.
- Crawling Corpses spawned by the altar destruction are slow (speed 15 tiles/round) and deal 1d4 bludgeoning — designed to be avoidable, not a hard combat.
- This quest intentionally stops short of the Rot Lord boss fight (saved for main story progression).

### Rewards
- **600 XP**
- **60 gold**
- Item: **Crypt Guard's Signet Ring** (accessory, +1 CON modifier for saves, flavour: "Worn by the last man to stand watch here. He is no longer standing.")
- **+200 Millhaven reputation**
- Unlocks: Chapter 1 main story quest "The Rot Lord Falls" (RPGAA-2 story arc)

---

## Quest 5 — "Flowers for the Fallen" (Escort / Talk Quest)
**Zone:** Millhaven → Whispering Forest
**Level:** 1
**Type:** Escort + Talk
**Quest Giver:** Lila — Child NPC, Millhaven market square (tile 10, 12)

### Summary
Lila's father went into the Whispering Forest three days ago to gather heartbloom flowers for her mother's birthday. He hasn't come back. She asks the player to find him. He is safe — he twisted his ankle on a root and cannot walk — but the area around him has been scouted by Goblin Scouts. The player must escort him home.

### Objectives
1. Speak with Lila (opens quest)
2. Find Willem (Lila's father) in the Whispering Forest (tile 14, 9)
   - Area has 2 Goblin Scouts patrolling nearby
3. Escort Willem safely back to the Millhaven gate (tile 12, 2)
   - Willem moves at 20 tiles/round (injured); escort pace
   - If Willem reaches 0 HP: quest fails
4. Return Willem to Lila

### Dialogue Hook (Lila)
> *"Mister? My daddy went to get flowers but he's been gone since yesterday morning. Mama says not to worry but I can see she's been crying. Will you look for him? Please?"*

### Escort NPC — Willem
> HP: 20 | AC: 10 | Speed: 20 tiles/round (injured)
> Cannot fight. Follows player at 3-tile range.
> Has ambient dialogue while escorting ("Watch that root!" / "Almost there, I think..." / "Lila's going to scold me for this.")

### Rewards
- **200 XP**
- **15 gold**
- Item: **Bundle of Heartbloom Flowers** (cosmetic/quest item; Lila gives it to player as thanks — can be placed in housing later)
- **+50 Millhaven reputation**
- Unlocks: Willem becomes a named NPC in Millhaven market, sells basic gathering supplies

---

## Quest Summary Table

| # | Title | Zone | Type | Level | Quest Giver |
|---|---|---|---|---|---|
| 1 | A Town in Need | Whispering Forest | Kill | 1 | Captain Aldric |
| 2 | Missing Supplies | Whispering Forest | Fetch | 1 | Sera (Innkeeper) |
| 3 | The Watcher in the Trees | Whispering Forest | Explore/Talk | 2 | Old Maren |
| 4 | Into the Dark | Sunken Crypt B1 | Kill/Dungeon | 2–3 | Captain Aldric |
| 5 | Flowers for the Fallen | Whispering Forest | Escort | 1 | Lila (child NPC) |
