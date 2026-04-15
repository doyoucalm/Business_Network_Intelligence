# 03 — Architecture

## Infrastructure

| Resource | Detail |
|----------|--------|
| Server | Contabo VPS, 4 Core, 8GB RAM, 145GB SSD |
| IP | 84.247.166.162 |
| OS | Ubuntu 24.04 LTS |
| Domain | bnimahardika.qd.je (DigitalPlat, DNS via ClouDNS) |
| SSL | Auto via Caddy (Let's Encrypt) |

## System Diagram

Internet │ ▼ Caddy (port 80/443, auto SSL) │ ├── bnimahardika.qd.je/* → FastAPI app (port 8000) │ ▼ FastAPI Application ├── Web routes (/, /form, /login, /edu, /admin) ├── API routes (/api/*) ├── Telegram Bot (webhook or polling) └── WhatsApp Bot (webhook) │ ▼ PostgreSQL 16 (port 5432, local only) │ ▼ OpenRouter API → DeepSeek (external, API calls)

Copy
## Docker Composition

All services run in a single docker-compose.yml, dedicated to this project.
No shared services with other projects — isolated and independent.

Services:
1. caddy — reverse proxy + SSL
2. postgres — database
3. app — FastAPI + bot handlers

## Network

Docker network: mahardika-net (internal)
Exposed ports: 80, 443 (via Caddy)
PostgreSQL: internal only (not exposed to internet)

## Multi-Project Strategy

Each project on this VPS gets its own directory under /opt/projects/ with
its own docker-compose.yml, own Caddy instance (different ports), or a shared
Caddy can be set up later if needed. For now, Mahardika Hub is the only project.

## LLM Integration

Provider: OpenRouter (https://openrouter.ai)
Model: DeepSeek (deepseek/deepseek-chat)
Use cases: parse business profiles, auto-cluster, generate briefs, match visitors
Cost estimate: ~$0.01-0.05/week for 51 members
All LLM calls go through backend — never client-side.
