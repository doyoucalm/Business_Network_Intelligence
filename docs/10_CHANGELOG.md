# 10 — Changelog

## 2026-04-15 — Project Kickoff

### Decisions Made
1. Tech stack: FastAPI + PostgreSQL + Caddy + Docker (all dedicated per project, not shared)
2. Database approach: fluid JSONB for business profiles, fixed columns for structural data
3. Dual-layer classification: BNI official (Layer 1) + actual business (Layer 2)
4. System starts empty — no hardcoded seed data, all via upload/form
5. Telegram for LT internal, WhatsApp for member/public external
6. ClouDNS for DNS management (Cloudflare does not support .je TLD)
7. Domain: bnimahardika.qd.je (DigitalPlat, free)
8. LLM: DeepSeek via OpenRouter (low cost, API-based)
9. Development: Gemini CLI on server for AI-assisted coding
10. Big picture: every LT role gets AI assistant + dashboard, not just CB

### Infrastructure Progress
- [x] Contabo VPS purchased — 4 Core, 8GB RAM, 145GB, Ubuntu 24.04
- [x] Domain registered — bnimahardika.qd.je
- [x] ClouDNS account created
- [x] tmux installed, SSH timeout extended
- [ ] Docker installed
- [ ] Node.js + Gemini CLI installed
- [ ] DNS pointing verified
- [ ] Application deployed

### Context Established
- Chapter Mahardika: 51 members, Bandung
- 20/51 business profile forms collected (Google Form)
- 4 Excel exports available: Roster, PALMS Summary, PALMS Attendance, Visitor Report
- Duplicate classifications identified and corrected (see context/CHAPTER_MAHARDIKA.md)
- Ha Hi Hi meeting scheduled: 16 April 2026, 11:00, Bandung, 25 attendees
- Edu moment scheduled for morning chapter meeting

## Format
Each entry: date, what was decided/changed/completed, and why.
