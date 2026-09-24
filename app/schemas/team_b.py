import uuid
from datetime import date

from pydantic import BaseModel, Field

from app.schemas.enums import DifficultyEnum, QuestionCategoryEnum


class TeamBQuestionPayload(BaseModel):
    source_id: str = Field(
        min_length=1, max_length=255, description="Team B's unique ID for this question"
    )
    question_text: str = Field(min_length=1, max_length=10000)
    category: QuestionCategoryEnum
    difficulty: DifficultyEnum
    expected_answer: str | None = Field(default=None, max_length=20000)


class TeamBInterviewPayload(BaseModel):
    source_id: str = Field(
        min_length=1,
        max_length=255,
        description="Team B's unique ID for this interview record",
    )
    student_id: uuid.UUID
    company_id: uuid.UUID
    alumni_id: uuid.UUID | None = None
    role: str = Field(min_length=1, max_length=255)
    interview_date: date
    difficulty: DifficultyEnum
    experience_text: str = Field(min_length=1, max_length=50000)
    tips: str | None = Field(default=None, max_length=10000)
    questions: list[TeamBQuestionPayload] = Field(
        min_length=1, description="At least one question is required"
    )
