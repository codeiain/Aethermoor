## RPG-66: CEO Brief (Draft)

Context
- Project: Aethermoor (2D MMO: Zelda-like + D&D)
- Role: OSS license audit, IP/licensing risk flagging, draft-ready legal docs
- Deadline: RPG-66 deliverables (EULA, ToS, Privacy) plus OSS license inventory and notices

Current Status
- Draft EULA, ToS, Privacy have been drafted and committed. OSS inventory template created; OSS notices scaffolded.
- Direct dependency stack identified in repo; a full license inventory is pending (including transitive licenses).

OSS Licensing (Direct Dependencies)
- Observed permissive licenses among direct dependencies (typical MIT/BSD-3-Clause/Apache-2.0/BSD-2-Clause).
- Potential risk centers on transitive licenses; copyleft obligations (GPL/MPL-type) could require source disclosure or other restrictions if present in transitive graph.
- Action: complete a comprehensive license inventory for all direct and transitive dependencies to confirm risk posture and attribution obligations.

IP/Docs Risk (Draft)
- EULA/ToS/Privacy drafted with self-hosted model; no cloud/data processing commitments beyond stated policy.
- OSS notices are to be surfaced via an OSS Notices section and a NOTICE file as required by licenses.
- Action: populate OSS notices in packaging and ensure notices are accessible to users.

Escalation Criteria
- High or Critical OSS license conflicts (copyleft risk, licensing incompatibility)
- IP infringement concerns or any material gap in the Terms or Privacy
- Any decision outside scope of OSS-only self-hosted deployment

Next Actions (Owner: Lawyer)
- Complete full OSS License Inventory (frontend and all backend services; include transitive licenses).
- Produce a CEO-ready risk brief summarizing licenses, risks, and recommended mitigations.
- Finalize the three legal documents (EULA, ToS, Privacy) with internal consistency and cross-references to OSS notices.
- Prepare a single-page RPG-66 briefing deck for CEO review.

Notes
- All licenses cited in the final brief should be named explicitly (e.g., MIT, BSD-3-Clause, Apache-2.0, MPL-2.0, GPL-3.0) with obligations and attribution requirements.
- Data handling in Privacy policy should align with self-hosted deployment and GDPR/CCPA considerations as applicable.
