import uuid

from pydantic import BaseModel


class TokenPayload(BaseModel):
    user_id: uuid.UUID
    role: str
    email: str = ""
