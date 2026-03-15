"""Initial schema — users, resumes, job_preferences, job_listings, applications

Revision ID: 001_initial
Revises: 
Create Date: 2025-01-01 00:00:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users
    op.create_table(
        "users",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("email", sa.String(), nullable=False, unique=True, index=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Resumes
    op.create_table(
        "resumes",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("s3_key", sa.String(), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("parsed_data", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Job preferences
    op.create_table(
        "job_preferences",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("job_title", sa.String(), nullable=False),
        sa.Column("location", sa.String(), nullable=False),
        sa.Column("salary_min", sa.Integer(), nullable=True),
        sa.Column("salary_max", sa.Integer(), nullable=True),
        sa.Column("job_type", sa.String(), default="full-time"),
        sa.Column("remote_preference", sa.String(), default="any"),
        sa.Column("platforms", sa.JSON(), default=list),
        sa.Column("auto_apply", sa.Boolean(), default=False),
        sa.Column("min_match_score", sa.Integer(), default=60),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Job listings
    op.create_table(
        "job_listings",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("external_id", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("company", sa.String(), nullable=False),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("salary_range", sa.String(), nullable=True),
        sa.Column("url", sa.String(), nullable=False, unique=True),
        sa.Column("platform", sa.String(), nullable=False),
        sa.Column("posted_date", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("requirements", sa.JSON(), default=list),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("discovered_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Applications
    op.create_table(
        "applications",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("job_id", sa.String(), sa.ForeignKey("job_listings.id"), nullable=False),
        sa.Column("resume_id", sa.String(), sa.ForeignKey("resumes.id"), nullable=True),
        sa.Column("match_score", sa.Float(), nullable=True),
        sa.Column("matching_skills", sa.JSON(), default=list),
        sa.Column("skill_gaps", sa.JSON(), default=list),
        sa.Column("skill_gap_coaching", sa.Text(), nullable=True),
        sa.Column("recommended_keywords", sa.JSON(), default=list),
        sa.Column("tailored_summary", sa.Text(), nullable=True),
        sa.Column("cover_letter", sa.Text(), nullable=True),
        sa.Column("custom_answers", sa.JSON(), default=dict),
        sa.Column("status", sa.String(), default="discovered"),
        sa.Column("confirmation_number", sa.String(), nullable=True),
        sa.Column("confirmation_message", sa.Text(), nullable=True),
        sa.Column("agent_session_id", sa.String(), nullable=True),
        sa.Column("video_recording_path", sa.String(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("requires_human", sa.Boolean(), default=False),
        sa.Column("human_review_requested", sa.Boolean(), default=False),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("applications")
    op.drop_table("job_listings")
    op.drop_table("job_preferences")
    op.drop_table("resumes")
    op.drop_table("users")
