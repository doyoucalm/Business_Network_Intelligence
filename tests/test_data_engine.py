import pytest
import os
from app.database import SessionLocal
from app.data_engine import process_roster_excel, process_palms_excel, process_visitor_excel

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

def get_chapter_id(db):
    from app.models import Chapter
    chapter = db.query(Chapter).first()
    if not chapter:
        chapter = Chapter(name="Test Chapter", city="Test City", region="Test Region")
        db.add(chapter)
        db.commit()
        db.refresh(chapter)
    return chapter.id

def test_roster_parser():
    db = SessionLocal()
    try:
        chapter_id = get_chapter_id(db)
        path = os.path.join(FIXTURE_DIR, "roster_sample.xml")
        with open(path, "rb") as f:
            data = f.read()

        result = process_roster_excel(data, chapter_id, db)

        assert "added" in result, f"Missing 'added' key: {result}"
        assert "updated" in result, f"Missing 'updated' key: {result}"
        assert "errors" in result, f"Missing 'errors' key: {result}"
        assert result["errors"] == 0, f"Roster errors: {result}"
        # We added 2 fake members
        assert result["added"] >= 1, f"Roster added should be >= 1, got {result}"
        print(f"ROSTER PASS: added={result['added']}, updated={result['updated']}, errors={result['errors']}")
    finally:
        db.rollback()
        db.close()

def test_palms_parser():
    db = SessionLocal()
    try:
        chapter_id = get_chapter_id(db)
        path = os.path.join(FIXTURE_DIR, "palms_sample.xml")
        with open(path, "rb") as f:
            data = f.read()

        result = process_palms_excel(data, chapter_id, db)

        assert "processed" in result, f"Missing 'processed' key: {result}"
        assert "matched" in result, f"Missing 'matched' key: {result}"
        assert "errors" in result, f"Missing 'errors' key: {result}"
        assert result["errors"] == 0, f"PALMS errors: {result}"
        # Should match "Lucky Surya" who exists in DB
        assert result["matched"] >= 1, f"PALMS matched should be >= 1, got {result}"
        print(f"PALMS PASS: processed={result['processed']}, matched={result['matched']}, errors={result['errors']}")
    finally:
        db.rollback()
        db.close()

def test_visitor_parser():
    db = SessionLocal()
    try:
        chapter_id = get_chapter_id(db)
        path = os.path.join(FIXTURE_DIR, "visitor_sample.xml")
        with open(path, "rb") as f:
            data = f.read()

        result = process_visitor_excel(data, chapter_id, db)

        assert "added" in result, f"Missing 'added' key: {result}"
        assert "processed" in result, f"Missing 'processed' key: {result}"
        assert "errors" in result, f"Missing 'errors' key: {result}"
        assert result["errors"] == 0, f"Visitor errors: {result}"
        assert result["added"] >= 1, f"Visitor added should be >= 1, got {result}"
        print(f"VISITOR PASS: added={result['added']}, processed={result['processed']}, errors={result['errors']}")
    finally:
        db.rollback()
        db.close()