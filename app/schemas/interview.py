import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.enums import DifficultyEnum, InterviewStatusEnum
from app.schemas.question import QuestionResponse


class InterviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_id: uuid.UUID
    company_id: uuid.UUID
    alumni_id: uuid.UUID | None
    role: str
    interview_date: date
    difficulty: str
    status: str
    experience_text: str
    tips: str | None
    questions: list[QuestionResponse] = []
    created_at: datetime
    updated_at: datetime


class InterviewListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_id: uuid.UUID
    company_id: uuid.UUID
    role: str
    interview_date: date
    difficulty: str
    status: str
    question_count: int = 0
    created_at: datetime


class InterviewFilterParams(BaseModel):
    company_id: uuid.UUID | None = None
    role: str | None = None
    difficulty: DifficultyEnum | None = None
    status: InterviewStatusEnum | None = None
    date_from: date | None = None
    date_to: date | None = None
