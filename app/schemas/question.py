import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.enums import DifficultyEnum, QuestionCategoryEnum


class QuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    interview_experience_id: uuid.UUID
    question_text: str
    category: str
    difficulty: str
    expected_answer: str | None
    created_at: datetime


class QuestionDetailResponse(QuestionResponse):
    company_name: str | None = None
    role: str | None = None
    interview_date: datetime | None = None


class QuestionFilterParams(BaseModel):
    category: QuestionCategoryEnum | None = None
    difficulty: DifficultyEnum | None = None
    company_id: uuid.UUID | None = None
    interview_experience_id: uuid.UUID | None = None
