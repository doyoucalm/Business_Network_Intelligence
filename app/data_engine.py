"""
Data parsers for BNI Connect XML SpreadsheetML exports.
Handles: Roster, PALMS Summary, Chapter Visitor Report, Visitor Registration Report.

BNI Connect exports .xls files that are actually XML SpreadsheetML, not real Excel.
All parsers use BeautifulSoup with 'xml' feature to parse them.
"""

import io
from datetime import datetime, timedelta, date as date_type
from sqlalchemy.orm import Session
from .models import (
    Member, Chapter, ActivityLog, UploadedFile,
    PalmsSnapshot, Visitor, DataImport
)


SOP_SCHEDULE = [
    {"task": "Roster Sync", "frequency": "Monthly", "description": "Update member list from BNI Connect", "role": "VP/ST"},
    {"task": "PALMS Import", "frequency": "Weekly", "description": "Import attendance and referral stats", "role": "VP"},
    {"task": "Visitor Report", "frequency": "Weekly", "description": "Import visitor data for follow-up", "role": "VH"},
    {"task": "Profile Review", "frequency": "Quarterly", "description": "Verify business profile accuracy", "role": "CB"},
]


# ═══════════════════════════════════════════════════════════════════
# SHARED UTILITIES
# ═══════════════════════════════════════════════════════════════════

def parse_bni_xml(file_content: bytes) -> list[list[str]]:
    """
    Parse BNI .xls (XML SpreadsheetML) into list of rows.
    Each row is a list of string cell values.
    Handles ss:Index attribute for sparse cells.
    """
    from bs4 import BeautifulSoup

    content = file_content.decode("utf-8", errors="ignore")
    if "<?xml" not in content[:500]:
        raise ValueError("Not a BNI XML SpreadsheetML file")

    soup = BeautifulSoup(content, "xml")
    all_rows = []

    for row_el in soup.find_all("Row"):
        cells = []
        expected_idx = 0
        for cell in row_el.find_all("Cell"):
            idx_attr = cell.get("ss:Index")
            if idx_attr:
                target = int(idx_attr) - 1
                while len(cells) < target:
                    cells.append("")
                expected_idx = target

            data = cell.find("Data")
            cells.append(data.get_text(strip=True) if data else "")
            expected_idx += 1

        if any(c.strip() for c in cells):
            all_rows.append(cells)

    return all_rows


def safe_int(val: str) -> int:
    """Parse '15', '0.0', '36.0', '', '-' → int."""
    if not val or val.strip() in ("", "-"):
        return 0
    try:
        return int(float(val.strip().replace(",", "")))
    except (ValueError, TypeError):
        return 0


def safe_float(val: str) -> float:
    """Parse '49407500.00', '1.856610963E+10', '' → float."""
    if not val or val.strip() in ("", "-"):
        return 0.0
    try:
        return float(val.strip().replace(",", "").upper())
    except (ValueError, TypeError):
        return 0.0


def parse_bni_date(val: str):
    """Parse '2026-04-14T21:30:02.000' or '2025-10-01T00:00:00.000' → date."""
    if not val:
        return None
    try:
        return datetime.fromisoformat(val.split("T")[0]).date()
    except Exception:
        return None


def extract_report_dates(rows: list[list[str]]) -> tuple:
    """Extract From/To dates from BNI report header."""
    from_date = None
    to_date = None
    for row in rows[:20]:
        for i, cell in enumerate(row):
            cell_s = cell.strip() if cell else ""
            if cell_s == "From:" or "From:" in cell_s:
                for j in range(i + 1, min(i + 3, len(row))):
                    d = parse_bni_date(row[j])
                    if d:
                        from_date = d
                        break
            if cell_s == "To:" or "To:" in cell_s:
                for j in range(i + 1, min(i + 3, len(row))):
                    d = parse_bni_date(row[j])
                    if d:
                        to_date = d
                        break
    return from_date, to_date


