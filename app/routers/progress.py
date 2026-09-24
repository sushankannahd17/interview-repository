import uuid

from fastapi import APIRouter, Depends

from app.dependencies import get_progress_service
from app.middleware.auth import require_any, require_student
from app.schemas.auth import TokenPayload
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.progress import ProgressCreate, ProgressResponse, ProgressUpdate
from app.services.progress_service import ProgressService

router = APIRouter(tags=["Progress"])


@router.get(
    "/study-plans/{plan_id}/progress",
    response_model=PaginatedResponse[ProgressResponse],
)
async def list_progress(
    plan_id: uuid.UUID,
    pagination: PaginationParams = Depends(),
    current_user: TokenPayload = Depends(require_any),
    service: ProgressService = Depends(get_progress_service),
) -> dict:
    return await service.list_progress(
        plan_id, pagination, current_user.user_id, current_user.role == "admin"
    )


@router.post(
    "/study-plans/{plan_id}/progress",
    response_model=ProgressResponse,
    status_code=201,
)
async def create_progress(
    plan_id: uuid.UUID,
    payload: ProgressCreate,
    current_user: TokenPayload = Depends(require_student),
    service: ProgressService = Depends(get_progress_service),
) -> ProgressResponse:
    return await service.create_progress(
        plan_id, payload, current_user.user_id, current_user.role == "admin"
    )


@router.patch("/progress/{progress_id}", response_model=ProgressResponse)
async def update_progress(
    progress_id: uuid.UUID,
    payload: ProgressUpdate,
    current_user: TokenPayload = Depends(require_student),
    service: ProgressService = Depends(get_progress_service),
) -> ProgressResponse:
    return await service.update_progress(
        progress_id, payload, current_user.user_id, current_user.role == "admin"
    )
