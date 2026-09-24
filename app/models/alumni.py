from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.interview import InterviewExperience


class PlacedAlumni(TimestampMixin, Base):
    __tablename__ = "placed_alumni"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    graduation_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True
    )
    role_at_company: Mapped[str | None] = mapped_column(String(255), nullable=True)

    company: Mapped[Company | None] = relationship()
    interview_experiences: Mapped[list[InterviewExperience]] = relationship(back_populates="alumni")