def match_member_by_name(db: Session, first_name: str, last_name: str,
                         chapter_id=None) -> Member | None:
    """
    Match BNI report name → DB member.
    Handles: "Lucky Surya" + "Haryadi" → "Lucky Surya Haryadi"
    Handles: "Jovian Hartanto" + "Chandra" → "Jovian Hartanto Chandra"
    Handles: "Harisendi" + "Harisendi" → "Harisendi Harisendi"
    """
    first = first_name.strip()
    last = last_name.strip()
    if not first and not last:
        return None

    q = db.query(Member)
    if chapter_id:
        q = q.filter(Member.chapter_id == chapter_id)

    # Strategy 1: Both parts in name
    if first and last:
        m = q.filter(
            Member.full_name.ilike(f"%{first}%"),
            Member.full_name.ilike(f"%{last}%"),
        ).first()
        if m:
            return m

    # Strategy 2: Concatenated match
    full = f"{first} {last}".strip()
    m = q.filter(Member.full_name.ilike(f"%{full}%")).first()
    if m:
        return m

    # Strategy 3: First name only (only if distinctive enough)
    if first and len(first) >= 4:
        m = q.filter(Member.full_name.ilike(f"{first}%")).first()
        if m:
            return m

    return None


# ═══════════════════════════════════════════════════════════════════
# ROSTER PARSER
# ═══════════════════════════════════════════════════════════════════

def process_roster_excel(file_content: bytes, chapter_id, db: Session):
    """
    Parse BNI Chapter Roster Report → update/add members.
    """
    try:
        if file_content.startswith(b"<?xml"):
            rows = parse_bni_xml(file_content)

            summary = {"added": 0, "updated": 0, "skipped": 0, "errors": 0}

            # Find the data section (after header rows)
            parsing = False
            for row in rows:
                # Header detection: row containing "Member Name" or "Classification"
                if any("Member Name" in c or "Classification" in c for c in row):
                    parsing = True
                    continue
                # Skip sub-headers like column labels G, R, V, 121...
                if not parsing:
                    continue
                if len(row) < 3:
                    continue

                name = row[0].strip()
                if not name or name in ("G", "R", "V", "Total", "Visitors", "BNI"):
                    continue

                classification = row[1].strip() if len(row) > 1 else ""
                company = row[2].strip() if len(row) > 2 else ""
                phone = row[3].strip() if len(row) > 3 else ""

                try:
                    member = db.query(Member).filter(
                        Member.full_name.ilike(f"%{name}%")
                    ).first()

                    if member:
                        member.membership_status = "active"
                        if classification:
                            member.classification = classification
                        if company:
                            member.company = company
                        if phone:
                            member.phone = phone
                        summary["updated"] += 1
                    else:
                        db.add(Member(
                            chapter_id=chapter_id,
                            full_name=name,
                            classification=classification,
                            company=company,
                            phone=phone,
                            membership_status="active",
                        ))
                        summary["added"] += 1
                except Exception as e:
                    print(f"Roster row error: {e}")
                    summary["errors"] += 1

            db.commit()
            return summary
        else:
            # Fallback: pandas for real xlsx/csv
            import pandas as pd
            stream = io.BytesIO(file_content)
            try:
                df = pd.read_excel(stream)
            except Exception:
                stream.seek(0)
                df = pd.read_csv(stream)

            summary = {"added": 0, "updated": 0, "errors": 0}
            for _, row in df.iterrows():
                name = str(row.get("Member", row.get("Full Name", ""))).strip()
                if not name or name == "nan":
                    continue
                member = db.query(Member).filter(Member.full_name.ilike(f"%{name}%")).first()
                if member:
                    member.membership_status = "active"
                    summary["updated"] += 1
                else:
                    db.add(Member(chapter_id=chapter_id, full_name=name, membership_status="active"))
                    summary["added"] += 1
            db.commit()
            return summary
    except Exception as e:
        raise ValueError(f"Gagal memproses Roster: {str(e)}")


