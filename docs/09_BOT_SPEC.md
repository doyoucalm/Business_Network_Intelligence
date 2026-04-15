# 09 — Bot Specifications

## Two Bots, Two Audiences

| Bot | Platform | Audience | Purpose |
|-----|----------|----------|---------|
| Mahardika LT Bot | Telegram | Leadership Team | Operations, admin, reports |
| Mahardika Hub Bot | WhatsApp | Members & Public | Notifications, forms, info |

## Telegram Bot — LT Internal (Phase 3)

Access: LT members only (verified by role in database)

### Command Groups

CB Commands:
/top10, /powerteams, /gaps, /match, /visitor_match

VP Commands:
/attendance, /palms, /breach, /renewals

ST Commands:
/budget, /renewals_detail, /speakers

General LT:
/health — chapter health score
/digest — this week's summary
/members — search member by name
/upload — upload Excel via bot (sends to web upload handler)

### Interaction Style
Inline keyboards for quick actions. Minimal typing required.
Example: /attendance → list members → tap Present/Absent per member → confirm → saved.

## WhatsApp Bot — External (Phase 3-4)

Access: any WhatsApp user

### Flows

Visitor:
"Halo, saya mau info BNI Mahardika"
→ Bot: chapter info + next meeting date + registration link

Member:
"Cek attendance saya"
→ Bot: verify phone number → show attendance summary

Notifications (outbound, system-initiated):
- Meeting reminder (1 day before)
- Form fill reminder (quarterly)
- Event invitation
- Renewal reminder (30 days before)
- Follow-up visitor (24h after visit)

## Bot-to-Web Integration
Both bots call the same FastAPI backend endpoints.
No separate database — single source of truth.
