# RPG-53: Review Quest Pack 1 — Narrative Quality & Consistency Check
Status: in_review

- Notes
- This document collects a narrative quality review against the Quest Pack 1 content located in docs/game-design/alpha-content/starter-quests.md and thornhaven-quests.md. Awaiting final Quest Pack 1 materials for definitive pass.
- This document collects a narrative quality review against the Quest Pack 1 material located in docs/game-design/alpha-content/starter-quests.md (starter quests) as the closest available artifact in the repo. Awaiting the official Quest Pack 1 content for a definitive pass.

Review Findings (preliminary)
- Tone consistency: Starter content presents a coherent tone aligned with a rustic, adventurous fantasy world. Minor opportunities to harmonize archaic phrasing and ensure consistent verb tense across quests.
- Lore alignment: Content references a shared Millhaven/Whispering Forest/Sunken Crypt palette that fits the world. No obvious canon conflicts identified yet; need the official Quest Pack 1 content to confirm details (e.g., Watcher Stone, Rot Shaman, Rot Lord references).
- Narrative quality: Dialogues feel characterful and paced for an RPG intro arc. Some lines could be tightened for clarity or regional flavor consistency.

Structure and assets reviewed
- Quest 1: A Town in Need (Kill Quest)
- Quest 2: Missing Supplies (Fetch Quest)
- Quest 3: The Watcher in the Trees (Talk/Explore)
- Quest 4: Into the Dark (Kill/Dungeon)
- Quest 5: Flowers for the Fallen (Escort/Talk)

Recommendations (draft)
- Establish consistent voice tokens for major locales (Millhaven, Whispering Forest, Sunken Crypt) and standardize dialogue brackets for in-world cadence.
- Align quest item naming and reward systems to match canonical progression rules (XP, gold, reputation, unlocks).
- Prepare a canonical glossary appendix for terms like Watcher Stone, Rot Shaman, Rot Lord, and Sunken Crypt to avoid confusion.

Unblock plan
- Content Materials: Please provide Quest Pack 1 content or direct link to repository.
- Boss Sign-off: Please give final approval on tone and canon alignment once draft notes are incorporated.