# ═══════════════════════════════════════════════════════════════════
# PALMS SUMMARY PARSER — HEADER-BASED COLUMN MAPPING
# ═══════════════════════════════════════════════════════════════════

def _get_palms_col(row: list, col_map: dict, *keys):
    """Get cell value from PALMS row by column name variants."""
    for key in keys:
        if key in col_map:
            idx = col_map[key]
            if idx < len(row):
                return row[idx].strip()
    return ""


def _find_header_row_palms(rows: list) -> tuple:
    """Find the PALMS header row and build column map. Returns (header_row, col_map, header_idx)."""
    for idx, row in enumerate(rows):
        if len(row) < 10:
            continue
        row_lower = [c.lower() for c in row]
        # PALMS header has "First Name", "Last Name", "RGI", "RGO", "TYFCB" etc.
        has_name = any("first name" in c or "last name" in c for c in row_lower)
        has_rgi = any(c.strip() in ("rgi", "rg i", "referrals given inside") for c in row)
        has_tyfcb = any("tyfcb" in c.lower() or "1-2-1" in c.lower() for c in row_lower)
        if has_name and has_rgi:
            col_map = {c.strip(): j for j, c in enumerate(row) if c.strip()}
            return row, col_map, idx
    return None, {}, -1


def process_palms_excel(file_content: bytes, chapter_id, db: Session):
    """
    Parse BNI Chapter Summary PALMS Report.

    Uses header-based column mapping to handle sparse/misaligned cells.
    Expected headers (case-insensitive):
      First Name, Last Name, P, A, L, M, S, RGI, RGO, RRI, RRO,
      V (Visitors), 1-2-1, TYFCB, CEU
    """
    try:
        rows = parse_bni_xml(file_content)
        from_date, to_date = extract_report_dates(rows)

        # Build column map from header row
        header_row, col_map, header_idx = _find_header_row_palms(rows)
        if header_idx < 0:
            raise ValueError("Cannot find PALMS header row. File format not recognized.")

        summary = {
            "processed": 0,
            "matched": 0,
            "updated": 0,
            "unmatched": 0,
            "skipped": 0,
            "errors": 0,
            "period_start": str(from_date) if from_date else None,
            "period_end": str(to_date) if to_date else None,
            "unmatched_names": [],
            "totals": {},
        }

        for row in rows[header_idx + 1:]:
            first_name = _get_palms_col(row, col_map, "First Name", "First Name ").strip()
            last_name = _get_palms_col(row, col_map, "Last Name", "Last Name ").strip()

            if not first_name and not last_name:
                summary["skipped"] += 1
                continue

            full_name = f"{first_name} {last_name}".strip()

            # Skip non-data rows
            if full_name.lower() in ("first name", "visitors", "bni", "total", ""):
                if full_name.lower() == "total":
                    # Capture totals
                    summary["totals"] = {
                        "present": safe_int(_get_palms_col(row, col_map, "P")),
                        "absent": safe_int(_get_palms_col(row, col_map, "A")),
                        "late": safe_int(_get_palms_col(row, col_map, "L")),
                        "medical": safe_int(_get_palms_col(row, col_map, "M")),
                        "substitute": safe_int(_get_palms_col(row, col_map, "S")),
                        "rgi": safe_int(_get_palms_col(row, col_map, "RGI")),
                        "rgo": safe_int(_get_palms_col(row, col_map, "RGO")),
                        "rri": safe_int(_get_palms_col(row, col_map, "RRI")),
                        "rro": safe_int(_get_palms_col(row, col_map, "RRO")),
                        "visitors": safe_int(_get_palms_col(row, col_map, "V")),
                        "one_to_ones": safe_int(_get_palms_col(row, col_map, "1-2-1", "1to1", "121")),
                        "tyfcb": safe_float(_get_palms_col(row, col_map, "TYFCB")),
                        "ceu": safe_int(_get_palms_col(row, col_map, "CEU")),
                    }
                summary["skipped"] += 1
                continue

            # Verify this is a data row (P column should be numeric)
            p_val = _get_palms_col(row, col_map, "P")
            if not p_val.replace(".", "").replace("-", "").isdigit():
                summary["skipped"] += 1
                continue

            summary["processed"] += 1

            # Match member
            member = match_member_by_name(db, first_name, last_name, chapter_id)
            if not member:
                summary["unmatched"] += 1
                summary["unmatched_names"].append(full_name)
                continue

            # Parse all fields using header-based mapping
            rgi = safe_int(_get_palms_col(row, col_map, "RGI"))
            rgo = safe_int(_get_palms_col(row, col_map, "RGO"))
            rri = safe_int(_get_palms_col(row, col_map, "RRI"))
            rro = safe_int(_get_palms_col(row, col_map, "RRO"))
            referrals_given_total = rgi + rgo
            referrals_received_total = rri + rro

            # Check for existing snapshot (dedup by member + period)
            existing = None
            if from_date and to_date:
                existing = db.query(PalmsSnapshot).filter(
                    PalmsSnapshot.member_id == member.id,
                    PalmsSnapshot.period_start == from_date,
                    PalmsSnapshot.period_end == to_date,
                ).first()

            data = {
                "present_count": safe_int(_get_palms_col(row, col_map, "P")),
                "absent_count": safe_int(_get_palms_col(row, col_map, "A")),
                "late_count": safe_int(_get_palms_col(row, col_map, "L")),
                "medical_count": safe_int(_get_palms_col(row, col_map, "M")),
                "substitute_count": safe_int(_get_palms_col(row, col_map, "S")),
                "rgi": rgi,
                "rgo": rgo,
                "rri": rri,
                "rro": rro,
                "referrals_given_total": referrals_given_total,
                "referrals_received_total": referrals_received_total,
                "referrals_given": referrals_given_total,
                "referrals_received": referrals_received_total,
                "referrals_outside": rgo + rro,
                "visitors_brought": safe_int(_get_palms_col(row, col_map, "V")),
                "one_to_ones": safe_int(_get_palms_col(row, col_map, "1-2-1", "1to1", "121")),
                "tyfcb_amount": safe_float(_get_palms_col(row, col_map, "TYFCB")),
                "ceu_credits": safe_int(_get_palms_col(row, col_map, "CEU")),
                "raw_data": {
                    "report_name": full_name,
                    "rgi": rgi, "rgo": rgo, "rri": rri, "rro": rro,
                },
            }

            if existing:
                for key, val in data.items():
                    setattr(existing, key, val)
                summary["updated"] += 1
            else:
                snapshot = PalmsSnapshot(
                    chapter_id=chapter_id,
                    member_id=member.id,
                    period_label=f"{from_date} to {to_date}" if from_date else "Current",
                    period_start=from_date or (datetime.utcnow().date() - timedelta(days=180)),
                    period_end=to_date or datetime.utcnow().date(),
                    **data,
                )
                db.add(snapshot)

            summary["matched"] += 1

        db.commit()

        # Clean up for JSON response
        if not summary["unmatched_names"]:
            del summary["unmatched_names"]

        return summary
    except Exception as e:
        raise ValueError(f"Gagal memproses PALMS: {str(e)}")


