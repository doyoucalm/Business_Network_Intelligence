# 13 — WM Presenter Spec

> Stage 3 of `docs/12_REFACTOR_PLAN.md`. Replaces the static `/wm/{date}` route.
> Source: 37 reference screenshots in `gdrive:/BNI MAHARDIKA HUB/WM Presentation/` (141-slide PPTX).

## Goal
A live, member-editable web presenter that replaces the 306 MB PPTX. Real-time via 5s polling. Members edit their own cards. Absent members auto-hidden.

## Slide structure (5 acts)

| Act | Slides | What |
|---|---|---|
| 1. Opening | 1–5 | Title, etiquettes, recording disclaimer, open networking |
| 2. Foundations | 6–12 | Global stats, Mission, Vision, Core Values, Givers Gain |
| 3. Leadership | 13–28 | LT teams, Mentor, Gold Member, New Member, Code of Ethics |
| 4. Weekly Presentations | 29–106 | Member cards by category (Business Service, Manufacturers, Finance, Marketing, Events, Health & Beauty, ...) |
| 5. Closing | 107–141 | Visitor intro, Feature Presentation, TYFCB lifetime, VP Report, Top 3 networkers, Photo Session, Green Member, Announcements |

## Slide types

| `slide_type` | Source | Owner | Auto-hide |
|---|---|---|---|
| `static` | `content` JSONB | admin | no |
| `data_bound` | DB query at render time | system | no |
| `member_editable` | content written by member | member | yes (on absence) |
| `external_embed` | Canva / Google Slides URL | member or admin | yes |
| `file_upload` | PPTX → PDF via libreoffice | member or admin | yes |

## New tables

```sql
-- Reusable slide order per chapter
CREATE TABLE meeting_templates (
  id UUID PK, chapter_id UUID FK, slug VARCHAR, name VARCHAR,
  slide_order JSONB,         -- [{position, template_slug, type, params}]
  is_default BOOLEAN
);

-- Member's reusable card (one per active member)
CREATE TABLE member_presentation_card (
  member_id UUID PK FK members(id),
  photo_url, logo_url, tagline,
  products_services TEXT[], looking_for TEXT[],
  contact JSONB,             -- {phone, email, ig, website}
  qr_url, gallery_urls TEXT[],
  business_category VARCHAR, -- 'business_service' | ...
  default_visibility VARCHAR DEFAULT 'visible'
);

-- Materialized slides for THIS meeting
CREATE TABLE meeting_slides (
  id UUID PK, meeting_id UUID FK, position INT,
  template_slug VARCHAR, slide_type VARCHAR,
  owner_member_id UUID NULL,
  content JSONB,
  embed_type VARCHAR,        -- canva | google_slides | youtube | pdf | none
  embed_url TEXT,
  uploaded_file_id UUID NULL,
  visibility VARCHAR DEFAULT 'visible',
  hidden_reason TEXT, hidden_at TIMESTAMPTZ,
  UNIQUE(meeting_id, position)
);

-- Add to existing meetings table
ALTER TABLE meetings
  ADD COLUMN template_id UUID FK,
  ADD COLUMN slide_overrides JSONB DEFAULT '{}',
  ADD COLUMN started_at TIMESTAMPTZ,
  ADD COLUMN ended_at TIMESTAMPTZ;
```

## Visibility rules

Precedence: `hidden_admin > hidden_manual > hidden_auto > visible`

**Auto-hide triggers:**
- Attendance marked `A` or `M` for slide owner
- PALMS upload includes owner in absent list
- Run `auto_hide_absent_slides(meeting_id)` after each event

**Manual hide:** member toggles "Hide my slide this week" on `/member/slides/{meeting_id}`.

## Embed handling

- **Canva:** validate `^https://www\.canva\.com/design/.../view`, render in sandboxed iframe with `?embed`
- **Google Slides:** validate `^https://docs\.google\.com/presentation/d/.../`, rewrite to `/embed`
- **PPTX:** `libreoffice --headless --convert-to pdf`, render via pdf.js, async
- **YouTube:** extract video ID, embed standard

## Routes

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/presenter/{meeting_id}` | open | Live presenter (full screen) |
| GET | `/api/presenter/{meeting_id}/state` | open | Polled every 5s |
| GET | `/member/slides/{meeting_id}` | member | Member's own slides |
| POST | `/api/member/slide/{slide_id}` | member | Edit content/embed |
| POST | `/api/member/slide/{slide_id}/visibility` | member | Hide/show toggle |
| GET | `/member/card` | member | Edit reusable card |
| POST | `/api/admin/meetings/{id}/build-slides` | admin | Materialize from template |
| POST | `/api/admin/meetings/{id}/start` | admin | status → live |
| POST | `/api/admin/meetings/{id}/advance` | admin | next slide (skips hidden) |
| POST | `/api/admin/meetings/{id}/end` | admin | status → completed |

## State machine
```
scheduled → live → (paused ↔ live) → completed
```
`current_slide_index` is the source of truth. Polling clients read it every 5s and render the slide at that index.

## Implementation order (Stage 3, ~5 days)

1. **Day 1 — Schema:** Alembic migration with the 3 new tables + meetings additions. Seed default `meeting_templates` row. Backfill `member_presentation_card` for 51 members.
2. **Day 2 — Read path:** `/presenter/{meeting_id}` template, polling JS, render dispatcher per slide type, iframe sandbox.
3. **Day 3 — Write path:** `build-slides`, rotation algorithm, state machine endpoints, member card edit page.
4. **Day 4 — Auto-hide + admin:** `auto_hide_absent_slides()`, wire into attendance + PALMS, admin live-entry pages.
5. **Day 5 — Dry run:** build slides for next Wednesday, walk every type, test hide scenarios, test 1 Canva + 1 PPTX.

## Open questions (answer before Day 1)

1. Full category list (observed 6, likely more)
2. Rotation slot size per category (looks like 4)
3. Other host-rotation slots beyond Core Values / Givers Gain / Edu & Development
4. Special Announcements: pull from `announcements` table or admin types each week?
5. PPTX conversion: async with placeholder OK?

## Out of scope
Animations, polls during slides, recording/replay, multi-language, slide analytics, mobile-only edit app.
