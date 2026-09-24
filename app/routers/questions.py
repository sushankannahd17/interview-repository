import uuid

from fastapi import APIRouter, Depends

from app.dependencies import get_question_service
from app.middleware.auth import require_any
from app.schemas.auth import TokenPayload
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.question import QuestionFilterParams, QuestionResponse
from app.services.question_service import QuestionService

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.get("", response_model=PaginatedResponse[QuestionResponse])
async def list_questions(
    filters: QuestionFilterParams = Depends(),
    pagination: PaginationParams = Depends(),
    current_user: TokenPayload = Depends(require_any),
    service: QuestionService = Depends(get_question_service),
) -> dict:
    return await service.list_questions(filters, pagination)


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: uuid.UUID,
    current_user: TokenPayload = Depends(require_any),
    service: QuestionService = Depends(get_question_service),
) -> QuestionResponse:
    return await service.get_question(question_id)
