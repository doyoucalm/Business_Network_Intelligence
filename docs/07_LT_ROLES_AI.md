# 07 — Leadership Team Roles & AI Assistant Specifications

## Role Map

| Role | Code | Committee | Current Holder | Phase |
|------|------|-----------|---------------|-------|
| President | P | Executive | TBD | Phase 4 |
| Vice President | VP | Executive | TBD | Phase 3 |
| Secretary/Treasurer | ST | Executive | TBD | Phase 4 |
| Community Builder | CB | Membership | Lucky Surya Haryadi | Phase 1 (now) |
| Member Engagement | ME | Membership | TBD | Phase 4 |
| Member Relations | MR | Membership | TBD | Phase 4 |
| Quality Assurance | QA | Membership | TBD | Phase 4 |
| Visitor Host Coordinator | VH | Support | TBD | Phase 4 |
| Education Coordinator | Edu | Support | TBD | Phase 4 |
| Mentor Coordinator | Mentor | Support | TBD | Phase 4 |
| Communications/Webmaster | Comms | Support | TBD | Phase 4 |

## Per-Role Specification

### CB — Community Builder (Phase 1, current focus)

Responsibilities:
- Maintain Top 10 Most Wanted classifications
- Schedule visitor events
- Coordinate with Chapter Consultant
- Form and manage Power Teams based on shared target market

Dashboard:
- Smart Top 10 Wanted (auto-scored by member need + cluster gap)
- Contact sphere map (filled vs empty)
- Power Team tracker (members, target customer, activity, gaps)
- Visitor pipeline (match score, follow-up status)
- Chapter gap analysis

AI Assistant:
- Auto-cluster members by target market from business profiles
- Score wanted classifications by impact
- Match visitors to wanted list instantly
- Detect referral gaps between members
- Suggest Power Team restructure based on data
- Generate event proposals targeting specific gaps

Bot Commands (Telegram):
- /top10 — current Top 10 Wanted with scores
- /powerteams — list all Power Teams
- /gaps — current classification gaps
- /match [keyword] — find members who serve a keyword
- /visitor_match [name] — score a visitor against wanted list

### VP — Vice President (Phase 3)

Responsibilities:
- Mark attendance weekly
- Submit PALMS report within 48h
- Send accountability letters
- 7-month check-ins
- Chair Membership Committee

Dashboard:
- Live attendance tracker per meeting
- PALMS auto-generated from bot data
- Rolling 6-month breach monitor
- Renewal timeline
- Member health heatmap

AI Assistant:
- Auto-draft accountability letters from attendance data
- Predict breach before it happens (pattern detection)
- Auto-generate PALMS report from attendance + referral bot data
- Remind 7-month check-in schedule

Bot Commands (Telegram):
- /attendance [date] — open attendance for a meeting
- /palms — generate current PALMS summary
- /breach — list members approaching or exceeding limits
- /renewals — upcoming renewal dates

### ST — Secretary/Treasurer (Phase 4)

Dashboard: budget tracker, renewal calendar, speaker roster, payment status
AI: auto-remind renewals 30 days before, suggest speaker rotation, budget report

### ME — Member Engagement (Phase 4)

Dashboard: engagement heatmap, Traffic Light auto-calc, Power of One tracker
AI: detect struggling members (attendance down, referrals declining, few 1-to-1s),
suggest intervention per member, auto-generate outreach message

### MR — Member Relations (Phase 4)

Dashboard: classification overlap detector, conflict log, resolution history
AI: detect Layer 1 vs Layer 2 conflicts, suggest resolution, draft communications

### QA — Quality Assurance (Phase 4)

Dashboard: application pipeline, onboarding tracker (day count), 7-month calendar
AI: alert if onboarding > 10 days, auto-schedule interviews, checklist tracker

### VH — Visitor Host (Phase 4)

Dashboard: visitor pipeline funnel, match score per visitor, conversion rate
AI: auto-match visitor to wanted list, auto-score fit, generate follow-up message,
alert if follow-up > 24h not done

### Edu — Education Coordinator (Phase 4)

Dashboard: content calendar, CEU tracker, topic history
AI: suggest topic based on chapter data needs, curate BNI podcasts/videos, draft script

### Mentor — Mentor Coordinator (Phase 4)

Dashboard: Passport Program progress, mentor assignment matrix, completion rate
AI: auto-assign mentor by Power Team compatibility, alert if mentor not reached out in 48h

### Comms — Communications/Webmaster (Phase 4)

Dashboard: content calendar, post scheduler, event queue
AI: draft social media posts from meeting highlights, event announcements, newsletter digest
CMS: full content management on web
