import uuid

from fastapi import APIRouter, Depends

from app.dependencies import get_interview_service
from app.middleware.auth import require_any
from app.schemas.auth import TokenPayload
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.interview import (
    InterviewFilterParams,
    InterviewListResponse,
    InterviewResponse,
)
from app.services.interview_service import InterviewService

router = APIRouter(prefix="/interviews", tags=["Interviews"])


@router.get("", response_model=PaginatedResponse[InterviewListResponse])
async def list_interviews(
    filters: InterviewFilterParams = Depends(),
    pagination: PaginationParams = Depends(),
    current_user: TokenPayload = Depends(require_any),
    service: InterviewService = Depends(get_interview_service),
) -> dict:
    return await service.list_interviews(filters, pagination)


@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: uuid.UUID,
    current_user: TokenPayload = Depends(require_any),
    service: InterviewService = Depends(get_interview_service),
) -> InterviewResponse:
    return await service.get_interview(interview_id)
