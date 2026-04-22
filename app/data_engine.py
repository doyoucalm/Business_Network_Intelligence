import pandas as pd
import io
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .models import Member, Chapter, ActivityLog, UploadedFile, PalmsSnapshot, Visitor
import json

SOP_SCHEDULE = [
    {"task": "Roster Sync", "frequency": "Monthly", "description": "Update member list from BNI Connect", "role": "VP/ST"},
    {"task": "PALMS Import", "frequency": "Weekly", "description": "Import attendance and referral stats", "role": "VP"},
    {"task": "Visitor Report", "frequency": "Weekly", "description": "Import visitor data for follow-up", "role": "VH"},
    {"task": "Profile Review", "frequency": "Quarterly", "description": "Verify business profile accuracy", "role": "CB"}
]

def process_roster_excel(file_content: bytes, chapter_id, db: Session):
    try:
        file_stream = io.BytesIO(file_content)
        
        # 1. BNI XML Spreadsheet 2003 detection
        if file_content.startswith(b"<?xml"):
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(file_content, 'xml')
            rows = []
            for row in soup.find_all('Row'):
                cells = [cell.get_text() for cell in row.find_all('Data')]
                if cells: rows.append(cells)
            
            # Find the header row (contains Member Name)
            member_data = []
            start_parsing = False
            for r in rows:
                if 'Member Name' in r:
                    start_parsing = True
                    continue
                if start_parsing:
                    # Skip sub-header or summary rows
                    if 'G' in r and 'R' in r: continue
                    if len(r) < 3: continue
                    
                    # BNI XML format: [Name, Classification, Company, Phone, G, R, V, 121, L, Abs]
                    member_data.append({
                        "Member": r[0],
                        "Classification": r[1] if len(r) > 1 else "",
                        "Company": r[2] if len(r) > 2 else "",
                        "Phone": r[3] if len(r) > 3 else "",
                        "Email": "" # BNI Roster XML usually doesn't have email for privacy, we'll match by name
                    })
            df = pd.DataFrame(member_data)
        else:
            # 2. Fallback to standard Excel/CSV
            try:
                df = pd.read_excel(file_stream)
            except Exception:
                file_stream.seek(0)
                df = pd.read_csv(file_stream)
    except Exception as e:
        raise ValueError(f"Gagal memproses file: {str(e)}")

    if df.empty:
        raise ValueError("File kosong atau data member tidak ditemukan.")
    
    summary = {"added": 0, "updated": 0, "errors": 0}
    
    for _, row in df.iterrows():
        try:
            name = str(row.get("Member", row.get("Member Name", row.get("Full Name", "")))).strip()
            if not name or name == "nan": continue
            
            classification = str(row.get("Classification", "")).strip()
            company = str(row.get("Company", row.get("Company Name", ""))).strip()
            phone = str(row.get("Phone", "")).strip()
            email = str(row.get("Email", "")).strip()
            
            member = db.query(Member).filter(Member.full_name.ilike(f"%{name}%")).first()
            
            if member:
                member.membership_status = "active"
                if classification: member.classification = classification # v3 schema
                if company: member.company = company # v3 schema
                if phone: member.phone = phone
                summary["updated"] += 1
            else:
                new_member = Member(
                    chapter_id=chapter_id,
                    full_name=name,
                    classification=classification, # v3 schema
                    company=company, # v3 schema
                    phone=phone,
                    email=email if (email and email != "nan") else None,
                    membership_status="active",
                    role="member"
                )
                db.add(new_member)
                summary["added"] += 1
        except Exception as e:
            print(f"Error processing row: {e}")
            summary["errors"] += 1
            
    db.commit()
    return summary

