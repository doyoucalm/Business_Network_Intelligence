from datetime import datetime, date, timedelta
from fastapi import Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import get_db
from .models import Meeting, Attendance, Member, Chapter
from .auth import (
    require_auth,
    is_admin,
    get_member_role_set,
    has_any_role,
    can_edit_meeting_field,
    ROLE_TOP3,
    ROLE_ST,
    ROLE_EDU,
)
from .host_rotation import suggest_next_host, record_host_assignment

templates = Jinja2Templates(directory="templates")

VALID_TYPES = {"regular", "closed", "launchpad"}

# Field → JSONB key in meeting.meta. Top-level columns are special-cased.
META_FIELDS = {
    "theme",
    "feature_presenter_id",
    "feature_presenter_2_id",
    "feature_title",
    "feature_description",
    "core_values_host_id",
    "education_host_id",
}


def _can_view_meetings(user: Member, db: Session) -> bool:
    return is_admin(user, db) or has_any_role(user, db, *ROLE_TOP3, *ROLE_ST, *ROLE_EDU)


async def meetings_page(request: Request, db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    if not _can_view_meetings(user, db):
        raise HTTPException(status_code=403, detail="Akses ditolak")

    chapter = db.query(Chapter).first()
    meetings = db.query(Meeting).order_by(Meeting.meeting_date.desc()).all()
    members = db.query(Member).filter_by(membership_status="active").order_by(Member.full_name).all()

    today = date.today()
    horizon = today + timedelta(days=62)  # 2-month scheduling window

    return templates.TemplateResponse(
        request, "admin/meetings.html",
        {
            "chapter": chapter,
            "meetings": meetings,
            "members": members,
            "user": user,
            "today_iso": today.isoformat(),
            "horizon_iso": horizon.isoformat(),
            "meeting_types": sorted(VALID_TYPES),
        },
    )


async def create_meeting_api(request: Request, db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    if not is_admin(user, db) and not has_any_role(user, db, *ROLE_TOP3):
        raise HTTPException(status_code=403)

    data = await request.json()
    chapter = db.query(Chapter).first()

    try:
        meeting_date = datetime.strptime(data["meeting_date"], "%Y-%m-%d").date()
    except Exception:
        raise HTTPException(status_code=400, detail="Format tanggal salah. Gunakan YYYY-MM-DD")

    meeting_type = (data.get("meeting_type") or "regular").lower()
    if meeting_type not in VALID_TYPES:
        raise HTTPException(status_code=400, detail=f"meeting_type harus salah satu: {sorted(VALID_TYPES)}")

    # Auto-suggest hosts if not provided.
    cv_host = data.get("core_values_host_id") or None
    edu_host = data.get("education_host_id") or None
    if not cv_host:
        s = suggest_next_host(db, chapter.id, "core_value")
        cv_host = str(s.id) if s else None
    if not edu_host:
        s = suggest_next_host(db, chapter.id, "education")
        edu_host = str(s.id) if s else None

    fp1 = data.get("feature_presenter_id") or None
    fp2 = data.get("feature_presenter_2_id") or None
    if meeting_type == "closed":
        fp1 = fp2 = None  # closed meetings have no FP
    if fp1 and fp2 and fp1 == fp2:
        raise HTTPException(status_code=400, detail="Dua FP tidak boleh orang yang sama")

    new_meeting = Meeting(
        chapter_id=chapter.id,
        meeting_date=meeting_date,
        meeting_type=meeting_type,
        weekly_notes=data.get("weekly_notes") or None,
        meta={
            "theme": data.get("theme", ""),
            "core_values_host_id": cv_host,
            "education_host_id": edu_host,
            "feature_presenter_id": fp1,
            "feature_presenter_2_id": fp2,
            "feature_title": data.get("feature_title", ""),
            "feature_description": data.get("feature_description", ""),
        },
    )
    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)

    if cv_host:
        record_host_assignment(db, chapter.id, "core_value", cv_host, meeting_date)
    if edu_host:
        record_host_assignment(db, chapter.id, "education", edu_host, meeting_date)

    return {"status": "ok", "meeting_id": str(new_meeting.id)}


async def meeting_edit_page(meeting_id: str, request: Request, db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    if not _can_view_meetings(user, db):
        raise HTTPException(status_code=403)

    meeting = db.query(Meeting).filter_by(id=meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404)

    chapter = db.query(Chapter).first()
    members = db.query(Member).filter_by(membership_status="active").order_by(Member.full_name).all()
    roles = get_member_role_set(user, db)

    editable = {f: can_edit_meeting_field(user, db, f) for f in (
        "theme", "weekly_notes",
        "feature_presenter_id", "feature_presenter_2_id", "feature_title", "feature_description",
        "core_values_host_id", "education_host_id",
        "meeting_type",
    )}
    # meeting_type only super_admin/admin
    editable["meeting_type"] = is_admin(user, db)

    return templates.TemplateResponse(
        request, "admin/meeting_edit.html",
        {
            "chapter": chapter,
            "meeting": meeting,
            "members": members,
            "user": user,
            "user_roles": sorted(roles),
            "editable": editable,
            "meeting_types": sorted(VALID_TYPES),
        },
    )


async def update_meeting_api(meeting_id: str, request: Request, db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    meeting = db.query(Meeting).filter_by(id=meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404)

    data = await request.json()
    chapter = db.query(Chapter).first()
    meta = dict(meeting.meta or {})
    changed = []

    if "meeting_type" in data and is_admin(user, db):
        mt = (data["meeting_type"] or "regular").lower()
        if mt not in VALID_TYPES:
            raise HTTPException(status_code=400, detail="meeting_type invalid")
        meeting.meeting_type = mt
        changed.append("meeting_type")

    if "weekly_notes" in data and can_edit_meeting_field(user, db, "weekly_notes"):
        meeting.weekly_notes = data["weekly_notes"] or None
        changed.append("weekly_notes")

    for field in META_FIELDS:
        if field not in data:
            continue
        if not can_edit_meeting_field(user, db, field):
            raise HTTPException(status_code=403, detail=f"Tidak punya akses ke field: {field}")
        meta[field] = data[field] or None
        changed.append(field)

    # Closed meetings cannot have feature presenters.
    if meeting.meeting_type == "closed":
        meta["feature_presenter_id"] = None
        meta["feature_presenter_2_id"] = None

    fp1 = meta.get("feature_presenter_id")
    fp2 = meta.get("feature_presenter_2_id")
    if fp1 and fp2 and fp1 == fp2:
        raise HTTPException(status_code=400, detail="Dua FP tidak boleh orang yang sama")

    meeting.meta = meta
    db.commit()
    return {"status": "ok", "changed": changed}


async def attendance_page(meeting_id: str, request: Request, db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    if not is_admin(user, db):
        raise HTTPException(status_code=403)

    meeting = db.query(Meeting).filter_by(id=meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404)

    chapter = db.query(Chapter).first()
    members = db.query(Member).filter_by(membership_status="active").order_by(Member.full_name).all()

    attendance_records = db.query(Attendance).filter_by(meeting_id=meeting_id).all()
    attendance_map = {str(a.member_id): a.status for a in attendance_records}

    return templates.TemplateResponse(
        request, "admin/attendance.html",
        {"chapter": chapter, "meeting": meeting, "members": members, "attendance_map": attendance_map, "user": user},
    )


async def save_attendance_api(request: Request, db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    if not is_admin(user, db):
        raise HTTPException(status_code=403)

    data = await request.json()
    meeting_id = data["meeting_id"]
    member_id = data["member_id"]
    status_val = data.get("status")

    attendance = db.query(Attendance).filter_by(meeting_id=meeting_id, member_id=member_id).first()
    if not status_val:
        if attendance:
            db.delete(attendance)
    else:
        if attendance:
            attendance.status = status_val
            attendance.recorded_at = datetime.utcnow()
        else:
            attendance = Attendance(meeting_id=meeting_id, member_id=member_id, status=status_val)
            db.add(attendance)

    db.commit()
    return {"status": "ok"}


async def host_suggest_api(rotation_type: str, db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    if not _can_view_meetings(user, db):
        raise HTTPException(status_code=403)
    if rotation_type not in ("core_value", "education"):
        raise HTTPException(status_code=400, detail="rotation_type invalid")
    chapter = db.query(Chapter).first()
    m = suggest_next_host(db, chapter.id, rotation_type)
    if not m:
        return {"member_id": None, "full_name": None}
    return {"member_id": str(m.id), "full_name": m.full_name}
