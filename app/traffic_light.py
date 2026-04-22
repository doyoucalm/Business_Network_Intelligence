"""
BNI Member Traffic Light Score System.
Based on BNI Accelerate scoring (verified from official screenshot).

Calculates from a 6-month PalmsSnapshot + sponsorship count.
Max score = 100. Green >= 70, Yellow >= 50, Orange >= 30, Red < 30.
"""

from sqlalchemy.orm import Session
from .models import PalmsSnapshot, Sponsorship, Member


def calculate_traffic_light(snapshot: PalmsSnapshot,
                            sponsors_count: int = 0,
                            weeks_in_period: int = 26) -> dict:
    """
    Calculate full traffic light breakdown for one member.

    Args:
        snapshot: PalmsSnapshot for the 6-month period
        sponsors_count: Number of members sponsored in this period
        weeks_in_period: Number of weeks in the period (default 26 = 6 months)

    Returns:
        {
            "total_score": 72,
            "color": "green",
            "breakdown": {
                "visitors": {"value": 3, "score": 15, "max": 25},
                "tyfcb": {"value": 18, "score": 4, "max": 5},
                "one_to_ones": {"per_week": 1.2, "score": 20, "max": 20},
                "referrals": {"per_week": 0.9, "score": 15, "max": 25},
                "sponsors": {"value": 1, "score": 5, "max": 5},
                "ceu": {"per_week": 0.8, "score": 10, "max": 10},
                "attendance": {"percentage": 92.3, "score": 5, "max": 10},
            }
        }
    """
    if not snapshot:
        return {
            "total_score": 0,
            "color": "grey",
            "breakdown": {},
        }

    # ── Calculate per-week averages ─────────────────────────
    w = max(weeks_in_period, 1)

    referrals_given_total = snapshot.referrals_given_total or (snapshot.rgi + snapshot.rgo) or 0
    ref_per_week = referrals_given_total / w

    oto_total = snapshot.one_to_ones or 0
    oto_per_week = oto_total / w

    ceu_total = snapshot.ceu_credits or 0
    ceu_per_week = ceu_total / w

    visitors = snapshot.visitors_brought or 0

    # TYFCB: scoring uses COUNT of TYFCB transactions, not amount.
    # PALMS gives amount; estimate count from ranges.
    tyfcb_amount = float(snapshot.tyfcb_amount or 0)

    if tyfcb_amount == 0:
        tyfcb_count = 0
    elif tyfcb_amount < 50_000_000:
        tyfcb_count = 1
    elif tyfcb_amount < 200_000_000:
        tyfcb_count = max(2, int(tyfcb_amount / 100_000_000))
    elif tyfcb_amount < 500_000_000:
        tyfcb_count = max(5, int(tyfcb_amount / 80_000_000))
    else:
        tyfcb_count = max(15, int(tyfcb_amount / 50_000_000))

    # Attendance
    total_meetings = (snapshot.present_count or 0) + (snapshot.absent_count or 0) + \
                     (snapshot.late_count or 0) + (snapshot.medical_count or 0) + \
                     (snapshot.substitute_count or 0)

    attended = (snapshot.present_count or 0) + (snapshot.late_count or 0) + \
               (snapshot.substitute_count or 0) + (snapshot.medical_count or 0)

    attendance_pct = (attended / total_meetings * 100) if total_meetings > 0 else 0

    # ── Score each category ─────────────────────────────────

    # 1. Visitors (per 6 months) — max 25
    if visitors >= 5:
        visitors_score = 25
    elif visitors == 4:
        visitors_score = 20
    elif visitors == 3:
        visitors_score = 15
    elif visitors == 2:
        visitors_score = 10
    elif visitors == 1:
        visitors_score = 5
    else:
        visitors_score = 0

    # 2. TYFCB (count) — max 5
    if tyfcb_count >= 30:
        tyfcb_score = 5
    elif tyfcb_count >= 15:
        tyfcb_score = 4
    elif tyfcb_count >= 5:
        tyfcb_score = 3
    elif tyfcb_count >= 2:
        tyfcb_score = 2
    elif tyfcb_count > 0:
        tyfcb_score = 1
    else:
        tyfcb_score = 0

    # 3. 1-2-1s (per week) — max 20
    if oto_per_week >= 1:
        oto_score = 20
    elif oto_per_week >= 0.75:
        oto_score = 15
    elif oto_per_week >= 0.5:
        oto_score = 10
    elif oto_per_week >= 0.25:
        oto_score = 5
    else:
        oto_score = 0

    # 4. Referrals Given (per week) — max 25
    if ref_per_week >= 1.25:
        ref_score = 25
    elif ref_per_week >= 1.0:
        ref_score = 20
    elif ref_per_week >= 0.75:
        ref_score = 15
    elif ref_per_week >= 0.50:
        ref_score = 10
    elif ref_per_week >= 0.25:
        ref_score = 5
    else:
        ref_score = 0

    # 5. Sponsors (per 6 months) — max 5
    sponsors_score = 5 if sponsors_count >= 1 else 0

    # 6. CEU (per week) — max 10
    if ceu_per_week > 0.5:
        ceu_score = 10
    elif ceu_per_week > 0:
        ceu_score = 5
    else:
        ceu_score = 0

    # 7. Attendance — max 10
    if attendance_pct >= 96:
        attendance_score = 10
    elif attendance_pct >= 88:
        attendance_score = 5
    else:
        attendance_score = 0

    # ── Total ───────────────────────────────────────────────
    total = visitors_score + tyfcb_score + oto_score + ref_score + \
            sponsors_score + ceu_score + attendance_score

    if total >= 70:
        color = "green"
    elif total >= 50:
        color = "yellow"
    elif total >= 30:
        color = "orange"
    else:
        color = "red"

    return {
        "total_score": total,
        "color": color,
        "breakdown": {
            "visitors": {"value": visitors, "score": visitors_score, "max": 25},
            "tyfcb": {"count_estimate": tyfcb_count, "amount": tyfcb_amount, "score": tyfcb_score, "max": 5},
            "one_to_ones": {"total": oto_total, "per_week": round(oto_per_week, 2), "score": oto_score, "max": 20},
            "referrals": {"total": referrals_given_total, "per_week": round(ref_per_week, 2), "score": ref_score, "max": 25},
            "sponsors": {"value": sponsors_count, "score": sponsors_score, "max": 5},
            "ceu": {"total": ceu_total, "per_week": round(ceu_per_week, 2), "score": ceu_score, "max": 10},
            "attendance": {"percentage": round(attendance_pct, 1), "attended": attended, "total": total_meetings, "score": attendance_score, "max": 10},
        },
    }


