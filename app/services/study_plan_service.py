import uuid

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.exceptions import EntityNotFoundError, ForbiddenError
from app.models.company import Company
from app.models.study_plan import StudyPlan
from app.repositories.progress_repository import ProgressRepository
from app.repositories.study_plan_repository import StudyPlanRepository
from app.schemas.common import PaginationParams, build_paginated_response
from app.schemas.study_plan import (
    ProgressSummary,
    StudyPlanCreate,
    StudyPlanResponse,
    StudyPlanUpdate,
)

logger = structlog.get_logger()


class StudyPlanService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = StudyPlanRepository(session)
        self.progress_repo = ProgressRepository(session)

    async def create_study_plan(
        self, payload: StudyPlanCreate, student_id: uuid.UUID
    ) -> StudyPlanResponse:
        if payload.target_company_id:
            company = await self.session.get(Company, payload.target_company_id)
            if not company:
                raise EntityNotFoundError("Company", str(payload.target_company_id))

        plan = StudyPlan(
            student_id=student_id,
            title=payload.title,
            description=payload.description,
            target_company_id=payload.target_company_id,
            target_role=payload.target_role,
            start_date=payload.start_date,
            target_date=payload.target_date,
        )

        created = await self.repo.create(plan)
        await self.session.commit()

        response = StudyPlanResponse.model_validate(created)
        response.progress_summary = ProgressSummary()
        return response

    async def get_study_plan(
        self, id: uuid.UUID, requesting_user_id: uuid.UUID, is_admin: bool
    ) -> StudyPlanResponse:
        plan = await self.repo.get_with_progress(id)
        if not plan:
            raise EntityNotFoundError("StudyPlan", str(id))

        if not is_admin and plan.student_id != requesting_user_id:
            raise ForbiddenError("You can only view your own study plans")

        summary_data = await self.progress_repo.get_summary(id)
        response = StudyPlanResponse.model_validate(plan)
        response.progress_summary = ProgressSummary(
            not_started=summary_data.get("NOT_STARTED", 0),
            in_progress=summary_data.get("IN_PROGRESS", 0),
            completed=summary_data.get("COMPLETED", 0),
            total=summary_data.get("total", 0),
        )
        return response

    async def list_study_plans(
        self,
        student_id: uuid.UUID | None,
        pagination: PaginationParams,
    ) -> dict:
        items, total = await self.repo.find_by_student(
            student_id=student_id,
            page=pagination.page,
            size=pagination.size,
            sort_by=pagination.sort_by,
            sort_order=pagination.sort_order,
        )

        response_items = [StudyPlanResponse.model_validate(item).model_dump() for item in items]

        return build_paginated_response(
            items=response_items,
            total=total,
            page=pagination.page,
            size=pagination.size,
        )

    async def update_study_plan(
        self,
        id: uuid.UUID,
        payload: StudyPlanUpdate,
        requesting_user_id: uuid.UUID,
        is_admin: bool,
    ) -> StudyPlanResponse:
        plan = await self.repo.get_by_id(id)
        if not plan:
            raise EntityNotFoundError("StudyPlan", str(id))

        if not is_admin and plan.student_id != requesting_user_id:
            raise ForbiddenError("You can only update your own study plans")

        if payload.target_company_id:
            company = await self.session.get(Company, payload.target_company_id)
            if not company:
                raise EntityNotFoundError("Company", str(payload.target_company_id))

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(value, "value"):
                value = value.value
            setattr(plan, field, value)

        await self.session.flush()
        await self.session.commit()

        summary_data = await self.progress_repo.get_summary(id)
        response = StudyPlanResponse.model_validate(plan)
        response.progress_summary = ProgressSummary(
            not_started=summary_data.get("NOT_STARTED", 0),
            in_progress=summary_data.get("IN_PROGRESS", 0),
            completed=summary_data.get("COMPLETED", 0),
            total=summary_data.get("total", 0),
        )
        return response
