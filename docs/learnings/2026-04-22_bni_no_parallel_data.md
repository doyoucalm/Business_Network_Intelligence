# Learning — 2026-04-22: BNI Rule — No Parallel Data Entry

## What we got wrong

In the first draft of `15_BNI_MODULE_CATALOG_AND_ROADMAP.md`, Stage 6 was named **"Slip Submission"** with the description "members log referrals, TYFCB, CEU, testimonials directly (no more weekly PALMS batch)."

User flagged it: **"this is from VP upload excel from bni connect, never violates real BNI rules."**

## The rule

The HUB **never** accepts direct member entry of:
- Referrals given/received (RGI/RGR)
- TYFCB (Thank You For Closed Business)
- CEU (Continuing Education Units)
- Attendance (Present, Absent, Late, Medical, Substitute)
- Visitor counts

These metrics are governed by **BNI Connect**. The chapter VP downloads the official PALMS Excel from BNI Connect each week and uploads it to the HUB. The HUB's role is to **mirror and visualize** — never to be an alternate ledger.

## Why this matters

- **BNI compliance.** Members entering their own slips creates a parallel ledger that competes with BNI Connect's authority.
- **Audit risk.** When the HUB and BNI Connect disagree, which one is the truth? BNI says BNI Connect, always.
- **Member disputes.** "I logged 3 referrals in the HUB but BNI Connect shows 1" — these arguments have no productive resolution.
- **Region/Director relations.** The chapter's standing with BNI is measured against BNI Connect numbers. Anything else is internal-use only.

## What is OK vs not OK

| Activity | OK in HUB? | Why |
|---|---|---|
| Member views their own PALMS stats live | ✅ | Read-only mirror of VP's upload |
| Member updates presentation card / photo / contact | ✅ | Chapter-owned content, not PALMS metric |
| Member edits their slide content for next meeting | ✅ | Local content, not a stat |
| Book a 1-2-1 with another member | ✅ | Operational tool, not a PALMS metric |
| Mark a 1-2-1 as completed | ✅ | Local tracking; the slip itself goes through BNI Connect |
| Invite a visitor / track RSVP | ✅ | Pre-PALMS — happens before the visitor becomes a stats line |
| Member submits "I gave a referral" slip | ❌ | Belongs in BNI Connect |
| Member marks own attendance | ❌ | VP submits attendance to BNI Connect |
| Member logs own CEU | ❌ | BNI Connect tracks education |
| Member enters TYFCB amount | ❌ | BNI Connect handles closed business |

## How to apply going forward

1. **Naming check:** any module named "Slip Submission," "Self-Reporting," "Direct Entry," etc. for a PALMS metric is automatically rejected. Rename or redesign.
2. **Feature check:** before adding any "let members log X" feature, ask: "Is X tracked in BNI Connect?" If yes → STOP, this is read-only mirror territory.
3. **Architecture check:** PALMS data flow is one-way: BNI Connect → VP downloads Excel → VP uploads to HUB → HUB displays. Never reverse.
4. **Write rule:** rule saved as project memory `project_bni_hub.md` so future agents on this codebase load it on session start.

## Renamed module

Stage 6: ~~Slip Submission~~ → **Member Stats Mirror** (3 days). Per-member dashboard sourced from VP's PALMS upload. Read-only.

## Lesson

**Domain compliance ≠ technical capability.** Just because we *can* let members enter slips doesn't mean we *should*. BNI's rules predate the HUB by 40 years and define what's acceptable, not the engineering team. Always check the domain rule before designing the feature.
