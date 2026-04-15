import pandas as pd
import io
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .models import Member, Chapter, ActivityLog, UploadedFile
import json

SOP_SCHEDULE = [
    {"task": "Roster Sync", "frequency": "Monthly", "description": "Update member list from BNI Connect", "role": "VP/ST"},
    {"task": "PALMS Import", "frequency": "Weekly", "description": "Import attendance and referral stats", "role": "VP"},
    {"task": "Visitor Report", "frequency": "Weekly", "description": "Import visitor data for follow-up", "role": "VH"},
    {"task": "Profile Review", "frequency": "Quarterly", "description": "Verify business profile accuracy", "role": "CB"}
]

def process_roster_excel(file_content: bytes, chapter_id, db: Session):
    df = pd.read_excel(io.BytesIO(file_content))
    
    # Simple BNI Connect Roster Parser logic
    # In production, we would map specific column names
    summary = {"added": 0, "updated": 0, "errors": 0}
    
    for _, row in df.iterrows():
        try:
            name = str(row.get("Member", row.get("Full Name", ""))).strip()
            email = str(row.get("Email", "")).strip()
            
            if not name: continue
            
            member = db.query(Member).filter(Member.full_name.ilike(f"%{name}%")).first()
            if member:
                member.membership_status = "active"
                summary["updated"] += 1
            else:
                new_member = Member(
                    chapter_id=chapter_id,
                    full_name=name,
                    email=email if email else None,
                    membership_status="active"
                )
                db.add(new_member)
                summary["added"] += 1
        except Exception as e:
            print(f"Error processing row: {e}")
            summary["errors"] += 1
            
    db.commit()
    return summary

def get_sop_status(db: Session):
    # Check last upload for each type
    status = []
    for item in SOP_SCHEDULE:
        last_upload = db.query(ActivityLog).filter(
            ActivityLog.action == f"upload_{item['task'].lower().replace(' ', '_')}"
        ).order_by(ActivityLog.created_at.desc()).first()
        
        status.append({
            **item,
            "last_done": last_upload.created_at if last_upload else None,
            "is_overdue": is_overdue(last_upload.created_at if last_upload else None, item["frequency"])
        })
    return status

def is_overdue(last_date, frequency):
    if not last_date: return True
    now = datetime.utcnow()
    if frequency == "Weekly":
        return now - last_date > timedelta(days=7)
    if frequency == "Monthly":
        return now - last_date > timedelta(days=30)
    return False
