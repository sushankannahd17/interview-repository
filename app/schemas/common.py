import math
from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
    sort_by: str = Field(default="created_at")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total_elements: int
    total_pages: int
    page: int
    size: int
    has_next: bool
    has_previous: bool


def build_paginated_response(items: list, total: int, page: int, size: int) -> dict:
    total_pages = math.ceil(total / size) if size > 0 else 0
    return {
        "items": items,
        "total_elements": total,
        "total_pages": total_pages,
        "page": page,
        "size": size,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


class ErrorResponse(BaseModel):
    detail: str
    error_code: str
    timestamp: datetime
