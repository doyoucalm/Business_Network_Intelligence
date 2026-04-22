from fastapi import FastAPI, Request, Depends, HTTPException, status, Response, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from .models import Chapter, Member, FormTemplate, FormResponse, EduContent, ActivityLog, Meeting, Attendance
from .ai import chat_with_ai
from .auth import verify_password, create_access_token, get_current_user, require_auth, ACCESS_TOKEN_EXPIRE_MINUTES, is_admin
from .data_engine import process_roster_excel, process_palms_excel, process_visitor_excel, get_sop_status
import os
from datetime import datetime, timedelta
from typing import Optional, List

app = FastAPI(title="Mahardika Hub")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ============================================
# PAGES
# ============================================

@app.get("/")
async def home(request: Request, db: Session = Depends(get_db), user: Optional[Member] = Depends(get_current_user)):
    chapter = db.query(Chapter).first()
    return templates.TemplateResponse(
        request=request, name="index.html", context={"chapter": chapter, "user": user}
    )

@app.get("/form/{slug}")
async def form_page(slug: str, request: Request, db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    form = db.query(FormTemplate).filter_by(slug=slug, is_active=True).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form tidak ditemukan")
    chapter = db.query(Chapter).first()
    return templates.TemplateResponse(
        request=request, name="form.html", context={"form": form, "chapter": chapter, "user": user}
    )

@app.get("/edu/{slug}")
async def edu_page(slug: str, request: Request, db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    edu = db.query(EduContent).filter_by(slug=slug, is_published=True).first()
    if not edu:
        raise HTTPException(status_code=404, detail="Konten tidak ditemukan")
    chapter = db.query(Chapter).first()
    return templates.TemplateResponse(
        request=request, name="edu.html", context={"edu": edu, "chapter": chapter, "user": user}
    )

@app.get("/members")
async def members_directory(request: Request, db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    chapter = db.query(Chapter).first()
    members = db.query(Member).filter_by(membership_status="active").order_by(Member.full_name).all()
    return templates.TemplateResponse(
        request=request, name="members.html", context={"chapter": chapter, "members": members, "user": user}
    )

@app.get("/presenter/{meeting_id}")
async def presenter_view(meeting_id: str, request: Request, db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    meeting = db.query(Meeting).filter_by(id=meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting tidak ditemukan")
    
    chapter = db.query(Chapter).first()
    chapter_settings = chapter.settings or {}
    slides_config = chapter_settings.get("wm_slides_config", {})

    context = {
        "chapter": chapter,
        "meeting": meeting,
        "user": user,
        "slides_config": slides_config,
        "is_admin": is_admin(user, db)
    }
    return templates.TemplateResponse(
        request=request, name="wm/presenter.html", context=context
    )

@app.get("/api/presenter/{meeting_id}/state")
async def get_presenter_state(meeting_id: str, db: Session = Depends(get_db)):
    meeting = db.query(Meeting).filter_by(id=meeting_id).first()
    if not meeting:
        return {"error": "not_found"}
    return {
        "current_slide_index": meeting.current_slide_index,
        "status": meeting.status,
        "is_locked": meeting.is_locked
    }

@app.post("/api/presenter/{meeting_id}/state")
async def update_presenter_state(meeting_id: str, request: Request, db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    if not is_admin(user, db):
        raise HTTPException(status_code=403)
    
    data = await request.json()
    meeting = db.query(Meeting).filter_by(id=meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404)
    
    if "current_slide_index" in data:
        meeting.current_slide_index = data["current_slide_index"]
    if "status" in data:
        meeting.status = data["status"]
    
    db.commit()
    return {"status": "ok"}

@app.get("/login")
async def login_page(request: Request, db: Session = Depends(get_db), user: Optional[Member] = Depends(get_current_user)):
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    chapter = db.query(Chapter).first()
    return templates.TemplateResponse(
        request=request, name="login.html", context={"chapter": chapter}
    )

@app.get("/admin/upload")
async def admin_upload_page(request: Request, db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    if not is_admin(user, db):
        return RedirectResponse(url="/")
    chapter = db.query(Chapter).first()
    sop_status = get_sop_status(db)
    return templates.TemplateResponse(
        request=request, name="admin_upload.html", context={"chapter": chapter, "user": user, "sop_status": sop_status}
    )


@app.get("/wm/{date}")
async def wm_slides_page(date: str, request: Request, db: Session = Depends(get_db), user: Optional[Member] = Depends(get_current_user)):
    """Weekly Meeting Slides - e.g., /wm/2026-04-17"""
    chapter = db.query(Chapter).first()
    # Get meeting video from chapter settings
    chapter_settings = chapter.settings or {}
    meeting_config = chapter_settings.get("meeting_video", {})
    # Get slides config safely
    slides_config = chapter_settings.get("wm_slides_config")
    if slides_config is None:
        slides_config = {}
    
    context = {
        "chapter": chapter, 
        "date": date,
        "user": user,
        "meeting_video_id": meeting_config.get("video_id", ""),
        "meeting_video_title": meeting_config.get("title", "Weekly Meeting - Welcome Video"),
        "slides_config": slides_config,
        "global_stats": {
            "members": "340,000+",
            "chapters": "11,300+", 
            "countries": "76"
        }
    }
    
    return templates.TemplateResponse(
        request=request, name="wm/wm_slides.html", context=context
    )

@app.post("/api/admin/wm-slides")
async def save_wm_slides_config(request: Request, db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    if not is_admin(user, db):
        raise HTTPException(status_code=403, detail="Akses ditolak")
    
    data = await request.json()
    chapter = db.query(Chapter).first()
    
    # Update settings JSONB
    settings = chapter.settings or {}
    settings["wm_slides_config"] = data
    chapter.settings = settings
    
    db.add(chapter)
    db.commit()
    
    return {"status": "ok", "message": "Konfigurasi slide berhasil disimpan"}


# ============================================
# AUTH API
# ============================================

@app.post("/api/auth/login")
async def login(response: Response, request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")
    
    user = db.query(Member).filter(Member.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Email atau password salah"}
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    response = JSONResponse(content={"status": "ok", "message": "Login berhasil"})
    response.set_cookie(
        key="access_token", 
        value=access_token, 
        httponly=True, 
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    return response

@app.get("/api/auth/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response

# ============================================
# DATA API
# ============================================

@app.post("/api/admin/upload")
async def admin_upload(
    file: UploadFile = File(...),
    data_type: str = Form(...),
    db: Session = Depends(get_db),
    user: Member = Depends(require_auth)
):
    if not is_admin(user, db):
        raise HTTPException(status_code=403, detail="Akses ditolak")

    chapter = db.query(Chapter).first()
    content = await file.read()

    if data_type == "roster":
        summary = process_roster_excel(content, chapter.id, db)
        action = "upload_roster_sync"
    elif data_type == "palms":
        summary = process_palms_excel(content, chapter.id, db)
        action = "upload_palms_import"
    elif data_type == "visitor":
        summary = process_visitor_excel(content, chapter.id, db)
        action = "upload_visitor_report"
    else:
        return JSONResponse({"detail": f"Tipe data '{data_type}' tidak dikenal. Gunakan: roster, palms, visitor"}, status_code=400)

    log = ActivityLog(
        chapter_id=chapter.id,
        actor_id=user.id,
        action=action,
        target_type=data_type,
        data={"summary": summary, "filename": file.filename}
    )
    db.add(log)
    db.commit()

    return {"status": "ok", "data_type": data_type, "summary": summary}

@app.post("/api/form/{slug}")
async def submit_form(slug: str, request: Request, db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    form = db.query(FormTemplate).filter_by(slug=slug, is_active=True).first()
    if not form:
        return JSONResponse({"detail": "Form tidak ditemukan"}, status_code=404)

    data = await request.json()
    answers = data.get("answers", {})

    for q in form.questions:
        if q.get("required") and not answers.get(q["key"]):
            return JSONResponse({"detail": f"Wajib diisi: {q['label']}"}, status_code=400)

    user.business_profile = {
        **answers,
        "submitted_at": datetime.utcnow().isoformat(),
        "version": (user.business_profile or {}).get("version", 0) + 1
    }
    user.profile_completed = True
    user.updated_at = datetime.utcnow()

    form_resp = FormResponse(
        form_id=form.id,
        respondent_id=user.id,
        respondent_name=user.full_name,
        respondent_email=user.email,
        answers=answers,
        meta={"form_type": form.form_type, "form_name": form.name}
    )
    db.add(form_resp)
    db.commit()

    return {"status": "ok", "respondent": user.full_name}

@app.post("/api/ai/chat")
async def ai_chat(request: Request, user: Optional[Member] = Depends(get_current_user)):
    data = await request.json()
    messages = data.get("messages", [])
    context = data.get("context", "general")
    if not messages:
        return JSONResponse({"detail": "Pesan kosong"}, status_code=400)
    reply = await chat_with_ai(messages, context)
    return {"reply": reply}

@app.get("/api/health")
async def health(db: Session = Depends(get_db)):
    chapter = db.query(Chapter).first()
    return {
        "status": "running",
        "chapter": chapter.name if chapter else None,
        "members": db.query(Member).count(),
        "active_forms": db.query(FormTemplate).filter_by(is_active=True).count(),
        "published_edu": db.query(EduContent).filter_by(is_published=True).count()
    }

@app.post("/api/admin/debug-upload")
async def debug_upload(db: Session = Depends(get_db), file: UploadFile = File(...), user: Member = Depends(require_auth)):
    if not is_admin(user, db):
        raise HTTPException(status_code=403, detail="Akses ditolak")
    os.makedirs("static/uploads/debug", exist_ok=True)
    filepath = f"static/uploads/debug/{file.filename}"
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)
    return {"status": "SAVED", "filename": file.filename, "exists": os.path.exists(filepath)}

@app.get("/api/admin/debug-upload")
async def debug_upload_get():
    return {"error": "You sent a GET request, but this endpoint requires a POST with a file."}

@app.get("/api/admin/debug-list")
async def debug_list(db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    if not is_admin(user, db):
        raise HTTPException(status_code=403, detail="Akses ditolak")
    # List files in the debug directory to confirm they are there
    path = "static/uploads/debug"
    if not os.path.exists(path):
        return {"files": []}
    return {"files": os.listdir(path)}

@app.get("/api/admin/debug-clear")
async def debug_clear(db: Session = Depends(get_db), user: Member = Depends(require_auth)):
    if not is_admin(user, db):
        raise HTTPException(status_code=403, detail="Akses ditolak")
    # Delete all files in the debug directory
    path = "static/uploads/debug"
    if os.path.exists(path):
        import shutil
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception:
                pass
    return {"status": "CLEANED"}


@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
async def unauthorized_exception_handler(request: Request, exc: HTTPException):
    return RedirectResponse(url="/login")