def calculate_all_traffic_lights(db: Session, chapter_id,
                                  period_start=None, period_end=None) -> list[dict]:
    """
    Calculate traffic lights for all active members in a chapter.
    Returns sorted list: red first, then orange, yellow, green.
    """
    members = db.query(Member).filter(
        Member.chapter_id == chapter_id,
        Member.membership_status == "active",
    ).order_by(Member.full_name).all()

    results = []

    for member in members:
        # Get the most recent snapshot
        q = db.query(PalmsSnapshot).filter(PalmsSnapshot.member_id == member.id)
        if period_start and period_end:
            q = q.filter(
                PalmsSnapshot.period_start == period_start,
                PalmsSnapshot.period_end == period_end,
            )
        snapshot = q.order_by(PalmsSnapshot.created_at.desc()).first()

        # Count sponsorships in period
        sponsor_q = db.query(Sponsorship).filter(Sponsorship.sponsor_id == member.id)
        if period_start:
            sponsor_q = sponsor_q.filter(Sponsorship.sponsor_date >= period_start)
        sponsors_count = sponsor_q.count()

        # Calculate weeks in period
        weeks = 26
        if snapshot and snapshot.period_start and snapshot.period_end:
            delta = snapshot.period_end - snapshot.period_start
            weeks = max(delta.days // 7, 1)

        tl = calculate_traffic_light(snapshot, sponsors_count, weeks)

        results.append({
            "member_id": str(member.id),
            "member_name": member.full_name,
            "classification": member.classification or "",
            "company": member.company or "",
            **tl,
        })

    # Sort: red first, then orange, yellow, green, grey
    color_order = {"red": 0, "orange": 1, "yellow": 2, "green": 3, "grey": 4}
    results.sort(key=lambda x: (color_order.get(x["color"], 5), -x["total_score"]))

    return results
