from fastapi import Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from .database import get_db
from .models import Meeting, Attendance, Member, MemberPresentation, MemberRole, Chapter, PalmsSnapshot, Visitor, Announcement
from .auth import require_auth, is_admin
from .traffic_light import calculate_all_traffic_lights
from datetime import datetime, timedelta
import collections

templates = Jinja2Templates(directory="templates")


def get_present_members(meeting_id: str, db: Session):
    """Get members who are present (P) or substituted (S) for a meeting."""
    attendance = db.query(Attendance).filter(
        Attendance.meeting_id == meeting_id,
        Attendance.status.in_(['P', 'S'])
    ).all()
    present_ids = [a.member_id for a in attendance]
    if not present_ids:
        return []

    members = db.query(Member).filter(Member.id.in_(present_ids)).all()
    if not members:
        return []

    # Attach presentation and traffic light to each member
    chapter_id = members[0].chapter_id
    all_tl = calculate_all_traffic_lights(db, chapter_id)
    tl_map = {str(m["member_id"]): m for m in all_tl}

    for m in members:
        m._presentation = db.query(MemberPresentation).filter_by(
            member_id=m.id, is_active=True
        ).first()
        m._is_green = tl_map.get(str(m.id), {}).get("color") == "green"

    return members


async def presenter_view(meeting_id: str, request: Request, db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    meeting = db.query(Meeting).filter_by(id=meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404)

    chapter = db.query(Chapter).first()

    # --- HOSTS ---
    core_values_host = db.query(Member).filter_by(id=meeting.meta.get("core_values_host_id")).first()
    edu_host = db.query(Member).filter_by(id=meeting.meta.get("education_host_id")).first()
    feature_presenter = db.query(Member).filter_by(id=meeting.meta.get("feature_presenter_id")).first()

    # --- LT ROSTER: join MemberRole with Member ---
    lt_roles = db.query(MemberRole, Member).join(Member, MemberRole.member_id == Member.id).filter(
        MemberRole.is_active == True
    ).all()
    # Each result is (MemberRole, Member) tuple

    # --- GOLD MEMBERS ---
    gold_list = db.query(Member).filter_by(is_gold_member=True, membership_status="active").all()

    # --- NEW MEMBERS (joined last 30 days) ---
    thirty_days_ago = datetime.utcnow().date() - timedelta(days=30)
    new_members = db.query(Member).filter(
        Member.join_date >= thirty_days_ago,
        Member.membership_status == "active"
    ).all()

    # --- PRESENT MEMBERS (from attendance) ---
    present_members = get_present_members(meeting_id, db)

    # --- GROUP BY CLASSIFICATION ---
    grouped = collections.defaultdict(list)
    for m in present_members:
        cat = m.classification or "Other"
        grouped[cat].append(m)
    sorted_categories = sorted(grouped.keys())

    # --- VISITORS ---
    visitors = db.query(Visitor).filter(Visitor.chapter_id == chapter.id).all()
    # Unpack visit_data JSONB into the visitor object for template access
    for v in visitors:
        v._company = v.visit_data.get("company", "") if v.visit_data else ""
        v._profession = v.visit_data.get("profession", "") if v.visit_data else ""
        v._phone = v.visit_data.get("phone", "") if v.visit_data else ""
        v._invited_by = ""
        if v.invited_by_id:
            inviter = db.query(Member).filter_by(id=v.invited_by_id).first()
            v._invited_by = inviter.full_name if inviter else ""

    # --- TYFCB LIFETIME TOTAL ---
    tyfcb_total = db.query(func.sum(PalmsSnapshot.tyfcb_amount)).scalar() or 0
    tyfcb_total_str = f"Rp {tyfcb_total:,.0f}".replace(",", ".") if tyfcb_total else "Rp 0"

    # --- TOP 3 LISTS ---
    def get_top3(field):
        """Get top 3 members by a PALMS field, returning dicts with name, value, photo."""
        snapshots = db.query(PalmsSnapshot, Member).join(Member, PalmsSnapshot.member_id == Member.id).order_by(
            field.desc()
        ).limit(3).all()
        result = []
        for i, (snap, m) in enumerate(snapshots):
            val = getattr(snap, field.key, 0)
            result.append({
                "rank": i + 1,
                "name": m.full_name,
                "value": val,
                "photo_url": m.photo_url
            })
        return result

    # --- ANNOUNCEMENTS ---
    now = datetime.utcnow().date()
    announcements = db.query(Announcement).filter(
        Announcement.chapter_id == chapter.id,
        Announcement.is_active == True,
        Announcement.expire_date >= now
    ).order_by(Announcement.priority.desc()).all()

    # --- TRAFFIC LIGHTS ---
    all_tl = calculate_all_traffic_lights(db, chapter.id)
    green_members = [m for m in all_tl if m.get("color") == "green"]

    # --- VP REPORT STATS ---
    present_count = db.query(Attendance).filter_by(meeting_id=meeting_id, status='P').count()
    absent_count = db.query(Attendance).filter_by(meeting_id=meeting_id, status='A').count()
    subs_count = db.query(Attendance).filter_by(meeting_id=meeting_id, status='S').count()

    # --- SLIDE BUILD ---
    slides = []

    # Act 1: Opening (slides 1-5)
    slides.append({"type": "static", "template": "wm_title", "data": {
        "date": str(meeting.meeting_date),
        "theme": meeting.meta.get("theme", "Weekly Meeting")
    }})
    slides.append({"type": "static", "template": "open_networking", "data": {}})
    slides.append({"type": "static", "template": "welcome_video", "data": {
        "video_title": meeting.meta.get("video_title", "Welcome to BNI")
    }})
    slides.append({"type": "static", "template": "etiquettes", "data": {}})
    slides.append({"type": "static", "template": "disclaimer", "data": {}})

    # Act 2: Foundations
    slides.append({"type": "static", "template": "global_stats", "data": {}})
    slides.append({"type": "static", "template": "mission_vision", "data": {}})
    slides.append({"type": "static", "template": "bni_overview", "data": {}})

    # Core Values with host
    slides.append({"type": "dynamic", "template": "core_values", "data": {
        "presenter_name": core_values_host.full_name if core_values_host else ""
    }})

    # Education Moment with host
    slides.append({"type": "dynamic", "template": "education_moment", "data": {
        "presenter": edu_host.full_name if edu_host else "",
        "title": meeting.meta.get("education_title", "Education Moment"),
        "content": meeting.meta.get("education_content", "")
    }})

    # Act 3: Leadership + Recognition
    # LT Roster: each item is (MemberRole, Member) tuple
    lt_roles_data = [{"role": r.role, "name": m.full_name, "photo_url": m.photo_url} for r, m in lt_roles]
    slides.append({"type": "dynamic", "template": "lt_roster", "data": {"roles": lt_roles_data}})

    # Gold Members
    slides.append({"type": "dynamic", "template": "gold_members", "data": {
        "members": [{"full_name": m.full_name, "photo_url": m.photo_url, "gold_since": ""} for m in gold_list]
    }})

    # Code of Ethics + New Members (conditional)
    if new_members:
        slides.append({"type": "static", "template": "code_of_ethics", "data": {}})
        for nm in new_members:
            slides.append({"type": "dynamic", "template": "new_member", "data": {
                "members": [{"full_name": nm.full_name, "photo_url": nm.photo_url,
                             "classification": nm.classification or "", "company": nm.company or ""}]
            }})

    # Act 4: Weekly Presentations
    flat_presenters = []
    for cat in sorted_categories:
        for m in grouped[cat]:
            flat_presenters.append(m)

    for cat in sorted_categories:
        slides.append({"type": "category_header", "template": "category_header", "data": {"category_name": cat}})
        for m in grouped[cat]:
            # Compute next presenter
            next_p = None
            current_idx = flat_presenters.index(m)
            if current_idx + 1 < len(flat_presenters):
                next_p = flat_presenters[current_idx + 1]

            slides.append({
                "type": "member_card",
                "template": "member_card",
                "data": {
                    "member": {
                        "id": str(m.id),
                        "full_name": m.full_name,
                        "photo_url": m.photo_url,
                        "classification": m.classification or "",
                        "company": m.company or "",
                        "phone": m.phone or "",
                        "instagram": m.instagram or "",
                        "email": m.email or "",
                        "website": m.website or "",
                        "is_gold_member": m.is_gold_member,
                        "_is_green": m._is_green,
                    },
                    "presentation": {
                        "logo_url": m._presentation.logo_url if m._presentation else "",
                        "products_services": m._presentation.products_services if m._presentation else [],
                        "looking_for": m._presentation.looking_for if m._presentation else [],
                        "product_images": m._presentation.product_images if m._presentation else [],
                        "canvas_type": m._presentation.canvas_type if m._presentation else "4images",
                    } if m._presentation else {},
                    "is_green": m._is_green,
                    "next_presenter": {
                        "full_name": next_p.full_name if next_p else ""
                    } if next_p else None,
                }
            })

    slides.append({"type": "static", "template": "still_looking", "data": {"category_name": ""}})
    slides.append({"type": "static", "template": "did_we_miss", "data": {}})

    # Act 5: Visitors
    visitors_data = [{
        "full_name": v.full_name,
        "company": v._company,
        "classification": v._profession,
        "invited_by": v._invited_by
    } for v in visitors]
    slides.append({"type": "dynamic", "template": "visitor_intro", "data": {"visitors": visitors_data}})

    # Feature Presentation
    slides.append({"type": "dynamic", "template": "feature_presentation", "data": {
        "member": {
            "full_name": feature_presenter.full_name if feature_presenter else "",
            "photo_url": feature_presenter.photo_url if feature_presenter else "",
            "classification": feature_presenter.classification if feature_presenter else ""
        },
        "title": meeting.meta.get("feature_title", "Feature Presentation"),
        "description": meeting.meta.get("feature_description", "")
    }})

    slides.append({"type": "static", "template": "photo_session", "data": {}})

    # TYFCB Lifetime
    slides.append({"type": "static", "template": "tyfcb_lifetime", "data": {"amount": tyfcb_total_str}})

    # VP Report
    slides.append({"type": "static", "template": "vp_report", "data": {
        "week_number": meeting.meta.get("week_number", ""),
        "stats": {
            "present": present_count,
            "absent": absent_count,
            "subs": subs_count,
            "visitors": len(visitors)
        },
        "vp_message": meeting.meta.get("vp_message", "")
    }})

    # Closing
    slides.append({"type": "static", "template": "closing", "data": {
        "next_meeting_date": meeting.meta.get("next_meeting_date", "")
    }})

    slides.append({"type": "static", "template": "thank_visitors", "data": {}})

    return templates.TemplateResponse(
        request, "presenter.html",
        {"chapter": chapter, "meeting": meeting, "slides": slides, "user": user}
    )
