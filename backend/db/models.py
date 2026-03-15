from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import async_sessionmaker
from config import settings
import uuid

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    job_preferences = relationship("JobPreference", back_populates="user", uselist=False)
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    s3_key = Column(String, nullable=True)
    raw_text = Column(Text, nullable=True)
    parsed_data = Column(JSON, nullable=True)  # skills, experience, education etc
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="resumes")


class JobPreference(Base):
    __tablename__ = "job_preferences"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    job_title = Column(String, nullable=False)
    location = Column(String, nullable=False)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    job_type = Column(String, default="full-time")  # full-time, part-time, contract
    remote_preference = Column(String, default="any")  # remote, hybrid, onsite, any
    platforms = Column(JSON, default=list)  # ["indeed", "linkedin", "glassdoor"]
    auto_apply = Column(Boolean, default=False)
    min_match_score = Column(Integer, default=60)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="job_preferences")


class JobListing(Base):
    __tablename__ = "job_listings"

    id = Column(String, primary_key=True, default=generate_uuid)
    external_id = Column(String, nullable=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=True)
    salary_range = Column(String, nullable=True)
    url = Column(String, nullable=False, unique=True)
    platform = Column(String, nullable=False)  # indeed, linkedin, glassdoor
    posted_date = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    requirements = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    discovered_at = Column(DateTime(timezone=True), server_default=func.now())

    applications = relationship("Application", back_populates="job")


class Application(Base):
    __tablename__ = "applications"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    job_id = Column(String, ForeignKey("job_listings.id"), nullable=False)
    resume_id = Column(String, ForeignKey("resumes.id"), nullable=True)

    # Match analysis
    match_score = Column(Float, nullable=True)
    matching_skills = Column(JSON, default=list)
    skill_gaps = Column(JSON, default=list)
    skill_gap_coaching = Column(Text, nullable=True)  # AI coaching on gaps
    recommended_keywords = Column(JSON, default=list)
    tailored_summary = Column(Text, nullable=True)

    # Application content
    cover_letter = Column(Text, nullable=True)
    custom_answers = Column(JSON, default=dict)

    # Status tracking
    status = Column(String, default="discovered")
    # discovered → matched → cover_letter_ready → pending_review → applying → submitted → confirmed → rejected
    confirmation_number = Column(String, nullable=True)
    confirmation_message = Column(Text, nullable=True)

    # Agent metadata
    agent_session_id = Column(String, nullable=True)
    video_recording_path = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    requires_human = Column(Boolean, default=False)  # CAPTCHA escalation flag
    human_review_requested = Column(Boolean, default=False)

    applied_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="applications")
    job = relationship("JobListing", back_populates="applications")


# Database engine setup
engine = create_async_engine(
    settings.database_url,
    echo=settings.app_env == "development",
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
