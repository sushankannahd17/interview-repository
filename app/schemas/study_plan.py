import uuid
from datetime import date, datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.enums import StudyPlanStatusEnum


class StudyPlanCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: str | None = Field(default=None, max_length=5000)
    target_company_id: uuid.UUID | None = None
    target_role: str | None = Field(default=None, max_length=255)
    start_date: date | None = None
    target_date: date | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        if self.start_date and self.target_date and self.target_date <= self.start_date:
            raise ValueError("target_date must be after start_date")
        return self


class StudyPlanUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    target_company_id: uuid.UUID | None = None
    target_role: str | None = None
    status: StudyPlanStatusEnum | None = None
    target_date: date | None = None


class ProgressSummary(BaseModel):
    not_started: int = 0
    in_progress: int = 0
    completed: int = 0
    total: int = 0


class StudyPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_id: uuid.UUID
    title: str
    description: str | None
    target_company_id: uuid.UUID | None
    target_role: str | None
    status: str
    start_date: date | None
    target_date: date | None
    progress_summary: ProgressSummary | None = None
    created_at: datetime
    updated_at: datetime
