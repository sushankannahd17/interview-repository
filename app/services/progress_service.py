import uuid
from datetime import datetime, timezone

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.exceptions import EntityNotFoundError, ForbiddenError
from app.models.progress import ProgressEntry
from app.models.study_plan import StudyPlan
from app.repositories.progress_repository import ProgressRepository
from app.schemas.common import PaginationParams, build_paginated_response
from app.schemas.progress import ProgressCreate, ProgressResponse, ProgressUpdate

logger = structlog.get_logger()


class ProgressService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ProgressRepository(session)

    async def _get_plan_with_ownership_check(
        self, plan_id: uuid.UUID, requesting_user_id: uuid.UUID, is_admin: bool
    ) -> StudyPlan:
        plan = await self.session.get(StudyPlan, plan_id)
        if not plan:
            raise EntityNotFoundError("StudyPlan", str(plan_id))
        if not is_admin and plan.student_id != requesting_user_id:
            raise ForbiddenError("You can only manage progress on your own study plans")
        return plan

    async def create_progress(
        self,
        plan_id: uuid.UUID,
        payload: ProgressCreate,
        requesting_user_id: uuid.UUID,
        is_admin: bool,
    ) -> ProgressResponse:
        await self._get_plan_with_ownership_check(
            plan_id, requesting_user_id, is_admin
        )

        status_value = payload.status.value if hasattr(payload.status, "value") else payload.status

        entry = ProgressEntry(
            study_plan_id=plan_id,
            topic=payload.topic,
            status=status_value,
            notes=payload.notes,
            completed_at=datetime.now(timezone.utc)
            if status_value == "COMPLETED"
            else None,
        )

        created = await self.repo.create(entry)
        await self.session.commit()
        return ProgressResponse.model_validate(created)

    async def update_progress(
        self,
        progress_id: uuid.UUID,
        payload: ProgressUpdate,
        requesting_user_id: uuid.UUID,
        is_admin: bool,
    ) -> ProgressResponse:
        entry = await self.repo.get_by_id(progress_id)
        if not entry:
            raise EntityNotFoundError("ProgressEntry", str(progress_id))

        await self._get_plan_with_ownership_check(
            entry.study_plan_id, requesting_user_id, is_admin
        )

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(value, "value"):
                value = value.value
            setattr(entry, field, value)

        if "status" in update_data:
            new_status = update_data["status"]
            if hasattr(new_status, "value"):
                new_status = new_status.value
            if new_status == "COMPLETED":
                entry.completed_at = datetime.now(timezone.utc)
            else:
                entry.completed_at = None

        await self.session.flush()
        await self.session.commit()
        return ProgressResponse.model_validate(entry)

    async def list_progress(
        self,
        plan_id: uuid.UUID,
        pagination: PaginationParams,
        requesting_user_id: uuid.UUID,
        is_admin: bool,
    ) -> dict:
        await self._get_plan_with_ownership_check(
            plan_id, requesting_user_id, is_admin
        )

        items, total = await self.repo.find_by_study_plan(
            study_plan_id=plan_id,
            page=pagination.page,
            size=pagination.size,
            sort_by=pagination.sort_by,
            sort_order=pagination.sort_order,
        )

        response_items = [
            ProgressResponse.model_validate(item).model_dump() for item in items
        ]

        return build_paginated_response(
            items=response_items,
            total=total,
            page=pagination.page,
            size=pagination.size,
        )
