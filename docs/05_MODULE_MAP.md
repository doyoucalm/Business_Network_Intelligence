# 05 — Module Map

## Overview

Each module is independent but connects to the shared database.
Modules are built in phases. Earlier phases are prerequisites for later ones.

## Phase 1 — LIVE (Target: 16 April 2026)

| Module | Description | Depends On |
|--------|-------------|------------|
| M1.1 Infrastructure | VPS, Docker, domain, SSL, Caddy, PostgreSQL | Nothing |
| M1.2 Database | Schema creation, empty tables ready | M1.1 |
| M1.3 Landing Page | Home page at bnimahardika.qd.je | M1.1 |
| M1.4 Edu Moment | Presentation page at /edu | M1.1 |
| M1.5 Business Profile Form | 3-question form at /form, saves to DB | M1.1, M1.2 |
| M1.6 Auth | Login page, session, role-based access | M1.2 |

## Phase 2 — DATA ENGINE (Target: Week 2-3)

| Module | Description | Depends On |
|--------|-------------|------------|
| M2.1 Admin Upload | Excel upload, auto-detect, preview, validate, import | M1.2, M1.6 |
| M2.2 LLM Integration | OpenRouter + DeepSeek: parse, cluster, brief | M1.2 |
| M2.3 Scoring Engine | Health, affinity, match, breach — computed scores | M1.2, M2.2 |

## Phase 3 — OPERATIONS (Target: Week 3-5)

| Module | Description | Depends On |
|--------|-------------|------------|
| M3.1 CB Dashboard | Power teams, Top 10, gap analysis, contact sphere | M2.1, M2.3 |
| M3.2 VP Dashboard | Attendance, PALMS, breach alerts, renewal | M2.1, M2.3 |
| M3.3 Telegram Bot | LT internal operations | M2.1, M1.6 |
| M3.4 WhatsApp Bot | Member & public notifications | M2.1, M1.6 |

## Phase 4 — ALL LT ROLES (Target: Week 6-10)

| Module | Description | Depends On |
|--------|-------------|------------|
| M4.1 President Dashboard | Chapter overview, LT summary, auto-agenda | M3.1, M3.2 |
| M4.2 ST Dashboard | Budget, renewals, speaker roster | M2.1 |
| M4.3 ME Dashboard | Engagement heatmap, struggling member detection | M2.3 |
| M4.4 MR Module | Classification overlap, conflict log | M2.1 |
| M4.5 QA Module | Onboarding pipeline, 7-month scheduler | M2.1 |
| M4.6 VH Module | Visitor pipeline, match scoring, follow-up | M2.3 |
| M4.7 Edu Module | Content calendar, topic AI, CEU tracker | M2.2 |
| M4.8 Mentor Module | Passport tracker, auto-assign, completion alerts | M2.1 |
| M4.9 Comms Module | CMS, social media drafts, event announcements | M2.2 |

## Phase 5 — INTELLIGENCE (Target: Month 3-4)

| Module | Description | Depends On |
|--------|-------------|------------|
| M5.1 Recommendation Engine | "Member You Should Meet", referral gap | M2.3, M4.* |
| M5.2 Predictive Analytics | Churn risk, growth forecast | M2.3 |
| M5.3 Event Management | Full lifecycle: create → register → pay → attend → report | M3.3, M3.4 |

## Phase 6 — SCALE (Future)

| Module | Description | Depends On |
|--------|-------------|------------|
| M6.1 Multi-Chapter | Support multiple chapters | All above |
| M6.2 Inter-Chapter Referrals | Cross-chapter referral network | M6.1 |
| M6.3 Regional Dashboard | Aggregate analytics | M6.1 |
| M6.4 White-Label | Template for other chapters | M6.1 |

## Dependency Graph (simplified)

Copy
M1.1 → M1.2 → M1.5, M1.6 │ ▼ M2.1 → M2.2 → M2.3 │ ┌───────┼────────┐ ▼ ▼ ▼ M3.1 M3.2 M3.3/M3.4 │ │ │ ▼ ▼ ▼ M4.* (all LT role modules) │ ▼ M5.* (intelligence) │ ▼ M6.* (scale)

Copy
