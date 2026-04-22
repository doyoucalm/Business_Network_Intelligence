import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Date, Integer, Numeric, Text, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .database import Base

def gen_uuid():
    return uuid.uuid4()

class Chapter(Base):
    __tablename__ = "chapters"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    name = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    region = Column(String(100))
    meeting_day = Column(String(10))
    meeting_time = Column(String(10))
    venue = Column(Text)
    status = Column(String(20), default="active")
    settings = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    members = relationship("Member", back_populates="chapter")
    forms = relationship("FormTemplate", back_populates="chapter")

class Member(Base):
    __tablename__ = "members"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=True)
    phone = Column(String(20))
    classification = Column(String(150))
    company = Column(String(200))
    membership_status = Column(String(20), default="active")
    join_date = Column(Date)
    renewal_date = Column(Date)
    password_hash = Column(String(255))
    is_activated = Column(Boolean, default=False)
    is_gold_member = Column(Boolean, default=False)
    sponsored_by_member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=True)
    business_profile = Column(JSONB, default={})
    profile_completed = Column(Boolean, default=False)
    meta = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    chapter = relationship("Chapter", back_populates="members")
    roles = relationship("MemberRole", back_populates="member")

class MemberRole(Base):
    __tablename__ = "member_roles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=False)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False)
    role = Column(String(50), nullable=False)
    committee = Column(String(50))
    term_start = Column(Date)
    term_end = Column(Date)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    member = relationship("Member", back_populates="roles")

class FormTemplate(Base):
    __tablename__ = "form_templates"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False)
    name = Column(String(150), nullable=False)
    slug = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    form_type = Column(String(30), nullable=False)
    questions = Column(JSONB, default=[])
    settings = Column(JSONB, default={})
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    chapter = relationship("Chapter", back_populates="forms")

class FormResponse(Base):
    __tablename__ = "form_responses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    form_id = Column(UUID(as_uuid=True), ForeignKey("form_templates.id"), nullable=False)
    respondent_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=True)
    respondent_name = Column(String(150))
    respondent_email = Column(String(150))
    answers = Column(JSONB, default={})
    meta = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

class EduContent(Base):
    __tablename__ = "edu_contents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False)
    title = Column(String(200), nullable=False)
    slug = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    slides = Column(JSONB, default=[])
    is_published = Column(Boolean, default=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Meeting(Base):
    __tablename__ = "meetings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False)
    meeting_date = Column(Date, nullable=False)
    meeting_type = Column(String(20), default="weekly")
    current_slide_index = Column(Integer, default=0)
    status = Column(String(20), default="scheduled")
    is_locked = Column(Boolean, default=False)
    meta = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    chapter = relationship("Chapter")
    attendance = relationship("Attendance", back_populates="meeting")

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    meeting_id = Column(UUID(as_uuid=True), ForeignKey("meetings.id"), nullable=False)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=False)
    status = Column(String(20), nullable=False)
    meta = Column(JSONB, default={})
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    meeting = relationship("Meeting", back_populates="attendance")
    member = relationship("Member")

class PalmsSnapshot(Base):
    __tablename__ = "palms_snapshots"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=False)
    period_label = Column(String(50))
    period_start = Column(Date)
    period_end = Column(Date)
    present_count = Column(Integer, default=0)
    absent_count = Column(Integer, default=0)
    medical_count = Column(Integer, default=0)
    late_count = Column(Integer, default=0)
    substitute_count = Column(Integer, default=0)
    referrals_given = Column(Integer, default=0)
    referrals_received = Column(Integer, default=0)
    referrals_outside = Column(Integer, default=0)
    visitors_brought = Column(Integer, default=0)
    one_to_ones = Column(Integer, default=0)
    tyfcb_amount = Column(Numeric(15, 2), default=0)
    ceu_credits = Column(Integer, default=0)
    raw_data = Column(JSONB, default={})
    import_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    chapter = relationship("Chapter")
    member = relationship("Member")

class PowerTeam(Base):
    __tablename__ = "power_teams"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    target_customer = Column(JSONB, default={})
    member_ids = Column(JSONB, default=[])
    is_active = Column(Boolean, default=True)
    meta = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

class Referral(Base):
    __tablename__ = "referrals"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False)
    giver_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=False)
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=False)
    status = Column(String(20), default="given")
    data = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

class Visitor(Base):
    __tablename__ = "visitors"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False)
    full_name = Column(String(150), nullable=False)
    invited_by_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=True)
    status = Column(String(20), default="visited")
    visit_data = Column(JSONB, default={})
    meta = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

class Sponsorship(Base):
    __tablename__ = "sponsorships"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False)
    sponsor_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=False)
    sponsored_member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=True)
    sponsored_name = Column(String(150))
    sponsor_date = Column(Date)
    status = Column(String(20), default="active")
    raw_data = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    chapter = relationship("Chapter")
    sponsor = relationship("Member", foreign_keys=[sponsor_id])
    sponsored_member = relationship("Member", foreign_keys=[sponsored_member_id])