def process_palms_excel(file_content: bytes, chapter_id, db: Session):
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(file_content, 'xml')
        rows = []
        for row in soup.find_all('Row'):
            cells = [cell.get_text() for cell in row.find_all('Data')]
            if cells: rows.append(cells)
            
        summary = {"processed": 0, "matched": 0, "errors": 0}
        
        # BNI PALMS format detection
        for r in rows:
            # Detect table start (usually 15 columns for PALMS)
            if len(r) >= 15:
                # Check if first cell looks like a name (Alpha or containing apostrophe)
                if not (r[0].replace(' ','').isalpha() or "'" in r[0]): continue
                if r[0] in ['Visitors', 'BNI', 'Total']: continue # Skip footer rows
                
                try:
                    first_name = r[0].strip()
                    last_name = r[1].strip()
                    full_name_report = f"{first_name} {last_name}"
                    
                    # 1. Match Member
                    member = db.query(Member).filter(
                        (Member.full_name.ilike(f"%{first_name}%")) & 
                        (Member.full_name.ilike(f"%{last_name}%"))
                    ).first()
                    
                    if not member:
                        member = db.query(Member).filter(Member.full_name.ilike(f"%{first_name}%")).first()

                    if member:
                        # 2. Create Snapshot
                        # In v3, we need period_start/end. For now, we'll use today as placeholder 
                        # until we parse the date from the report header
                        now = datetime.utcnow().date()
                        snapshot = PalmsSnapshot(
                            chapter_id=chapter_id,
                            member_id=member.id,
                            period_label="Current Report",
                            period_start=now - timedelta(days=7),
                            period_end=now,
                            present_count=int(float(r[2])) if r[2].replace('.','').replace('-','').isdigit() else 0,
                            absent_count=int(float(r[3])) if r[3].replace('.','').replace('-','').isdigit() else 0,
                            late_count=int(float(r[4])) if r[4].replace('.','').replace('-','').isdigit() else 0,
                            medical_count=int(float(r[5])) if r[5].replace('.','').replace('-','').isdigit() else 0,
                            substitute_count=int(float(r[6])) if r[6].replace('.','').replace('-','').isdigit() else 0,
                            referrals_given=int(float(r[7])) if r[7].replace('.','').replace('-','').isdigit() else 0,
                            referrals_received=int(float(r[8])) if r[8].replace('.','').replace('-','').isdigit() else 0,
                            visitors_brought=int(float(r[9])) if r[9].replace('.','').replace('-','').isdigit() else 0,
                            one_to_ones=int(float(r[10])) if r[10].replace('.','').replace('-','').isdigit() else 0,
                            ceu_credits=int(float(r[11])) if r[11].replace('.','').replace('-','').isdigit() else 0,
                            tyfcb_amount=float(r[13]) if r[13].replace('.','').replace('E','').replace('+','').replace('-','').isdigit() else 0,
                            raw_data={"report_name": full_name_report, "testimonials": int(float(r[14])) if r[14].replace('.','').replace('-','').isdigit() else 0}
                        )
                        db.add(snapshot)
                        summary["matched"] += 1
                    
                    summary["processed"] += 1
                except Exception as e:
                    print(f"Error parsing palms row: {e}")
                    summary["errors"] += 1
                    
        db.commit()
        return summary
    except Exception as e:
        raise ValueError(f"Gagal memproses PALMS: {str(e)}")

def process_visitor_excel(file_content: bytes, chapter_id, db: Session):
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(file_content, 'xml')
        rows = []
        for row in soup.find_all('Row'):
            cells = [cell.get_text() for cell in row.find_all('Data')]
            if cells: rows.append(cells)
            
        summary = {"processed": 0, "added": 0, "errors": 0}
        
        # BNI Visitor Report format detection
        start_parsing = False
        for r in rows:
            if 'First Name' in r and 'Invited By' in r:
                start_parsing = True
                continue
            
            if start_parsing:
                if len(r) < 10: continue
                
                try:
                    first_name = r[0].strip()
                    last_name = r[1].strip()
                    invited_by_name = r[13].strip() if len(r) > 13 else ""
                    
                    inviter = db.query(Member).filter(Member.full_name.ilike(f"%{invited_by_name}%")).first()
                    
                    # Using Fluid approach: extra fields in visit_data/meta
                    visitor = Visitor(
                        chapter_id=chapter_id,
                        full_name=f"{first_name} {last_name}",
                        invited_by_id=inviter.id if inviter else None,
                        status="visited",
                        visit_data={
                            "company": r[2].strip() if len(r) > 2 else "",
                            "profession": r[3].strip() if len(r) > 3 else "",
                            "email": r[4].strip() if len(r) > 4 else "",
                            "phone": r[5].strip() if len(r) > 5 else "",
                            "original_type": r[14] if len(r) > 14 else "Visitor"
                        }
                    )
                    db.add(visitor)
                    summary["added"] += 1
                    summary["processed"] += 1
                except Exception as e:
                    print(f"Error parsing visitor row: {e}")
                    summary["errors"] += 1
                    
        db.commit()
        return summary
    except Exception as e:
        raise ValueError(f"Gagal memproses Visitor: {str(e)}")

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
