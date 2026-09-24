import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import ProgressStatusEnum


class ProgressCreate(BaseModel):
    topic: str = Field(min_length=1, max_length=255)
    status: ProgressStatusEnum = Field(default=ProgressStatusEnum.NOT_STARTED)
    notes: str | None = Field(default=None, max_length=5000)


class ProgressUpdate(BaseModel):
    status: ProgressStatusEnum | None = None
    notes: str | None = None


class ProgressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    study_plan_id: uuid.UUID
    topic: str
    status: str
    notes: str | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime
