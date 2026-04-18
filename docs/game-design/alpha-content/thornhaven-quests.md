# Thornhaven Village Starter Quest Pack — Project AETHERMOOR
**Document:** thornhaven-quests.md
**Version:** 1.0
**Date:** 2026-04-18
**Author:** Game Designer
**Issue:** [RPG-48](/RPG/issues/RPG-48)
**Related:** [RPGAA-21 — NPC & Quest System](/RPGAA/issues/RPGAA-21) | [RPGAA-29 — Alpha Content Design](/RPGAA/issues/RPGAA-29) | [RPGAA-31 — Tutorial & Onboarding](/RPGAA/issues/RPGAA-31)

---

## Overview

Five starter quests for Thornhaven Village — the true game-world entry point for all players graduating from the Ashfen Refuge tutorial. These quests are designed for characters at **Level 1–3**, introducing each core quest type (tutorial, combat, gathering, social, exploration) in a deliberate sequence that eases new players into the world while rewarding veteran players who want to move briskly.

Together they form a natural introductory arc: the player arrives in Thornhaven, earns the trust of its people, and uncovers the first whispers of a darkness stirring beneath the ancient forest to the east.

---

## Quest 1 — "The Missing Farmer"
**Type:** Tutorial (Fetch & Return)
**Zone:** Thornhaven Village → Thornhaven Fields
**Level:** 1
**Quest Giver:** Edra Hartwick — Innkeeper's wife, the Hearthstone Inn, Thornhaven (tile 9, 13)

### Summary
Edra's husband Oswin left before dawn to check the eastern field fences after a night of strange noises. He hasn't returned. He is safe — he found a collapsed fence section and lost track of time repairing it — but the fields border the treeline where goblin activity has been reported. Edra asks the player to check on him.

This quest is designed as the first interaction after Ashfen Refuge. It teaches NPC dialogue, zone traversal, and objective tracking without requiring combat.

### Briefing Dialogue (Edra)
> *"Excuse me — you look like you've just arrived. Forgive me for stopping a stranger, but I'm at my wit's end. My husband Oswin went to check the eastern fences before breakfast. That was three hours ago. Normally I wouldn't worry — he loses track of time out there — but the Brannick boy said he saw goblins near the treeline last night.*
>
> *He's probably fine. Probably. But if you're heading east anyway, would you look in on him? The field's just past the mill — you can't miss the broken wheel. I'd go myself but someone has to mind the inn."*

### Objectives
1. Travel to Thornhaven Fields — eastern section (follow the dirt track past the mill)
2. Find Oswin Hartwick at the collapsed fence (tile 28, 9)
   - Oswin is repairing the fence with his back to the treeline; ambient dialogue triggers on approach: *"Oh! You gave me a start. Edra send you? Bless her. Tell her I'll be home for supper — this last post just needs to be—"*
3. Return to Edra at the Hearthstone Inn and report

### Completion Dialogue (Edra)
> *"Oh, thank goodness. That man would forget his own boots if they weren't attached to his feet. Here — take this for your trouble. You've made a friend today, stranger. There aren't many of those to spare in a village this size."*

### Rewards
- **150 XP**
- **12 gold**
- Item: **Traveller's Bread** ×3 (consumable — restores 3 HP; flavour: *"Thick, slightly burnt on one side, and exactly what you needed."*)
- **+50 Thornhaven reputation**
- Unlocks: Edra offers 15% discount on Hearthstone Inn room rentals permanently

### Lore Note
*The Hartwick family has farmed Thornhaven's eastern fields for four generations. Oswin's great-grandmother was among the settlers who rebuilt the village on the bones of the old Aethermoor Empire road — the stone track the locals still call the Emperor's Path.*

---

## Quest 2 — "Goblin Skirmish"
**Type:** Combat (Kill)
**Zone:** Thornhaven Fields — southern road
**Level:** 1
**Quest Giver:** Sergeant Rynn — Village Militia, Thornhaven gatehouse (tile 4, 6)

