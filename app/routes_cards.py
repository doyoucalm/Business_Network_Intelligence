from fastapi import Request, Depends, HTTPException, UploadFile, File
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .database import get_db
from .models import Member, MemberPresentation, Chapter
from .auth import require_auth, is_admin
import os
import uuid
import shutil

templates = Jinja2Templates(directory="templates")

async def cards_list_page(request: Request, db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    if not is_admin(user, db):
        raise HTTPException(status_code=403)
    
    chapter = db.query(Chapter).first()
    members = db.query(Member).filter_by(membership_status="active").order_by(Member.full_name).all()
    
    # Check completion status for each member
    status_map = {}
    for m in members:
        p = db.query(MemberPresentation).filter_by(member_id=m.id, is_active=True).first()
        if not p:
            status_map[str(m.id)] = "red"
        else:
            has_products = len(p.products_services or []) > 0
            has_looking = len(p.looking_for or []) > 0
            if has_products and has_looking:
                status_map[str(m.id)] = "green"
            elif has_products or has_looking:
                status_map[str(m.id)] = "yellow"
            else:
                status_map[str(m.id)] = "red"
                
    return templates.TemplateResponse(
        "admin/cards_list.html",
        {"request": request, "chapter": chapter, "members": members, "status_map": status_map, "user": user}
    )

async def card_editor_page(member_id: str, request: Request, db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    if not is_admin(user, db):
        raise HTTPException(status_code=403)
    
    member = db.query(Member).filter_by(id=member_id).first()
    if not member:
        raise HTTPException(status_code=404)
        
    presentation = db.query(MemberPresentation).filter_by(member_id=member_id, is_active=True).first()
    if not presentation:
        # Create empty one if missing
        presentation = MemberPresentation(member_id=member_id, version=1, title=member.full_name)
        db.add(presentation)
        db.commit()
        db.refresh(presentation)
        
    chapter = db.query(Chapter).first()
    return templates.TemplateResponse(
        "admin/card_editor.html",
        {"request": request, "chapter": chapter, "member": member, "p": presentation, "user": user}
    )

async def save_card_api(member_id: str, request: Request, db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    if not is_admin(user, db):
        raise HTTPException(status_code=403)
    
    data = await request.json()
    member = db.query(Member).filter_by(id=member_id).first()
    p = db.query(MemberPresentation).filter_by(member_id=member_id, is_active=True).first()
    
    if not member or not p:
        raise HTTPException(status_code=404)
        
    # Update member fields
    if "phone" in data: member.phone = data["phone"]
    if "email" in data: member.email = data["email"]
    if "instagram" in data: member.instagram = data["instagram"]
    if "website" in data: member.website = data["website"]
    if "photo_url" in data: member.photo_url = data["photo_url"]
    
    # Update presentation fields
    if "title" in data: p.title = data["title"]
    if "focus_product" in data: p.focus_product = data["focus_product"]
    if "products_services" in data: p.products_services = data["products_services"]
    if "looking_for" in data: p.looking_for = data["looking_for"]
    if "logo_url" in data: p.logo_url = data["logo_url"]
    if "canvas_type" in data: p.canvas_type = data["canvas_type"]
    if "canvas_content" in data: p.canvas_content = data["canvas_content"]
    
    db.commit()
    return {"status": "ok"}

async def upload_image_api(member_id: str, file: UploadFile = File(...), db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    if not is_admin(user, db):
        raise HTTPException(status_code=403)
        
    upload_dir = f"static/uploads/members/{member_id}"
    os.makedirs(upload_dir, exist_ok=True)
    
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(upload_dir, filename)
    
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"url": f"/{filepath}"}