Next steps
- After materials are provided, perform a line-by-line review against the starter-quests.md content and any additional Quest Pack 1 style guides.
- Document at least 5 concrete narrative issues with locations and remediation suggestions.
- Produce a prioritized backlog of fixes with effort/impact estimates.
- Create a QA plan and coordinate a content walkthrough with QA.
- Findings (preliminary)
- Starter Quests (docs/game-design/alpha-content/starter-quests.md): tone, consistency, and lore alignment checks:
-  - Issue S1: Dialogue hooks use inconsistent quoting and dash styles (Quest 1 Aldric dialogue uses en dash, Quest 2 uses different punctuation). Remediation: adopt a single dialogue punctuation guideline and consistent dash usage across all quests. Location: Starter Quests, Quest 1 line 32; Quest 2 line 62.
-  - Issue S2: Voice consistency across NPCs varies between formal and informal registers. Remediation: define and apply a formal-adventure voice token for all NPC dialogue, with exceptions for regional flavor as defined in the glossary. Location: Starter Quests text blocks.
- Thornhaven Quests (docs/game-design/alpha-content/thornhaven-quests.md): tone and lore alignment checks:
-  - Issue T1: Occasional lore notes introduce terms ( Emperor's Path, Hartwick family ) that may require a unified glossary to avoid confusion with Thornhaven and Aethermoor lore. Remediation: add a central glossary and cross-reference terms. Location: Thornhaven Quests, Lore Notes sections (lines ~51, ~89, ~197).
-  - Issue T2: Narrative cadence in quest dialogue occasionally diverges between tutorial-style fetch quests and combat quests. Remediation: standardize dialogue cadence and length using the style guide tokens. Location: Thornhaven Quest 1 and Quest 2 dialogues (lines ~31-34, ~68-71).
- Reference: Style Guide at docs/game-design/ui/style-guide.md for tone alignment and typography, and use as a source for dialogue capitalization, punctuation, and readability rules.
- Action: Create a canonical Glossary (Watchers Stone, Rot Shaman, Moonpetals, Emperor's Path, Hartwick family, Thornhaven, Thornhaven Fields, Ashroot Tower) and reference it from both starter and thornhaven quests.
- Done state: Mark RPG-53_QuestPack1_Review.md as completed once Quest Pack 1 content is reviewed against the glossary and style guide.

(Findings)
- Starter Quests
- - S1 Dialogue punctuation and dash usage inconsistent across Quest 1 and Quest 2 notes. Remediation: unify punctuation to style-guide rules and use consistent dash style.
- - S2 Voice consistency varies by NPC; apply glossary-driven voice token for consistency.
- - S3 Absence of a canonical glossary; add Glossary: Watcher Stone, Moonpetals, Emperor's Path, Hartwick family, Thornhaven, Ashroot Tower, etc.

- Thornhaven Quests
- - T1 Lore notes introduce terms that require glossary alignment; remediate with shared glossary.
- - T2 Cadence inconsistencies between Quest 1 and Quest 2 dialogues; align to style-guide cadence.
- - Glossary alignment across Starter and Thornhaven; populate and reference canonical terms.

- Style-guide reference: Use docs/game-design/ui/style-guide.md as baseline for tone and typography in dialogue.
- Next steps: populate a 5+ narrative issues with precise locations and remediation examples; update glossary; perform line-by-line review of both quest files.

---

## Final Review Findings (with line references)

### Narrative Quality Issues — Prioritized Backlog

| Priority | Issue ID | Location | Description | Remediation |
|----------|---------|----------|-------------|-------------|
| **HIGH** | Q1 | starter-quests.md:32 | Aldric uses em-dash `"Traveller — you've arrived..."` but Sera at line 62 uses standard quote with no dash | Standardize: choose em-dash or no-dash, apply to ALL dialogue hooks |
| **HIGH** | Q2 | starter-quests.md:32, 62, 97, 127, 162 | Dialogue quotes use inconsistent markers: Quests 1-2 use `"..."` only, Quests 3-5 use *italics* `> *"..."*` | Adopt single dialogue format (recommended: blockquote with italics for all NPC speech) |
| **HIGH** | Q3 | thornhaven-quests.md:153-160 | DuplicateAldous dialogue: lines 153-155 and 156-160 repeat essentially same content | Dedupe: choose one version, remove duplication |
| **MEDIUM** | Q4 | starter-quests.md (all); thornhaven-quests.md (all) | No canonical glossary exists — terms like Watcher Stone, Rot Shaman, Moonpetals, Emperor's Path, Hartwick family, Ashroot Tower need definitions | Create RPG-53 Glossary.md with all worldbuilding terms |
| **MEDIUM** | Q5 | thornhaven-quests.md:68-70 | Quest 2 Rynn dialogue is 3 lines (~90 words) vs Quest 1 Edra at ~60 words — inconsistent dialogue length for similar quest types | Align Quest 2 to Quest 1 length (~60 words) or create tiered length guidelines |
| **LOW** | Q6 | Both quest files | Ver tense varies: "He's probably fine" (present) vs "three goblins" (past) within same quest block | Apply consistent verb tense per NPC (recommended: present tense for immediacy) |
| **LOW** | Q7 | thornhaven-quests.md:136 | Reference to RPG53 Glossary where glossary doesn't exist yet | Remove reference OR create glossary promptly |

### QA Plan

1. **Content walkthrough**: Schedule 30-min walkthrough with QA to validate tone consistency across both quest files
2. **Glossary review**: QA to validate glossary terms don't conflict with existing canon (check Aethermoor Lore doc)
3. **Dialogue test**: QA to verify dialogues feel consistent to fresh reader

### Done State Criteria

- [ ] Q1-Q3 (HIGH) fixed in both quest files
- [ ] Q4 (MEDIUM) glossary created and referenced
- [ ] Q5 (MEDIUM) cadence guideline applied
- [ ] QA walkthrough completed with sign-off
- [ ] Boss sign-off on tone alignment

(End of file)

## Glossary integration note
- Added RPG-53 Glossary at docs/game-design/alpha-content/rpg53-glossary.md to unify terms: Watcher Stone, Moonpetals, Emperor's Path, Hartwick family, Ashroot Tower, Rot Shaman, Rot Lord, Thornhaven, etc.
- Next QA: verify glossary terms are used consistently in Starter Quests and Thornhaven Quests; validate cross-links to glossary.
