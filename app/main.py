from fastapi import FastAPI, Request, Depends, HTTPException, status, Response, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from .models import Chapter, Member, FormTemplate, FormResponse, EduContent, ActivityLog
from .ai import chat_with_ai
from .auth import verify_password, create_access_token, get_current_user, require_auth, ACCESS_TOKEN_EXPIRE_MINUTES
from .data_engine import process_roster_excel, get_sop_status
from datetime import datetime, timedelta
from typing import Optional

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
    if user.role != "admin":
        return RedirectResponse(url="/")
    chapter = db.query(Chapter).first()
    sop_status = get_sop_status(db)
    return templates.TemplateResponse(
        request=request, name="admin_upload.html", context={"chapter": chapter, "user": user, "sop_status": sop_status}
    )

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
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Akses ditolak")
    
    chapter = db.query(Chapter).first()
    content = await file.read()
    
    summary = {}
    if data_type == "roster":
        summary = process_roster_excel(content, chapter.id, db)
        # Log activity
        log = ActivityLog(
            chapter_id=chapter.id,
            actor_id=user.id,
            action="upload_roster_sync",
            target_type="member",
            data={"summary": summary, "filename": file.filename}
        )
        db.add(log)
        db.commit()
    else:
        # Placeholder for other types
        return JSONResponse({"detail": f"Tipe data {data_type} segera hadir"}, status_code=400)

    return {"status": "ok", "summary": summary}

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

@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
async def unauthorized_exception_handler(request: Request, exc: HTTPException):
    return RedirectResponse(url="/login")
