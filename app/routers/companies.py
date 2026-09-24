import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions.exceptions import EntityNotFoundError
from app.middleware.auth import require_any
from app.repositories.company_repository import CompanyRepository
from app.schemas.auth import TokenPayload
from app.schemas.common import PaginatedResponse, PaginationParams, build_paginated_response
from app.schemas.company import CompanyResponse

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.get("", response_model=PaginatedResponse[CompanyResponse])
async def list_companies(
    pagination: PaginationParams = Depends(),
    current_user: TokenPayload = Depends(require_any),
    db: AsyncSession = Depends(get_db),
) -> dict:
    repo = CompanyRepository(db)
    items, total = await repo.find_all(
        page=pagination.page,
        size=pagination.size,
        sort_by=pagination.sort_by,
        sort_order=pagination.sort_order,
    )
    response_items = [
        CompanyResponse.model_validate(item).model_dump() for item in items
    ]
    return build_paginated_response(
        items=response_items,
        total=total,
        page=pagination.page,
        size=pagination.size,
    )


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: uuid.UUID,
    current_user: TokenPayload = Depends(require_any),
    db: AsyncSession = Depends(get_db),
) -> CompanyResponse:
    repo = CompanyRepository(db)
    company = await repo.get_by_id(company_id)
    if not company:
        raise EntityNotFoundError("Company", str(company_id))
    return CompanyResponse.model_validate(company)