class DataImport(Base):
    __tablename__ = "data_imports"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False)
    source_type = Column(String(50), nullable=False)
    filename = Column(String(255))
    file_path = Column(String(500))
    raw_data = Column(JSONB, default=[])
    mapped_data = Column(JSONB, default=[])
    import_status = Column(String(20), default="pending")
    records_total = Column(Integer, default=0)
    records_imported = Column(Integer, default=0)
    records_skipped = Column(Integer, default=0)
    records_error = Column(Integer, default=0)
    error_log = Column(JSONB, default=[])
    imported_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    chapter = relationship("Chapter")

class Score(Base):
    __tablename__ = "scores"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    scope_type = Column(String(20), nullable=False)
    scope_id = Column(UUID(as_uuid=True), nullable=False)
    score_type = Column(String(50), nullable=False)
    value = Column(Numeric(10, 2))
    details = Column(JSONB, default={})
    computed_at = Column(DateTime, default=datetime.utcnow)

class ActivityLog(Base):
    __tablename__ = "activity_log"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    chapter_id = Column(UUID(as_uuid=True), nullable=True)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=True)
    action = Column(String(50), nullable=False)
    target_type = Column(String(50))
    target_id = Column(UUID(as_uuid=True))
    data = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    actor = relationship("Member")

class Announcement(Base):
    __tablename__ = "announcements"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False)
    meeting_id = Column(UUID(as_uuid=True), ForeignKey("meetings.id"), nullable=True)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    priority = Column(Integer, default=1)
    type = Column(String(30), default="general")
    start_date = Column(Date, default=datetime.utcnow().date)
    expire_date = Column(Date)
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    chapter = relationship("Chapter")
    meeting = relationship("Meeting")
    author = relationship("Member", foreign_keys=[created_by])

class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50))
    uploaded_by = Column(UUID(as_uuid=True), nullable=True)
    status = Column(String(20), default="pending")
    row_count = Column(Integer)
    parsed_data = Column(JSONB, default={})
    import_log = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

# RESTORING THE DROPPED TABLES
class ChapterContent(Base):
    __tablename__ = "chapter_content"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False)
    content_type = Column(String(50), nullable=False)
    title = Column(String(255))
    content = Column(JSONB, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ChapterTarget(Base):
    __tablename__ = "chapter_targets"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False)
    period_label = Column(String(50), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    metric = Column(String(50), nullable=False)
    target_value = Column(Numeric(15, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ReferralNeed(Base):
    __tablename__ = "referral_needs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=False)
    target_description = Column(String(255), nullable=False)
    priority = Column(Integer, default=1)
    status = Column(String(20), default="active")
    version = Column(Integer, default=1)
    fulfilled_date = Column(Date)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MemberAchievement(Base):
    __tablename__ = "member_achievements"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=False)
    achievement_type = Column(String(30), nullable=False)
    title = Column(String(150))
    description = Column(Text)
    criteria_snapshot = Column(JSONB, default={})
    achieved_at = Column(Date)
    announced_at = Column(DateTime)
    announced_meeting_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, default=datetime.utcnow)

class MemberPresentation(Base):
    __tablename__ = "member_presentations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=False)
    version = Column(Integer, nullable=False)
    title = Column(String(255))
    focus_product = Column(String(255))
    description = Column(Text)
    products_services = Column(JSONB, default=[])
    looking_for = Column(JSONB, default=[])
    product_images = Column(JSONB, default=[])
    is_active = Column(Boolean, default=True)
    rotation_order = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MeetingActivity(Base):
    __tablename__ = "meeting_activity"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    meeting_id = Column(UUID(as_uuid=True), ForeignKey("meetings.id"), nullable=False)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=False)
    referrals_given = Column(Integer, default=0)
    referrals_received = Column(Integer, default=0)
    referrals_outside = Column(Integer, default=0)
    tyfcb_amount = Column(Numeric(15, 2), default=0)
    one_to_ones = Column(Integer, default=0)
    visitors_brought = Column(Integer, default=0)
    ceu_credits = Column(Integer, default=0)
    testimonials_given = Column(Integer, default=0)
    notes = Column(Text)
    source = Column(String(30), default="manual")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CSMMeeting(Base):
    __tablename__ = "csm_meetings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False)
    date = Column(Date, nullable=False)
    location = Column(String(255))
    attendees = Column(JSONB, default=[])
    agenda = Column(JSONB, default=[])
    vp_report = Column(JSONB, default={})
    visitor_report = Column(JSONB, default={})
    mc_report = Column(JSONB, default={})
    education_report = Column(JSONB, default={})
    mentor_report = Column(JSONB, default={})
    event_report = Column(JSONB, default={})
    notes = Column(Text)
    next_meeting_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ActionItem(Base):
    __tablename__ = "action_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    csm_meeting_id = Column(UUID(as_uuid=True), ForeignKey("csm_meetings.id"), nullable=False)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False)
    description = Column(Text, nullable=False)
    assigned_to_member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"))
    assigned_to_name = Column(String(150))
    due_date = Column(Date)
    status = Column(String(20), default="open")
    completed_date = Column(Date)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MemberReview(Base):
    __tablename__ = "member_reviews"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=False)
    review_cycle = Column(Integer, nullable=False, default=1)
    scheduled_date = Column(Date)
    actual_date = Column(Date)
    pic_member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"))
    score_percentage = Column(Integer)
    keterangan = Column(Text)
    solusi = Column(Text)
    status = Column(String(20), default="scheduled")
    decision = Column(String(20))
    raw_data = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