### Summary
Three goblin scouts have been spotted lurking along the southern trade road, disrupting merchant traffic into Thornhaven. The militia is stretched thin guarding the village walls. Sergeant Rynn asks the player to clear them out before the evening merchant cart arrives.

This is the player's first intentional combat encounter in the main world — designed to be winnable at Level 1 solo, but challenging enough to feel meaningful.

### Briefing Dialogue (Rynn)
> *"Good timing. You're new, aren't you — just through from Ashfen? Then let me give you the lay of the land. We've three goblins camped in the scrub along the south road. Scouts, by the look of them — they're watching the merchants, waiting for a moment to rush someone. My people are on the wall and I can't spare them.*
>
> *I'm not asking you to pick a fight with an army. Three scouts. Drive them off or put them down — either works. The road needs to be clear before the Brannick cart comes through at dusk. Can I count on you?"*

### Objectives
1. Travel to the southern road (Thornhaven Fields — south, tiles 8–22)
2. Defeat 3 Goblin Scouts
   - Goblin Scouts patrol in pairs then split; one is perched in a tree (ranged Shortbow attacker)
   - Stats: HP 12, AC 13, Attack +3, 1d6 piercing (shortbow) or 1d4+1 slashing (dagger)
3. Return to Sergeant Rynn at the gatehouse

### Completion Dialogue (Rynn)
> *"Three scouts dealt with. Good. You've got a calm head in a fight — I can tell by the way you came back breathing. Thornhaven looks after people who look after Thornhaven. Remember that."*

### Rewards
- **250 XP**
- **25 gold**
- Item: **Militia Shortcoat** (light armour — +1 AC; flavour: *"Stamped with the Thornhaven militia mark. It smells of oil and honest work."*)
- **+75 Thornhaven reputation**

### Lore Note
*Goblins have raided Thornhaven's trade road intermittently for decades. In recent months the raids have grown bolder and more frequent — as if something in the deep forest is pushing them toward the village margins. Sergeant Rynn doesn't say this aloud. She doesn't want to frighten anyone.*

---

## Quest 3 — "Herb Gatherer"
**Type:** Gathering (Collect & Deliver)
**Zone:** Thornhaven → Thornwood Edge (forest fringe)
**Level:** 1
**Quest Giver:** Petra Vane — Village Herbalist, the Apothecary Stall, Thornhaven market (tile 11, 10)

### Summary
Petra is low on Moonpetal herbs — the core ingredient in her healing salves, which the militia depends on. Moonpetals grow only in shaded clearings at the forest's edge and must be picked fresh. She cannot leave the stall while patients need her. She asks the player to collect five blooms and return before nightfall.

This quest introduces gathering mechanics and zone resource nodes. The forest fringe has mild enemy presence (Thorn Sprites — non-aggressive unless the player disturbs the old stones) to create ambient tension without forcing combat.

### Briefing Dialogue (Petra)
> *"Oh, perfect timing. Are you the sort of person who doesn't mind getting their hands a little muddy? I need Moonpetal herbs from the forest edge — five blooms, no more, no fewer. They only grow where the old roots break the surface in the shade.*
>
> *They're easy to spot; pale silver-white petals, smell faintly of rain. Stay on the cleared paths and you won't have any trouble. I'd go myself, but I've three patients and a militia runner who needs his dressings changed.*
>
> *Bring them back intact and I'll make it worth your while — and you'll have the militia's gratitude, which counts for something around here."*

### Objectives
1. Travel to the Thornwood Edge — forest fringe (north-east of Thornhaven, tiles 30–45)
2. Collect 5 Moonpetal Herbs (glowing resource nodes — pale silver, found in shaded clearings)
   - Node spawn density: 8 nodes per instance, each yields 1–2 herbs; nodes respawn every 5 minutes
   - Disturbing the three ancient stones in the area aggros 2 Thorn Sprites (non-mandatory combat)
3. Return all 5 Moonpetal Herbs to Petra at the market stall

### Completion Dialogue (Petra)
> *"Five blooms, all intact. You picked them cleanly — most people crush the stems. You've done this before, or you pay attention to the world. Either way, take this. And thank you — truly."*