# ═══════════════════════════════════════════════════════════════════
# VISITOR PARSERS — BOTH REPORT TYPES WITH DEDUP
# ═══════════════════════════════════════════════════════════════════

def process_visitor_excel(file_content: bytes, chapter_id, db: Session):
    """
    Auto-detect and parse either:
    - Chapter Visitor Report (has "Visit Date", "Invited By", "Type")
    - Prospective Visitor Registration Report (has "Specialty", "Product/Service Description")

    Uses dedup: same name + same visit date = update, not duplicate.
    Tracks visit history in visit_data JSONB.
    """
    try:
        rows = parse_bni_xml(file_content)

        # Detect which report type by looking at header row content
        report_type = None
        header_idx = -1
        col_map = {}

        for i, row in enumerate(rows):
            row_text = " ".join(row).lower()
            if "specialty" in row_text and "product/service" in row_text:
                report_type = "registration"
                header_idx = i
                col_map = {c.strip(): j for j, c in enumerate(row) if c.strip()}
                break
            elif "visit date" in row_text and "invited by" in row_text:
                report_type = "visitor"
                header_idx = i
                col_map = {c.strip(): j for j, c in enumerate(row) if c.strip()}
                break

        if report_type is None:
            # Fallback: try to detect from column count
            for i, row in enumerate(rows):
                if "First Name" in row:
                    header_idx = i
                    col_map = {c.strip(): j for j, c in enumerate(row) if c.strip()}
                    if len(row) > 18:
                        report_type = "registration"
                    else:
                        report_type = "visitor"
                    break

        if header_idx < 0:
            raise ValueError("Cannot detect visitor report format. No header row found.")

        if report_type == "registration":
            return _process_visitor_registration(rows, header_idx, col_map, chapter_id, db)
        else:
            return _process_visitor_report(rows, header_idx, col_map, chapter_id, db)

    except Exception as e:
        raise ValueError(f"Gagal memproses Visitor: {str(e)}")


