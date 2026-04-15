# 04 — Database Design

## Philosophy

Fluid database: fixed structural frame + flexible JSONB content.

Fixed columns for data that never changes shape:
- member has name, email, join_date, status
- meeting has date, type
- attendance has meeting_id, member_id, status

JSONB columns for data that evolves:
- business_profile → questions can change, answers are free-form
- meta → any additional data without schema migration
- scores → computed values with flexible breakdown

## Why Not Separate Tables for Everything?

This is a multi-week, evolving project. Requirements will change as more LT roles
are onboarded. JSONB allows adding new data points without ALTER TABLE migrations.
When a pattern stabilizes, it can be promoted to a fixed column.

## Entity Map

Chapter ──1:N── Member │ ├── business_profile (JSONB) ← Layer 2 ├── bni_classification (text) ← Layer 1 ├── meta (JSONB) ← flexible extras │ ├──1:N── Attendance ──N:1── Meeting ├──1:N── Referral (as giver) ├──1:N── Referral (as receiver) └──N:M── PowerTeam (via member_ids JSONB)

Visitor ──N:1── Member (invited_by) UploadedFile ──N:1── Member (uploaded_by) Score → scoped to any entity (chapter, member, power_team, visitor) ActivityLog → tracks all system events

Copy
## Core Tables

1. chapters — id, name, city, region, meeting_day, meeting_time, venue, config(JSONB)
2. members — id, chapter_id, full_name, email, phone, bni_classification, company_name,
   membership_status, role, join_date, password_hash, is_activated,
   business_profile(JSONB), profile_completed, meta(JSONB)
3. meetings — id, chapter_id, meeting_date, meeting_type, is_locked, meta(JSONB)
4. attendance — id, meeting_id, member_id, status, meta(JSONB)
5. power_teams — id, chapter_id, name, description, target_customer(JSONB),
   member_ids(JSONB), is_active, meta(JSONB)
6. referrals — id, chapter_id, giver_id, receiver_id, status, data(JSONB)
7. referral_aggregates — id, member_id, period_start, period_end, counts (from PALMS import)
8. visitors — id, chapter_id, full_name, invited_by_id, status, visit_data(JSONB)
9. uploaded_files — id, filename, file_type, uploaded_by, status, parsed_data(JSONB), import_log(JSONB)
10. scores — id, scope_type, scope_id, score_type, value, details(JSONB)
11. activity_log — id, chapter_id, actor_id, action, target_type, target_id, data(JSONB)

## Dual-Layer Classification

Layer 1 (members.bni_classification): official BNI classification. Read-only for member.
Layer 2 (members.business_profile): actual business — products, customers, partners.
Editable by member. Parsed by AI into structured tags.

Example business_profile JSONB:
{
  "q1_products": "Distributor besi beton untuk proyek konstruksi besar",
  "q2_customers": "Developer perumahan, kontraktor mall, pemerintah",
  "q3_partners": "Bobby — setiap proyek butuh besi, Erick — APAR wajib di gedung baru",
  "parsed_tags": {
    "products": ["besi beton", "material konstruksi"],
    "customers": ["developer", "kontraktor komersial", "pemerintah"],
    "partners": ["Bobby", "Erick"]
  },
  "cluster": "construction_supply",
  "version": 2,
  "submitted_at": "2026-04-16T11:30:00Z"
}

## Score Table Design

Scores are recomputed, never manually edited. scope_type + scope_id + score_type
identifies what is being scored. details(JSONB) contains the breakdown.

Example:
{
  scope_type: "chapter",
  scope_id: "uuid-of-mahardika",
  score_type: "health",
  value: 54.0,
  details: {
    "contact_sphere_coverage": 35,
    "classification_uniqueness": 60,
    "attendance_rate": 55,
    "referral_flow_balance": 40,
    "profile_completion": 39,
    "engagement": 70
  }
}
