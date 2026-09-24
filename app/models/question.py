from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.interview import InterviewExperience


class Question(TimestampMixin, Base):
    __tablename__ = "questions"
    __table_args__ = (
        UniqueConstraint(
            "source_system", "source_record_id", name="uq_question_source"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    interview_experience_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interview_experiences.id"),
        nullable=False,
        index=True,
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
    expected_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_system: Mapped[str] = mapped_column(String(50), nullable=False)
    source_record_id: Mapped[str] = mapped_column(String(255), nullable=False)

    interview_experience: Mapped[InterviewExperience] = relationship(
        back_populates="questions"
    )
