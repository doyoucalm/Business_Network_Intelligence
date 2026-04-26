"""Host rotation suggestion for Edu Moment + Core Value slots.

Round-robin among active members, deprioritizing recently-assigned hosts.
State persisted in `host_rotation_state` (one row per chapter × rotation_type).
"""
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from .models import Member, HostRotationState


COOLDOWN_WEEKS = 8


def suggest_next_host(db: Session, chapter_id, rotation_type: str) -> Optional[Member]:
    """Return the next member to host this rotation slot, or None if no eligible members."""
    state = db.query(HostRotationState).filter_by(
        chapter_id=chapter_id, rotation_type=rotation_type
    ).first()

    history_ids = []
    if state and state.history:
        history_ids = [h.get("member_id") for h in state.history[-COOLDOWN_WEEKS:] if h.get("member_id")]

    members = db.query(Member).filter_by(
        chapter_id=chapter_id, membership_status="active"
    ).order_by(Member.full_name).all()
    if not members:
        return None

    eligible = [m for m in members if str(m.id) not in history_ids]
    pool = eligible if eligible else members  # fallback when everyone has hosted recently
    return pool[0]


def record_host_assignment(db: Session, chapter_id, rotation_type: str, member_id, meeting_date: date):
    state = db.query(HostRotationState).filter_by(
        chapter_id=chapter_id, rotation_type=rotation_type
    ).first()
    entry = {"member_id": str(member_id), "date": meeting_date.isoformat()}

    if not state:
        state = HostRotationState(
            chapter_id=chapter_id,
            rotation_type=rotation_type,
            last_member_id=member_id,
            last_index=1,
            last_assigned_date=meeting_date,
            history=[entry],
        )
        db.add(state)
    else:
        history = list(state.history or [])
        history.append(entry)
        state.history = history[-52:]  # cap a year
        state.last_member_id = member_id
        state.last_index = (state.last_index or 0) + 1
        state.last_assigned_date = meeting_date
    db.commit()
