import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions.exceptions import EntityNotFoundError
from app.middleware.auth import require_any
from app.repositories.alumni_repository import AlumniRepository
from app.schemas.alumni import AlumniResponse
from app.schemas.auth import TokenPayload
from app.schemas.common import PaginatedResponse, PaginationParams, build_paginated_response

router = APIRouter(prefix="/alumni", tags=["Alumni"])


@router.get("", response_model=PaginatedResponse[AlumniResponse])
async def list_alumni(
    company_id: uuid.UUID | None = None,
    pagination: PaginationParams = Depends(),
    current_user: TokenPayload = Depends(require_any),
    db: AsyncSession = Depends(get_db),
) -> dict:
    repo = AlumniRepository(db)
    items, total = await repo.find_all(
        company_id=company_id,
        page=pagination.page,
        size=pagination.size,
        sort_by=pagination.sort_by,
        sort_order=pagination.sort_order,
    )
    response_items = [
        AlumniResponse.model_validate(item).model_dump() for item in items
    ]
    return build_paginated_response(
        items=response_items,
        total=total,
        page=pagination.page,
        size=pagination.size,
    )


@router.get("/{alumni_id}", response_model=AlumniResponse)
async def get_alumni(
    alumni_id: uuid.UUID,
    current_user: TokenPayload = Depends(require_any),
    db: AsyncSession = Depends(get_db),
) -> AlumniResponse:
    repo = AlumniRepository(db)
    alumni = await repo.get_by_id(alumni_id)
    if not alumni:
        raise EntityNotFoundError("Alumni", str(alumni_id))
    return AlumniResponse.model_validate(alumni)
