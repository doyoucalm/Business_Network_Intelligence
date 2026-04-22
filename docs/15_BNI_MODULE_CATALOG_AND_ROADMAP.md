# 15 — BNI HUB Module Catalog & Roadmap

> Created: 2026-04-22
> Companion to: `13_WM_PRESENTER_SPEC.md`, `14_HANDOFF_2026-04-22.md`, `learnings/2026-04-22_member_lifecycle.md`

## Member lifecycle — current state

**NOT handled.** Roster import only ever sets `membership_status = "active"`; nothing writes `exited`, no audit trail, no cascade. New members get added blindly with no induction tracking. Full gap analysis in `learnings/2026-04-22_member_lifecycle.md`. The fix becomes its own module (Stage 4).

## When can we run a real meeting on this web?

- **Best case: Wednesday 29 April 2026** (1 week). Block D today, Stage 3 starts Apr 23, Day 5 dry run Apr 27, live Apr 29.
- **Realistic case: Wednesday 6 May 2026** (2 weeks). Day 1 always slips. Iframe sandbox + PPTX async are 1.5-day items each. Padding for Canva tests, attendance integration, projector rendering bugs.
- **Recommended:** target Apr 29 as dry run *with old PPTX as backup*, go fully live May 6.

## BNI module catalog — what we can add

### Member-growth pipeline
- **Visitor Hosting** — invite forms, RSVP, follow-up CRM, conversion funnel
- **Membership Committee** — application intake, vetting checklist, classification conflict check, decision log
- **Member Lifecycle** — joined/exited/induction stages, mentor assignment, onboarding wizard, exit cascade
- **MSP (Member Success Program)** — 12-week new-member curriculum, completion tracking
- **Renewal Manager** — membership expiry alerts, dues invoicing, non-renewal flow

### Networking mechanics (BNI's core engine)
- **Member Stats Mirror** — surfaces each member's PALMS data (referrals, TYFCB, CEU, attendance) in their own dashboard. **Source of truth: PALMS Excel uploaded by VP from BNI Connect — never direct member entry.** See "BNI Rule" note below.
- **1-2-1 Booking** — calendar matching, agenda templates, completion logging
- **GAINS Sheet** — Goals/Accomplishments/Interests/Networks/Skills profile, surfaced in 1-2-1s
- **Power Team Detector** — auto-cluster related professions, suggest team formation
- **Substitute Manager** — request substitute, match available, attendance credit logic

### Recognition + reporting
- **Notable Networker / Founders Circle** — milestone progression, awards
- **President/VP Dashboard** — chapter health KPIs, churn risk, retention curves, top performers
- **Chapter Performance Reports** — monthly/quarterly auto-generated PDFs for region

### Education + content
- **Education Library** — Ed Moment slide bank, indexed by topic, reusable across weeks
- **Feature Presentation Manager** — FP rotation calendar, slot booking, slide template library
- **Training Schedule** — chapter trainings, regional events, RSVP

### Integrations
- **BNI Connect Sync** — two-way (currently one-way XML import only)
- **Telegram Bot** — nudges, weekly digest, slip submission shortcuts
- **Public Chapter Site** — visitor-facing landing, member directory opt-in, RSVP form
- **AI Copilot** — DeepSeek-backed chat over chapter data

### Governance
- **Code of Ethics tracking** — violation log, vetting committee workflow
- **Director Consultant Visit Log** — DC visits, action items, follow-up
- **Inter-chapter Visit Tracker** — visiting other chapters, hosting visiting members

## Build order — what next

| Stage | Module | Why now | Estimate |
|---|---|---|---|
| 3 | **WM Presenter** | Replaces 306 MB PPTX, weekly pain | 5 days |
| 4 | **Member Lifecycle** | Fixes today's gap, unblocks every other module | 3 days |
| 5 | **Visitor Hosting** | Feeds Member Lifecycle (visitors → applicants → members), highest LT pain | 5 days |
| 6 | **Member Stats Mirror** | Per-member dashboard sourced from VP's PALMS upload (never direct entry — BNI rule) | 3 days |
| 7 | **President/VP Dashboard** | Ties it together once underlying data exists | 2 days |

After Stage 7, modules become parallelizable — Education, FP Manager, Membership Committee, Telegram bot in any order based on chapter pain.

---

## BNI Rule — No Parallel Data Entry

**The HUB never accepts direct member entry of referrals, TYFCB, CEU, attendance, or visitor counts.**

These metrics are governed by BNI Connect and PALMS. The VP downloads the official PALMS Excel from BNI Connect each week and uploads it to the HUB. The HUB is a **mirror and visualization layer**, never an alternate ledger.

**Why:** BNI compliance. Parallel ledgers create disputes, audit risk, and undermine BNI Connect's role. Members entering their own slips would split the source of truth.

**How to apply:**
- Members can VIEW their stats in real-time once VP uploads the latest PALMS.
- Members can UPDATE their presentation card, contact info, profile, photo, embed links — anything the chapter owns locally.
- Members CANNOT submit referral slips, mark their own attendance, log their own CEUs, or enter visitor counts.
- 1-2-1 booking and completion is OK to track locally — it's not a PALMS metric, it's a chapter operational tool.
- Visitor invites/RSVP is OK to track locally — it's pre-PALMS, before the visitor becomes a stats line.

**Never violate this. Future modules must read this rule before adding any "let members log X" feature.**

