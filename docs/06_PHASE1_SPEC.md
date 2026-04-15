# 06 — Phase 1 Specification

## Target
Live by 16 April 2026.

## Scope
Minimum viable: domain resolves, landing page loads, edu moment page works,
business profile form saves to database, login page exists.

## Checklist

### Infrastructure
- [ ] tmux installed, SSH timeout 24h
- [ ] Docker + Docker Compose installed
- [ ] Node.js + Gemini CLI installed
- [ ] Firewall: 22, 80, 443
- [ ] ClouDNS: A record → 84.247.166.162
- [ ] DigitalPlat: nameservers → ClouDNS
- [ ] DNS propagated

### Application
- [ ] docker-compose.yml (Caddy + PostgreSQL + App)
- [ ] Caddyfile for bnimahardika.qd.je
- [ ] .env with credentials
- [ ] Dockerfile for FastAPI
- [ ] requirements.txt
- [ ] Database schema created (via SQLAlchemy models)
- [ ] FastAPI app: main, config, database, models, api
- [ ] Landing page (/)
- [ ] Edu moment page (/edu)
- [ ] Business profile form (/form)
- [ ] Form API: POST /api/profile
- [ ] Login page (/login)
- [ ] Health check: GET /api/health

### Deployment
- [ ] docker compose build — success
- [ ] docker compose up -d — running
- [ ] https://bnimahardika.qd.je — loads
- [ ] https://bnimahardika.qd.je/form — functional
- [ ] https://bnimahardika.qd.je/edu — loads
- [ ] https://bnimahardika.qd.je/api/health — returns ok

### Post-Launch (16 April)
- [ ] QR code ready for edu moment
- [ ] 13+ members fill form at Ha Hi Hi
- [ ] Data verified in database

## Pages

### / (Landing)
Dark theme. BNI red accent (#CF2030). Three cards: Edu Moment, Business Profile, Login.
Chapter branding: "MAHARDIKA HUB — BNI Chapter Mahardika, Bandung"

### /edu (Edu Moment)
Scroll-snap fullscreen slides. 7 slides total.
Topic: "Kenali Tetangga Bisnis Lo"
Ends with QR code to /form.
Content editable via template — Bapak Lucky adjusts text as needed.

### /form (Business Profile)
5 fields: nama, klasifikasi BNI, Q1 products, Q2 customers, Q3 partners.
Saves to members.business_profile (JSONB).
Success message on submit.

### /login (Member Login)
Email + password. Functional auth built in Phase 1, dashboard in Phase 2.
