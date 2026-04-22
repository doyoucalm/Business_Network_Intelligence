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
    settings = Column(JSONB, default={}) # Reconciled with DB
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
    # Post-migration names
    classification = Column(String(150))
    company = Column(String(200))
    membership_status = Column(String(20), default="active")
    role = Column(String(20), default="member") # Legacy column, to be migrated to MemberRole
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
    is_locked = Column(Boolean, default=False)
    meta = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    meeting_id = Column(UUID(as_uuid=True), ForeignKey("meetings.id"), nullable=False)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=False)
    status = Column(String(20), nullable=False)
    meta = Column(JSONB, default={})
    recorded_at = Column(DateTime, default=datetime.utcnow)

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