### Notes
- Herb nodes are highlighted on-screen for first-time gatherers by a tutorial tooltip: *"Tap glowing plants to harvest. Some rare herbs only grow in specific zones or at certain times of day."*
- If the player gathers more than 5, only 5 are consumed by the quest; extras remain in inventory as a crafting ingredient.

### Rewards
- **200 XP**
- **18 gold**
- Item: **Healer's Pouch** (consumable ×4 — restores 6 HP per use; flavour: *"Petra's own blend. Better than anything you'd buy on the road."*)
- **+60 Thornhaven reputation**
- Unlocks: Petra's apothecary stall gains a 'restocked' inventory including basic healing salves and antitoxins

### Lore Note
*Moonpetals grow where the soil is thin over old Aethermoor stonework. Herbalists say the flowers absorb something from the ancient foundations — a trace of the old empire's knowledge. Scholars say that is wishful thinking. Both are probably right.*

---

## Quest 4 — "The Blacksmith Debt"
**Type:** Social (Dialogue / Dispute Resolution)
**Zone:** Thornhaven Village
**Level:** 2
**Quest Giver:** Aldous Crenn — Blacksmith, Thornhaven Forge (tile 17, 8)

### Summary
Aldous borrowed twenty gold from Mira Solten, the village merchant, to buy iron stock when trade prices were low. He repaid fifteen of it, then business dried up. Now Mira has locked his account at the general store and is refusing to sell him fuel coal — which means the forge goes cold and no one in Thornhaven gets repairs. The player must speak to both parties and broker a resolution.

This quest introduces the skill-check dialogue system with three viable paths (Persuasion, Deception, Intimidation), each with a different outcome and flavour. It also rewards players who observe both sides before committing.

### Briefing Dialogue (Aldous)
> *"You look like someone who can see reason. Come closer — I don't want the whole square to hear this. Mira Solten has cut off my coal supply. Five gold. That's what I still owe her. Five gold, and she'll let the whole village freeze rather than wait a fortnight.*
>
> *I've fixed blades for half the militia, made door hinges for the inn for free, and this is my thanks. I'm not a deadbeat — I'm a man who had a slow winter. If someone could make her see that, I'd owe them more than five gold.*
>
> *Talk to her? She's at the store on the square. I'd go myself but last time we spoke it nearly came to blows."*

### Objectives

**Step 1 — Speak to Mira Solten** (General Store, tile 10, 8)
Mira's side: Aldous has owed her for three months and keeps making excuses. She's a small trader who can't float debt indefinitely.

*Mira's dialogue:*
> *"Aldous. Yes. He's a good smith and a bad debtor, and those are not in balance. Five gold isn't a fortune, but I lent it in good faith and 'I'll have it soon' doesn't pay my suppliers. He's had three months. I've been patient.*
>
> *If someone can guarantee me the five gold within the week — or give me a reason to believe it — I'll reopen his account. But I'm not doing it on a promise."*

**Step 2 — Resolve the dispute via one of three paths:**

| Path | Skill Check | DC | Outcome |
|---|---|---|---|
| **Persuasion** | CHA check | DC 11 | Mira agrees to a one-week extension; relationship preserved; both NPCs gain positive disposition |
| **Deception** | CHA check | DC 13 | Player claims to have witnessed Aldous complete a paid commission. Mira grants the extension on false grounds (Aldous never knows; if player fails this check, Mira becomes hostile to player for 24 hrs in-game) |
| **Pay the Debt** | No check (costs 5g) | — | Player pays Mira directly. She reopens the account immediately. Aldous is deeply grateful; Mira neutral-good outcome |

**Bonus path — Insight (WIS DC 10, available before any resolution attempt):**
If the player passes Insight before approaching Mira, they notice she's been avoiding eye contact with Aldous specifically — the debt dispute is partly personal (old argument pre-dating the loan). This reveals an optional dialogue line that bypasses one DC tier on Persuasion (DC drops to 8).

**Step 3 — Return to Aldous and report the outcome**

