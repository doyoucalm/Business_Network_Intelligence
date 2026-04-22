from fastapi import Request, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .database import get_db
from .models import Meeting, Attendance, Member, Chapter
from .auth import require_auth, is_admin
from datetime import datetime
import uuid

templates = Jinja2Templates(directory="templates")

async def meetings_page(request: Request, db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    if not is_admin(user, db):
        raise HTTPException(status_code=403, detail="Akses ditolak")
    
    chapter = db.query(Chapter).first()
    meetings = db.query(Meeting).order_by(Meeting.meeting_date.desc()).all()
    # Also get members for host selection
    members = db.query(Member).filter_by(membership_status="active").order_by(Member.full_name).all()
    
    return templates.TemplateResponse(
        request, "admin/meetings.html",
        {"chapter": chapter, "meetings": meetings, "members": members, "user": user}
    )

async def create_meeting_api(request: Request, db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    if not is_admin(user, db):
        raise HTTPException(status_code=403)
    
    data = await request.json()
    chapter = db.query(Chapter).first()
    
    try:
        meeting_date = datetime.strptime(data["meeting_date"], "%Y-%m-%d").date()
    except Exception:
        raise HTTPException(status_code=400, detail="Format tanggal salah. Gunakan YYYY-MM-DD")
    
    new_meeting = Meeting(
        chapter_id=chapter.id,
        meeting_date=meeting_date,
        meta={
            "theme": data.get("theme", ""),
            "core_values_host_id": data.get("core_values_host_id"),
            "education_host_id": data.get("education_host_id"),
            "feature_presenter_id": data.get("feature_presenter_id"),
            "feature_title": data.get("feature_title", "")
        }
    )
    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)
    return {"status": "ok", "meeting_id": str(new_meeting.id)}

async def attendance_page(meeting_id: str, request: Request, db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    if not is_admin(user, db):
        raise HTTPException(status_code=403)
    
    meeting = db.query(Meeting).filter_by(id=meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404)
    
    chapter = db.query(Chapter).first()
    members = db.query(Member).filter_by(membership_status="active").order_by(Member.full_name).all()
    
    # Get current attendance for this meeting
    attendance_records = db.query(Attendance).filter_by(meeting_id=meeting_id).all()
    attendance_map = {str(a.member_id): a.status for a in attendance_records}
    
    return templates.TemplateResponse(
        request, "admin/attendance.html",
        {"chapter": chapter, "meeting": meeting, "members": members, "attendance_map": attendance_map, "user": user}
    )

async def save_attendance_api(request: Request, db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    if not is_admin(user, db):
        raise HTTPException(status_code=403)
    
    data = await request.json()
    meeting_id = data["meeting_id"]
    member_id = data["member_id"]
    status_val = data.get("status") # P, A, S, M, L or empty
    
    # Upsert attendance
    attendance = db.query(Attendance).filter_by(meeting_id=meeting_id, member_id=member_id).first()
    
    if not status_val:
        if attendance:
            db.delete(attendance)
    else:
        if attendance:
            attendance.status = status_val
            attendance.recorded_at = datetime.utcnow()
        else:
            attendance = Attendance(
                meeting_id=meeting_id,
                member_id=member_id,
                status=status_val
            )
            db.add(attendance)
    
    db.commit()
    return {"status": "ok"}
