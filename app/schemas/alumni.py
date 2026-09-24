import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AlumniResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    graduation_year: int | None
    company_id: uuid.UUID | None
    role_at_company: str | None
    created_at: datetime
    updated_at: datetime
