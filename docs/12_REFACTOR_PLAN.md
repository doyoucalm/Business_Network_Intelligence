# BNI Mahardika Hub — Refactor Plan (April 2026)

## 📍 Current Status Summary
The project has successfully established its infrastructure, authentication, and basic data ingestion. However, there is a significant drift between the **v3.0 Master Specification** (which envisions a complex 20+ table relational system) and the **current implementation** (which uses a simplified model). 

### 🔴 Critical Blockers
1. **Schema Drift:** `app/models.py` and `migrations/001_core_schema.sql` are out of sync.
2. **Broken Data Engine:** PALMS and Visitor imports are unreachable or crash due to missing columns/imports.
3. **Phase 1 Incomplete:** The WM Presenter uses static templates instead of the live-polling state machine defined in the specs.

---

## 🛠 Refactor Roadmap

### Stage 0 — Stabilize (Immediate)
- [x] Commit WIP to `wip/april-22` branch.
- [ ] Auth-gate or remove `/api/admin/debug-*` endpoints.
- [ ] Fix critical typos (`os.path.islink`) and missing imports in `main.py`.
- [ ] Remove Rick Roll fallback.

### Stage 1 — Reconcile Schema
- **Source of Truth:** Adopt `migrations/001_core_schema.sql`.
- **Action:** Regenerate `app/models.py` to match the SQL migration.
- **Migration:** Use Alembic for future schema tracking.
- **Data:** Backfill 51 members into the new schema structure.

### Stage 2 — Fix Data Engine (Phase 2)
- **Imports:** Wire `process_palms_excel` and `process_visitor_excel` correctly.
- **Fluidity:** Use JSONB `meta` fields for non-core visitor/palms data.
- **Auditing:** Implement the `data_imports` audit table.

### Stage 3 — Build the real WM Presenter (Core Deliverable)
- Route: `/presenter/{meeting_id}`.
- Logic: Implement 5s polling state machine.
- Admin: Real-time entry for attendance, referrals, and TYFCB.

### Stage 4 — Role-Based Access (Phase 3)
- Implement `member_roles` table for granular permissions.
- Build tailored dashboards for VP, ST, Growth, and Edu roles.

---

## 📅 Timeline

- **Week 1:** "Make it not lie" (Schema reconciliation + Data engine fixes).
- **Week 2:** "Make it presenter-ready" (Meeting models + Polling + Live Slides).

---
*Plan drafted on 2026-04-22.*
