# 08 — Data Flow

## Principle
Data enters through defined channels only. Every entry is logged.
System validates before storing. AI processes after storing.

## Input Channels

| Channel | Data Type | Frequency | Actor |
|---------|-----------|-----------|-------|
| Web form /form | Business profile (3 questions) | Quarterly per member | Member |
| Web admin upload | Excel (Roster, PALMS, Visitor, Form export) | Semi-annual | CB/Admin |
| Telegram Bot | Attendance, referral, event, Power Team commands | Weekly | LT |
| WhatsApp Bot | Visitor registration, event RSVP | Per event | Visitor/Member |
| Direct API | Bulk operations, integrations | As needed | Admin |

## Processing Pipeline

INPUT → VALIDATE → STORE → PROCESS → OUTPUT

INPUT Form submission / file upload / bot command

VALIDATE

Required fields present?
Member name matches existing record? (fuzzy match)
File format recognized?
Duplicates detected? → Flag issues for human review if uncertain
STORE

Save raw data (always preserve original)
Save structured data to appropriate table
Log in activity_log
PROCESS (async, after store)

LLM parse business profile → tags, cluster suggestion
Recalculate affected scores (health, affinity, match)
Check attendance breach rules
Update Power Team recommendations
Match visitors to wanted list
OUTPUT

Dashboard refresh (web)
Bot notification (Telegram to LT)
Bot notification (WhatsApp to member/visitor)
Weekly digest generation

Copy
## Upload Flow (Excel)

Admin uploads file → System reads headers → Detect file type (roster? palms? visitor?) → Show preview: "Detected 51 rows, type: roster. Confirm?" → Admin confirms → System validates each row: - Row 1: OK - Row 2: OK - Row 3: WARNING — name not found, possible new member - Row 4: ERROR — missing required field → Show validation report → Admin resolves: skip errors / fix / force import → Import approved rows → log skipped rows → Trigger post-import processing (scores, alerts)

Copy
## Business Profile Flow

Member opens /form → Fills 5 fields (name, classification, Q1, Q2, Q3) → POST /api/profile → Backend: fuzzy match name to existing member - Found → update business_profile JSONB - Not found → create new member record → Save raw answers in business_profile.raw → Trigger LLM parse (async): - Extract product tags - Extract customer tags - Extract partner references (match to member names) - Suggest cluster → Save parsed result in business_profile.parsed_tags → Recalculate: Top 10 Wanted, Power Team suggestions, chapter health → If significant change → notify CB via Telegram

Copy
## Update Frequencies

| Data | Frequency | Trigger |
|------|-----------|---------|
| Business profile | Quarterly | Bot reminder or manual |
| Attendance | Weekly | Post-meeting bot ping |
| Referral detail | Weekly | Post-meeting bot prompt |
| TYFCB | Monthly | Manual or upload |
| Visitor | Per meeting | QR scan or manual |
| PALMS aggregate | Semi-annual | Bulk Excel upload |
| Roster sync | Semi-annual | Bulk Excel upload |
| Score recalculation | On data change | Automatic |
| Weekly digest | Weekly | Cron job |
