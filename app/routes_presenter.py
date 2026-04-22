from fastapi import Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from .database import get_db
from .models import Meeting, Attendance, Member, MemberPresentation, MemberRole, Chapter, PalmsSnapshot, Visitor, Announcement
from .auth import require_auth, is_admin
from datetime import datetime, timedelta
import collections

templates = Jinja2Templates(directory="templates")

async def presenter_view(meeting_id: str, request: Request, db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    meeting = db.query(Meeting).filter_by(id=meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404)
    
    chapter = db.query(Chapter).first()
    
    # --- DATA GATHERING ---
    
    # Hosts
    core_values_host = db.query(Member).filter_by(id=meeting.meta.get("core_values_host_id")).first()
    edu_host = db.query(Member).filter_by(id=meeting.meta.get("education_host_id")).first()
    
    # LT Roles
    active_roles = db.query(MemberRole).filter_by(is_active=True).all()
    lt_roles = []
    for r in active_roles:
        m = db.query(Member).filter_by(id=r.member_id).first()
        if m:
            lt_roles.append({"role": r.role, "name": m.full_name, "photo": m.photo_url})
            
    # Gold Members
    gold_list = db.query(Member).filter_by(is_gold_member=True, membership_status="active").all()
    
    # New Members (joined in last 30 days)
    thirty_days_ago = datetime.utcnow().date() - timedelta(days=30)
    new_members = db.query(Member).filter(Member.join_date >= thirty_days_ago, Member.membership_status=="active").all()
    
    # Weekly Presentations (Attendance based)
    # Present members (Status 'P' or 'S')
    attendance = db.query(Attendance).filter(Attendance.meeting_id == meeting_id, Attendance.status.in_(['P', 'S'])).all()
    present_member_ids = [a.member_id for a in attendance]
    present_members = db.query(Member).filter(Member.id.in_(present_member_ids)).all()
    
    # Group by category
    grouped = collections.defaultdict(list)
    for m in present_members:
        cat = m.classification or "Other"
        p = db.query(MemberPresentation).filter_by(member_id=m.id, is_active=True).first()
        m.presentation = p
        # Mock traffic light for now
        m.traffic_light = "green" if m.profile_completed else "grey"
        grouped[cat].append(m)
    
    # Sort categories alphabetically
    sorted_categories = sorted(grouped.keys())
    
    # Visitors
    this_week_visitors = db.query(Visitor).filter(Visitor.created_at >= meeting.meeting_date).all()
    
    # Feature Presentation
    feature_presenter = db.query(Member).filter_by(id=meeting.meta.get("feature_presenter_id")).first()
    feature_info = {
        "presenter": feature_presenter,
        "title": meeting.meta.get("feature_title")
    }
    
    # Stats
    tyfcb_sum = db.query(func.sum(PalmsSnapshot.tyfcb_amount)).scalar() or 0
    
    # --- SLIDE BUILDER ---
    
    slides = []

    # Act 1: Static opening
    slides += [
        {"type": "static", "template": "wm_title", "data": {"date": meeting.meeting_date, "theme": meeting.meta.get("theme")}},
        {"type": "static", "template": "open_networking"},
        {"type": "static", "template": "welcome_video"},
        {"type": "static", "template": "etiquettes"},
        {"type": "static", "template": "disclaimer"},
    ]

    # Act 2: Foundations
    slides += [
        {"type": "static", "template": "global_stats"},
        {"type": "static", "template": "mission_vision"},
        {"type": "dynamic", "template": "core_values", "data": {"host": core_values_host}},
        {"type": "static", "template": "bni_overview"},
        {"type": "dynamic", "template": "education_moment", "data": {"host": edu_host}},
    ]

    # Act 3: Leadership + Recognition
    slides.append({"type": "dynamic", "template": "lt_roster", "data": {"roles": lt_roles}})
    slides.append({"type": "dynamic", "template": "gold_members", "data": {"members": gold_list}})

    if new_members:
        slides.append({"type": "static", "template": "code_of_ethics"})
        for nm in new_members:
            slides.append({"type": "dynamic", "template": "new_member", "data": {"member": nm}})

    # Act 4: Weekly Presentations
    flat_presenters = []
    for cat in sorted_categories:
        for m in grouped[cat]:
            flat_presenters.append(m)

    for cat in sorted_categories:
        slides.append({"type": "category_header", "template": "category_header", "data": {"name": cat}})
        for i, m in enumerate(grouped[cat]):
            # Predict next
            next_p = None
            current_idx_in_flat = flat_presenters.index(m)
            if current_idx_in_flat + 1 < len(flat_presenters):
                next_p = flat_presenters[current_idx_in_flat + 1]
            
            slides.append({
                "type": "member_card",
                "template": "member_card",
                "data": {
                    "member": m,
                    "presentation": m.presentation,
                    "is_green": m.traffic_light == "green",
                    "next_presenter": next_p,
                }
            })

    slides.append({"type": "static", "template": "still_looking_for"})
    slides.append({"type": "static", "template": "did_we_miss"})

    # Act 5: Closing
    slides.append({"type": "dynamic", "template": "visitor_intro", "data": {"visitors": this_week_visitors}})
    slides.append({"type": "dynamic", "template": "feature_presentation", "data": {"feature": feature_info}})
    slides.append({"type": "static", "template": "photo_session"})
    slides.append({"type": "static", "template": "closing"})
    
    return templates.TemplateResponse(
        "presenter.html",
        {"request": request, "chapter": chapter, "meeting": meeting, "slides": slides, "user": user}
    )
