import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Date, Integer, Numeric, Text, ForeignKey
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
    config = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    members = relationship("Member", back_populates="chapter")

class Member(Base):
    __tablename__ = "members"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=True)
    phone = Column(String(20))
    bni_classification = Column(String(150))
    company_name = Column(String(200))
    membership_status = Column(String(20), default="active")
    role = Column(String(20), default="member")
    join_date = Column(Date)
    renewal_date = Column(Date)
    password_hash = Column(String(255))
    is_activated = Column(Boolean, default=False)
    business_profile = Column(JSONB, default={})
    profile_completed = Column(Boolean, default=False)
    meta = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    chapter = relationship("Chapter", back_populates="members")

class FormTemplate(Base):
    __tablename__ = "form_templates"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id"), nullable=False)
    name = Column(String(150), nullable=False)
    slug = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    form_type = Column(String(30), nullable=False)
    # form_type: business_profile, event_rsvp, payment_check, attendance, survey, custom
    questions = Column(JSONB, default=[])
    settings = Column(JSONB, default={})
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    actor_id = Column(UUID(as_uuid=True), nullable=True)
    action = Column(String(50), nullable=False)
    target_type = Column(String(50))
    target_id = Column(UUID(as_uuid=True))
    data = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
