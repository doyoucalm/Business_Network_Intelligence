# 01 — Project Overview

## Project Name
Mahardika Hub

## Domain
https://bnimahardika.qd.je

## Server
Contabo VPS — 4 Core, 8GB RAM, 145GB SSD, Ubuntu 24.04
IP: 84.247.166.162

## Owner
Lucky Surya Haryadi
Role: Community Builder, BNI Chapter Mahardika, Bandung

## One-Line Summary
AI-powered operating system for BNI Chapter Mahardika that automates
administrative operations for every Leadership Team role, enabling the
team to focus on strategic thinking and relationship building.

## Problem
1. Data scattered across Google Forms, Excel exports, WhatsApp groups
2. BNI classifications do not reflect actual member businesses
3. Power Teams formed by similar profession, not by shared target market
4. Referrals frequently miss the mark — members don't know each other's real business
5. Manual attendance, manual PALMS, manual everything
6. Data lost every leadership term change
7. No single source of truth

## Solution
One integrated platform that:
- Collects real business data from members organically
- Processes with AI (LLM) to generate structured insights
- Automates administrative tasks for every LT role
- Produces actionable intelligence: Power Teams, gap analysis, recommendations
- Communicates via Telegram (LT internal) and WhatsApp (member/public external)

## Core Principles
1. System starts empty — all data enters through upload or form, never hardcoded
2. Validate before import — preview, flag issues, human approves
3. Dual-layer classification — BNI official (Layer 1) + actual business (Layer 2, JSONB)
4. Fluid database — fixed structural frame + flexible JSONB content
5. AI assists, human decides — recommendations require approval
6. Built for handover — next CB/LT can pick up without losing anything

## Users & Channels

| Role | Channel | Access |
|------|---------|--------|
| Leadership Team (LT) | Web dashboard + Telegram Bot | Full admin per role |
| Community Builder (CB) | Web dashboard + Telegram Bot | Power teams, classifications, visitors, gap analysis |
| Member | Web + WhatsApp Bot | Profile, dashboard view, notifications |
| Visitor / Public | Web + WhatsApp Bot | Form, chapter info, event registration |

## Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Backend | Python — FastAPI | Async, fast, easy to extend |
| Database | PostgreSQL 16 | JSONB support, reliable, free |
| Reverse Proxy | Caddy | Auto SSL, simple config |
| AI/LLM | DeepSeek via OpenRouter | Low cost, good quality, API-based |
| Internal Bot | Telegram | Free, rich UI (inline keyboards), LT already uses it |
| External Bot | WhatsApp Business API | Members and public use WhatsApp daily |
| Container | Docker + Docker Compose | Reproducible, isolated, easy deploy |
| Development | Gemini CLI | AI-assisted coding on server |

## Current Status
Phase 1 — Infrastructure setup in progress.
See 06_PHASE1_SPEC.md for details.
