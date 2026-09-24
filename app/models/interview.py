from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.alumni import PlacedAlumni
    from app.models.company import Company
    from app.models.question import Question
    from app.models.student import Student


class InterviewExperience(TimestampMixin, Base):
    __tablename__ = "interview_experiences"
    __table_args__ = (
        UniqueConstraint("source_system", "source_record_id", name="uq_interview_source"),
        Index("ix_interview_company_difficulty", "company_id", "difficulty"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id"), nullable=False, index=True
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True
    )
    alumni_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("placed_alumni.id"), nullable=True
    )
    role: Mapped[str] = mapped_column(String(255), nullable=False)
    interview_date: Mapped[date] = mapped_column(Date, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    experience_text: Mapped[str] = mapped_column(Text, nullable=False)
    tips: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_system: Mapped[str] = mapped_column(String(50), nullable=False)
    source_record_id: Mapped[str] = mapped_column(String(255), nullable=False)

    student: Mapped[Student] = relationship(back_populates="interview_experiences")
    company: Mapped[Company] = relationship(back_populates="interview_experiences")
    alumni: Mapped[PlacedAlumni | None] = relationship(back_populates="interview_experiences")
    questions: Mapped[list[Question]] = relationship(
        back_populates="interview_experience", cascade="all, delete-orphan"
    )