### Completion Dialogue (Aldous)

*Persuasion/Insight path:*
> *"She agreed? She actually — hah. I owe you a pint at the Hearthstone and a blade sharpened for free, whenever you need it. Thank you. Genuinely."*

*Deception path:*
> *"I don't know what you told her, but it worked. I won't ask questions. Here — for your trouble. And I'll get that debt paid by week's end, I swear it."*

*Pay the Debt path:*
> *"You paid her yourself? I — that's — I don't know what to say. I'll pay you back. I mean that. Here's what I have now; the rest when the next order comes in."* *(Aldous repays the player 3g over the next two in-game days via auto-deposit to their wallet.)*

### Rewards
- **350 XP**
- **30 gold** (or 25g if player spent 5g on the direct-pay path, partially offset by Aldous's repayment)
- Item: **Crenn-Made Dagger** (common weapon — 1d4+2 piercing; flavour: *"The steel is clean, the balance is excellent, and the maker is proud of it."*)
- **+100 Thornhaven reputation**
- Unlocks: Aldous becomes a named merchant with discounted repair costs for the player (10% off all repairs)

### Lore Note
*Thornhaven's economy runs on debt and trust in roughly equal measure. The village has no bank — the nearest one is in the City of Aethermoor, three days' travel east. People here keep their word or lose their neighbours, and losing your neighbours in a place this size is a kind of death.*

---

## Quest 5 — "Ancient Ruins"
**Type:** Exploration (Discover & Report)
**Zone:** Thornhaven Fields → Ashroot Tower (ruined structure)
**Level:** 2–3
**Quest Giver:** Scholar Finn Darell — Travelling Academic, Hearthstone Inn common room (tile 9, 15)

### Summary
Finn is a junior scholar from the City of Aethermoor, cataloguing ruins of the old Aethermoor Empire for the Lorekeeper's Archive. He has found references in old manuscripts to a watch-tower called Ashroot Tower — built by the empire to monitor the forest for incursions — said to lie a few hours east of Thornhaven. He cannot make the journey himself (he took a fall from his horse) and asks the player to scout the tower, find its inscription stone, and report back on the structure's condition.

This quest introduces overworld exploration and environmental lore. The tower is ruined but structurally interesting, with a readable inscription that connects to AETHERMOOR's backstory.

### Briefing Dialogue (Finn)
> *"Ah — excuse me. You look like you've been out in the field today. May I ask — have you travelled the eastern road past the mill? Yes? Then you may have passed within sight of it without knowing: Ashroot Tower.*
>
> *It's a watch-tower from the Aethermoor Empire — four hundred years old at least, probably more. I have records suggesting it was manned until the Cataclysm and then simply... abandoned. I'd go myself, but I landed badly when my horse shied at something on the road — something in the treeline.*
>
> *I need someone to reach the tower, find the cornerstone inscription, and sketch or transcribe what it says. And anything else of note — structural condition, what's growing in the ruins, whether anything is living there now. My notes are incomplete and the Archive won't fund a second expedition if I can't deliver a proper report."*

### Objectives
1. Travel east from Thornhaven and locate Ashroot Tower (ruined tower — east of Thornhaven Fields, tile 48, 14)
   - The approach path is overgrown; the tower is visible once the player enters the eastern field zone
   - 2 Goblin Scouts are camped at the tower base (non-mandatory: can be fought or avoided by circling the east wall)
2. Examine the base of the tower — find the Cornerstone Inscription (interactable object — tile 50, 16)
   - **Skill Check — History (INT) DC 10:**
     - **Pass:** Player reads the full inscription (see below) and transcribes it accurately in their Quest Log
     - **Fail:** Player can partially read it but must bring a rubbing to Finn for translation (adds one dialogue step; still completes the quest)
3. Explore Ashroot Tower — discover 2 of the following 3 optional points of interest (to complete "survey" objective):
   - The Collapsed Staircase (tile 50, 12) — climbable to the second level with a view of the forest canopy
   - The Old Fire Pit (tile 49, 17) — signs of recent use (warm ash; someone has been here within the last day)
   - The Empire Tile (tile 51, 16) — a floor tile stamped with the Aethermoor Empire crest (Lore entry unlocked: *"The Crest of the Ae'Moran"*)
4. Return to Finn at the Hearthstone Inn and deliver your report

### Cornerstone Inscription (as read on History pass)
> *"Built in the forty-third year of the Ae'Moran Compact, by order of the Warden of the Eastern Reaches. Let this tower stand as our eyes upon the forest. Let what stirs beneath the roots find no purchase while soldiers still watch from above.*
>
> *The Cataclysm has silenced the Compact. May whoever reads these words keep watching."*

### Completion Dialogue (Finn)

*History pass (full transcription):*
> *"'May whoever reads these words keep watching.' By the Archive, that's extraordinary. The forty-third year of the Compact puts this tower at least four centuries old — and the Warden of the Eastern Reaches was never documented to have built anything this far out. This changes my entire chapter. Thank you. Here — my expedition fund is modest, but this is worth every coin."*

*History fail (partial + rubbing):*
> *"Let me see... yes, that's the Ae'Moran seal in the stamp pattern. The rest I can fill in from context. This is still enormously useful — don't think it isn't. You found it. That's the hard part."*

### Notes
- The warm ash in the old fire pit foreshadows a future content hook (someone or something is using the tower as shelter — the identity is left unresolved in this quest, seeding a later story beat).
- The collapsed staircase climb is purely cosmetic — from the second level, the player can see a distant light in the deep forest, visible only at dusk (time-gated ambient detail, not a mechanic).

### Rewards
- **500 XP**
- **40 gold**
- Item: **Finn's Field Notes** (quest item, converted post-quest to cosmetic: *"Densely annotated sketches. On the last page, Finn has written your name next to the entry for Ashroot Tower."*)
- Item: **Surveyor's Compass** (tool item — reveals undiscovered zone entrances within 3 tiles on the minimap; flavour: *"The needle always points toward something worth finding."*)
- **+150 Thornhaven reputation**
- Unlocks: Finn returns to the City of Aethermoor and sends the player a follow-up letter (in-game mail) opening a later optional questline in the Aethermoor Lorekeeper's Archive

### Lore Note
*Ashroot Tower was one of seventeen watch-posts the Aethermoor Empire erected along the forest borders during the Warden Period. Thirteen of the seventeen collapsed within a generation of the Cataclysm. The other four are still standing — which means someone, or something, has been maintaining them.*

---

## Quest Summary Table

| # | Title | Zone | Type | Level | Quest Giver | Rewards (XP / Gold) |
|---|---|---|---|---|---|---|
| 1 | The Missing Farmer | Thornhaven Fields | Tutorial / Fetch | 1 | Edra Hartwick (Innkeeper's wife) | 150 XP / 12g |
| 2 | Goblin Skirmish | Thornhaven Fields — South Road | Combat / Kill | 1 | Sergeant Rynn (Militia) | 250 XP / 25g |
| 3 | Herb Gatherer | Thornwood Edge | Gathering | 1 | Petra Vane (Herbalist) | 200 XP / 18g |
| 4 | The Blacksmith Debt | Thornhaven Village | Social / Dialogue | 2 | Aldous Crenn (Blacksmith) | 350 XP / 30g |
| 5 | Ancient Ruins | Ashroot Tower (east fields) | Exploration | 2–3 | Scholar Finn Darell | 500 XP / 40g |

---

## Narrative Arc Notes

These five quests are designed to function independently but reward players who complete them in sequence. The through-line is **Thornhaven as a community under quiet pressure**: goblins on the road, a forge at risk, a scholar too injured to leave the inn, a farmer's wife who has lived too many mornings of worry. The player does not yet know about the Rot or what is driving the goblins from the deep forest — but Quest 5's warm ash and Quest 2's sergeant who doesn't say the frightening things aloud both plant that seed.

The Ashroot Tower inscription (*"May whoever reads these words keep watching"*) is intentional. By the time the player first arrives in Thornhaven, someone has already started watching again.
