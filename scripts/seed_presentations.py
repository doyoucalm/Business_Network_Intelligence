"""Create one MemberPresentation (version 1) for every active member who doesn't have one."""

import os
import sys

# Add the parent directory to the path so we can import 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import Member, MemberPresentation

db = SessionLocal()
try:
    members = db.query(Member).filter_by(membership_status="active").all()
    created = 0
    for m in members:
        existing = db.query(MemberPresentation).filter_by(member_id=m.id, version=1).first()
        if not existing:
            p = MemberPresentation(
                member_id=m.id,
                version=1,
                title=m.full_name,
                focus_product=m.classification or "",
                products_services=[],
                looking_for=[],
                product_images=[],
                canvas_type="4images",
                canvas_content={},
                is_active=True,
                rotation_order=0,
            )
            db.add(p)
            created += 1
    db.commit()
    print(f"Created {created} presentations for {len(members)} members")
finally:
    db.close()
