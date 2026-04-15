# Design Decisions

## D001 — Dedicated vs Shared Services
Decision: Dedicated PostgreSQL and Caddy per project
Reason: Avoid conflicts between projects. Simpler debugging. Independent lifecycle.
Date: 2026-04-15

## D002 — JSONB for Business Profiles
Decision: Store business profiles as JSONB, not fixed columns
Reason: Questions may change quarterly. New data points added without migration.
Date: 2026-04-15

## D003 — No Seed Data
Decision: System starts empty. All data via upload or form.
Reason: Avoid stale/wrong hardcoded data. System must learn from real input.
Date: 2026-04-15

## D004 — Power Teams by Target Market
Decision: Group members by shared target customer, not by similar profession
Reason: Members who serve the same customer type generate real referrals.
Example: MBG (franchise F&B) needs contractor, kitchen supplier, HR, signage — not "all food people."
Date: 2026-04-15

## D005 — Telegram Internal, WhatsApp External
Decision: Two separate bots for two audiences
Reason: LT needs operational commands (admin). Members/public need notifications (read-mostly).
Date: 2026-04-15

## D006 — DNS via ClouDNS
Decision: Use ClouDNS instead of Cloudflare
Reason: Cloudflare does not support .je TLD. ClouDNS supports any TLD, free plan sufficient.
Date: 2026-04-15
