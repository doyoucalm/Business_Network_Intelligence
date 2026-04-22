from fastapi import Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .database import get_db
from .models import Member, MemberRole, Chapter
from .auth import require_auth, is_admin
from datetime import datetime

templates = Jinja2Templates(directory="templates")

LT_ROLES = [
    "President", "Vice President", "Secretary/Treasurer", 
    "Education Coordinator", "Mentor Coordinator", "Visitor Host Coordinator",
    "Member Engagement", "Quality Assurance", "Community Building", "Member Relations"
]

async def roles_page(request: Request, db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    if not is_admin(user, db):
        raise HTTPException(status_code=403)
    
    chapter = db.query(Chapter).first()
    members = db.query(Member).filter_by(membership_status="active").order_by(Member.full_name).all()
    
    # Get current active roles
    active_roles = db.query(MemberRole).filter_by(is_active=True).all()
    role_map = {r.role: str(r.member_id) for r in active_roles}
    
    return templates.TemplateResponse(
        request, "admin/roles.html",
        {"chapter": chapter, "members": members, "lt_roles": LT_ROLES, "role_map": role_map, "user": user, "current_term": "2025/2026"}
    )

async def assign_roles_api(request: Request, db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    if not is_admin(user, db):
        raise HTTPException(status_code=403)
    
    data = await request.json() # Expects list of {member_id, role}
    chapter = db.query(Chapter).first()
    
    for item in data:
        role_name = item.get("role")
        member_id = item.get("member_id")
        
        if not role_name: continue
        
        # Deactivate old active role for this position
        db.query(MemberRole).filter_by(role=role_name, is_active=True).update({"is_active": False})
        
        if member_id:
            new_role = MemberRole(
                member_id=member_id,
                chapter_id=chapter.id,
                role=role_name,
                is_active=True
            )
            db.add(new_role)
            
    db.commit()
    return {"status": "ok"}
