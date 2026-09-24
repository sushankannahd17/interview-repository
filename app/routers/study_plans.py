import uuid

from fastapi import APIRouter, Depends

from app.dependencies import get_study_plan_service
from app.middleware.auth import require_any, require_student
from app.schemas.auth import TokenPayload
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.study_plan import StudyPlanCreate, StudyPlanResponse, StudyPlanUpdate
from app.services.study_plan_service import StudyPlanService

router = APIRouter(prefix="/study-plans", tags=["Study Plans"])


@router.post("", response_model=StudyPlanResponse, status_code=201)
async def create_study_plan(
    payload: StudyPlanCreate,
    current_user: TokenPayload = Depends(require_student),
    service: StudyPlanService = Depends(get_study_plan_service),
) -> StudyPlanResponse:
    return await service.create_study_plan(payload, current_user.user_id)


@router.get("", response_model=PaginatedResponse[StudyPlanResponse])
async def list_study_plans(
    pagination: PaginationParams = Depends(),
    current_user: TokenPayload = Depends(require_any),
    service: StudyPlanService = Depends(get_study_plan_service),
) -> dict:
    student_id = None if current_user.role == "admin" else current_user.user_id
    return await service.list_study_plans(student_id, pagination)


@router.get("/{plan_id}", response_model=StudyPlanResponse)
async def get_study_plan(
    plan_id: uuid.UUID,
    current_user: TokenPayload = Depends(require_any),
    service: StudyPlanService = Depends(get_study_plan_service),
) -> StudyPlanResponse:
    return await service.get_study_plan(plan_id, current_user.user_id, current_user.role == "admin")


@router.patch("/{plan_id}", response_model=StudyPlanResponse)
async def update_study_plan(
    plan_id: uuid.UUID,
    payload: StudyPlanUpdate,
    current_user: TokenPayload = Depends(require_student),
    service: StudyPlanService = Depends(get_study_plan_service),
) -> StudyPlanResponse:
    return await service.update_study_plan(
        plan_id, payload, current_user.user_id, current_user.role == "admin"
    )
