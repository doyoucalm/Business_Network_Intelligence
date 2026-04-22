# Learning — 2026-04-22: Member Lifecycle Is Not Handled

## What we found

The system can ingest a roster and add new members, but has **no model for membership exits or status transitions**. Concretely:

- `members.membership_status` has default `"active"` and is only ever set to `"active"`. Nothing writes `"exited"`, `"inactive"`, `"on_leave"`, etc.
- `process_roster_excel` adds new members it doesn't recognize, but does **not** mark missing-from-roster members as exited. A member dropped from the BNI Connect roster stays `"active"` forever in our DB.
- There's no audit trail (no `joined_at`, `exited_at`, `status_changed_at`).
- No cascade: an exited member's `member_presentation_card`, slides, role assignments, mentor links, and PALMS history all stay live.
- No new-member onboarding workflow: induction (Mentor → Gold → Notable Networker), MSP (Member Success Program), GAINS sheet collection, classification verification, dues setup — none modeled.

## Why this matters

- WM Presenter would show exited members' cards as "absent" forever (auto-hide kicks in, but the card persists).
- New members joining mid-term have no system path: admin manually adds them via roster, but no induction tracking, no mentor assignment, no welcome flow.
- BNI runs on **renewal cycles** (typically annual). Without exit handling, churn/retention reporting is impossible.
- Power Team formation, mentor pairing, and Gold Member tracking all depend on accurate member status.

## The fix (architectural pattern, not yet built)

### Schema
```sql
ALTER TABLE members
  ADD COLUMN joined_at DATE,
  ADD COLUMN exited_at DATE,
  ADD COLUMN exit_reason VARCHAR,           -- 'resigned' | 'expelled' | 'non_renewal' | 'relocated'
  ADD COLUMN induction_stage VARCHAR;       -- 'new' | 'mentor' | 'gold' | 'notable' | 'founder'

CREATE TABLE member_status_history (
  id UUID PK, member_id UUID FK, chapter_id UUID FK,
  from_status VARCHAR, to_status VARCHAR,
  reason TEXT, changed_by UUID FK members(id),
  changed_at TIMESTAMPTZ DEFAULT NOW()
);
```

`membership_status` enum widens to: `active | on_leave | exited | pending`.

### Roster sync logic (additive change to `process_roster_excel`)
- Snapshot member IDs in roster vs DB before write.
- After matching/inserting, mark any active DB member NOT in the roster file as `pending_exit` (NOT silently exited — admin confirms).
- Admin sees a "Roster diff" page after each upload: who's new, who's missing, who's classification-changed. Admin clicks confirm → `exited_at = today`, status → `exited`, reason recorded.

### Cascade on exit
- `member_presentation_card.default_visibility = 'hidden_admin'` (slide stays in DB for history but never shows).
- `member_roles.is_active = false`.
- Mentor pairings closed.
- 1-2-1 booking disabled.
- PALMS history retained (don't delete past data).

### New member onboarding
A small wizard at `/admin/members/new` or `/onboarding/{member_id}`:
1. Basic info (name, classification, company, phone, email).
2. Assign mentor (dropdown of existing members marked `induction_stage >= 'gold'`).
3. Send welcome (Telegram message via bot, not WhatsApp — see Silentek Rule Zero).
4. Set `induction_stage = 'new'`, `joined_at = today`.
5. Stage progression: `new` → `mentor` (after MSP completion) → `gold` (after 90 days + KPI) → `notable` (top performer recognition).

## Lessons

1. **Lifecycle gaps hide in default values.** A column with `default="active"` and no setter elsewhere looks fine until you ask "how does it ever become anything else?" Audit every status enum for write paths to all values.
2. **Roster sync needs a diff phase, not just an upsert.** Pure upsert loses the "missing from source" signal. Always compute set-difference and surface it for admin review.
3. **Cascade is policy, not just code.** What happens to a member's slides, roles, mentor links, and stats when they exit? These are chapter-policy decisions (retain history? hide or delete? grace period?) that must be answered before writing the cascade SQL.
4. **Onboarding is a workflow, not a form.** New members go through stages over months (induction → MSP → Gold). The system needs to track stage, not just "active."

## Action items

- Add to `12_REFACTOR_PLAN.md` as **Stage 4 — Member Lifecycle Module** (proposed next after Stage 3 WM Presenter ships).
- Open question for chapter policy: grace period on missing-from-roster (immediately exit, or 2-week confirmation window)?
- Open question: retain or anonymize exited member PII after N months (GDPR-style hygiene even though Indonesia's PDP law is the relevant frame)?