def _get_col(row: list, col_map: dict, *keys) -> str:
    """Get cell value by column name, trying multiple possible names."""
    for key in keys:
        if key in col_map:
            idx = col_map[key]
            if idx < len(row):
                return row[idx].strip()
    return ""


def _find_or_create_visitor(db: Session, chapter_id, full_name: str,
                            email: str = "") -> tuple:
    """
    Find existing visitor by name+email or create new.
    Returns (visitor, is_new).
    """
    if not full_name:
        return None, False

    # Match by email first (most reliable)
    if email:
        existing = db.query(Visitor).filter(
            Visitor.chapter_id == chapter_id,
            Visitor.visit_data["email"].astext.ilike(email),
        ).first()
        if existing:
            return existing, False

    # Match by exact name
    existing = db.query(Visitor).filter(
        Visitor.chapter_id == chapter_id,
        Visitor.full_name.ilike(full_name),
    ).first()
    if existing:
        return existing, False

    # Create new
    visitor = Visitor(
        chapter_id=chapter_id,
        full_name=full_name,
        status="visited",
        visit_data={},
        meta={},
    )
    db.add(visitor)
    return visitor, True


def _process_visitor_report(rows, header_idx, col_map, chapter_id, db):
    """
    Chapter Visitor Report columns:
    First Name | Last Name | Company | Profession | Email | Phone |
    Address Line One | Address Line Two | City | State | Postcode | Country |
    Visit Date | Invited By | Type
    """
    summary = {"processed": 0, "added": 0, "updated": 0, "skipped": 0, "errors": 0}

    for row in rows[header_idx + 1:]:
        if len(row) < 5:
            continue

        first_name = _get_col(row, col_map, "First Name")
        last_name = _get_col(row, col_map, "Last Name")
        full_name = f"{first_name} {last_name}".strip()

        if not full_name:
            summary["skipped"] += 1
            continue

        summary["processed"] += 1

        company = _get_col(row, col_map, "Company")
        profession = _get_col(row, col_map, "Profession")
        email = _get_col(row, col_map, "Email")
        phone = _get_col(row, col_map, "Phone")
        city = _get_col(row, col_map, "City")
        state = _get_col(row, col_map, "State")
        visit_date_str = _get_col(row, col_map, "Visit Date")
        invited_by_name = _get_col(row, col_map, "Invited By")
        visit_type = _get_col(row, col_map, "Type")
        address1 = _get_col(row, col_map, "Address Line One")
        address2 = _get_col(row, col_map, "Address Line Two")

        visit_date = parse_bni_date(visit_date_str)

        try:
            visitor, is_new = _find_or_create_visitor(db, chapter_id, full_name, email)
            if visitor is None:
                summary["skipped"] += 1
                continue

            # Match inviter to member
            inviter = None
            if invited_by_name:
                parts = invited_by_name.split(" ", 1)
                if len(parts) == 2:
                    inviter = match_member_by_name(db, parts[0], parts[1], chapter_id)
                if not inviter:
                    inviter = db.query(Member).filter(
                        Member.full_name.ilike(f"%{invited_by_name}%")
                    ).first()

            if inviter:
                visitor.invited_by_id = inviter.id

            # Build/update visit_data
            vd = visitor.visit_data or {}
            vd["company"] = company or vd.get("company", "")
            vd["profession"] = profession or vd.get("profession", "")
            vd["email"] = email or vd.get("email", "")
            vd["phone"] = phone or vd.get("phone", "")
            vd["city"] = city or vd.get("city", "")
            vd["state"] = state or vd.get("state", "")
            vd["address"] = f"{address1} {address2}".strip() or vd.get("address", "")

            # Track visit history in meta
            meta = visitor.meta or {}
            visits = meta.get("visits", [])

            visit_key = f"{visit_date}|{visit_type}"
            existing_keys = [f"{v.get('date')}|{v.get('type')}" for v in visits]

            if visit_key not in existing_keys:
                visits.append({
                    "date": str(visit_date) if visit_date else None,
                    "type": visit_type,
                    "invited_by": invited_by_name,
                })
                meta["visits"] = visits
                meta["visit_count"] = len(visits)
                meta["last_visit_date"] = str(visit_date) if visit_date else meta.get("last_visit_date")
                meta["last_visit_type"] = visit_type or meta.get("last_visit_type")

            # Update funnel status based on visit type
            type_priority = {
                "First Visit": 1, "Guest": 1,
                "Repeat Visitor": 2,
                "Substitute": 3,
            }
            current_priority = type_priority.get(visitor.status, 0)
            new_priority = type_priority.get(visit_type, 0)
            if new_priority > current_priority:
                visitor.status = visit_type.lower().replace(" ", "_") if visit_type else visitor.status

            visitor.visit_data = vd
            visitor.meta = meta

            if is_new:
                summary["added"] += 1
            else:
                summary["updated"] += 1

        except Exception as e:
            print(f"Visitor row error: {e}")
            summary["errors"] += 1

    db.commit()
    return summary


def _process_visitor_registration(rows, header_idx, col_map, chapter_id, db):
    """
    Prospective Visitor Registration Report columns:
    Title | First Name | Last Name | Suffix | Company Name | Profession |
    Specialty | Product/Service Description | Invited By: | Visit Date |
    Meeting Format | Phone | Mobile | Fax | Email | Address Line 1 |
    Address Line 2 | City | State/County/Province | Country | Postcode | Type
    """
    summary = {"processed": 0, "added": 0, "updated": 0, "skipped": 0, "errors": 0}

    for row in rows[header_idx + 1:]:
        if len(row) < 5:
            continue

        first_name = _get_col(row, col_map, "First Name")
        last_name = _get_col(row, col_map, "Last Name")
        full_name = f"{first_name} {last_name}".strip()

        if not full_name:
            summary["skipped"] += 1
            continue

        summary["processed"] += 1

        title = _get_col(row, col_map, "Title")
        company = _get_col(row, col_map, "Company Name", "Company")
        profession = _get_col(row, col_map, "Profession")
        specialty = _get_col(row, col_map, "Specialty")
        product_service = _get_col(row, col_map, "Product/Service Description")
        invited_by_name = _get_col(row, col_map, "Invited By:", "Invited By")
        visit_date_str = _get_col(row, col_map, "Visit Date")
        meeting_format = _get_col(row, col_map, "Meeting Format")
        phone = _get_col(row, col_map, "Phone")
        mobile = _get_col(row, col_map, "Mobile")
        email = _get_col(row, col_map, "Email")
        city = _get_col(row, col_map, "City")
        state = _get_col(row, col_map, "State / County / Province", "State")
        country = _get_col(row, col_map, "Country")
        address1 = _get_col(row, col_map, "Address Line 1", "Address Line One")
        address2 = _get_col(row, col_map, "Address Line 2", "Address Line Two")
        visit_type = _get_col(row, col_map, "Type")
        visit_date = parse_bni_date(visit_date_str)

        try:
            visitor, is_new = _find_or_create_visitor(db, chapter_id, full_name, email)
            if visitor is None:
                summary["skipped"] += 1
                continue

            # Match inviter
            inviter = None
            if invited_by_name:
                parts = invited_by_name.split(" ", 1)
                if len(parts) == 2:
                    inviter = match_member_by_name(db, parts[0], parts[1], chapter_id)
                if not inviter:
                    inviter = db.query(Member).filter(
                        Member.full_name.ilike(f"%{invited_by_name}%")
                    ).first()

            if inviter:
                visitor.invited_by_id = inviter.id

            # Registration report has richer profile data
            vd = visitor.visit_data or {}
            vd["title"] = title or vd.get("title", "")
            vd["company"] = company or vd.get("company", "")
            vd["profession"] = profession or vd.get("profession", "")
            vd["specialty"] = specialty or vd.get("specialty", "")
            vd["product_service"] = product_service or vd.get("product_service", "")
            vd["email"] = email or vd.get("email", "")
            vd["phone"] = phone or mobile or vd.get("phone", "")
            vd["mobile"] = mobile or vd.get("mobile", "")
            vd["city"] = city or vd.get("city", "")
            vd["state"] = state or vd.get("state", "")
            vd["country"] = country or vd.get("country", "")
            vd["address"] = f"{address1} {address2}".strip() or vd.get("address", "")
            vd["meeting_format"] = meeting_format or vd.get("meeting_format", "")

            # Track visit history
            meta = visitor.meta or {}
            visits = meta.get("visits", [])
            visit_key = f"{visit_date}|{visit_type}"
            existing_keys = [f"{v.get('date')}|{v.get('type')}" for v in visits]

            if visit_key not in existing_keys:
                visits.append({
                    "date": str(visit_date) if visit_date else None,
                    "type": visit_type,
                    "invited_by": invited_by_name,
                    "meeting_format": meeting_format,
                })
                meta["visits"] = visits
                meta["visit_count"] = len(visits)
                meta["last_visit_date"] = str(visit_date) if visit_date else meta.get("last_visit_date")
                meta["last_visit_type"] = visit_type or meta.get("last_visit_type")

            # Status based on type
            type_map = {
                "Visitor": "visited",
                "Guest": "guest",
                "Substitute": "substitute",
                "First Visit": "first_visit",
                "Repeat Visitor": "repeat_visitor",
            }
            if visit_type in type_map:
                visitor.status = type_map[visit_type]

            visitor.visit_data = vd
            visitor.meta = meta

            if is_new:
                summary["added"] += 1
            else:
                summary["updated"] += 1

        except Exception as e:
            print(f"Visitor registration row error: {e}")
            summary["errors"] += 1

    db.commit()
    return summary


# ═══════════════════════════════════════════════════════════════════
# SOP STATUS
# ═══════════════════════════════════════════════════════════════════

def get_sop_status(db: Session):
    status_list = []
    for item in SOP_SCHEDULE:
        last_upload = db.query(ActivityLog).filter(
            ActivityLog.action == f"upload_{item['task'].lower().replace(' ', '_')}"
        ).order_by(ActivityLog.created_at.desc()).first()

        status_list.append({
            **item,
            "last_done": last_upload.created_at if last_upload else None,
            "is_overdue": _is_overdue(last_upload.created_at if last_upload else None, item["frequency"]),
        })
    return status_list


def _is_overdue(last_date, frequency):
    if not last_date:
        return True
    now = datetime.utcnow()
    if frequency == "Weekly":
        return now - last_date > timedelta(days=7)
    if frequency == "Monthly":
        return now - last_date > timedelta(days=30)
    return False
