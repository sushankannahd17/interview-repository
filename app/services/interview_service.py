import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.exceptions import EntityNotFoundError
from app.repositories.interview_repository import InterviewRepository
from app.schemas.common import PaginationParams, build_paginated_response
from app.schemas.interview import (
    InterviewFilterParams,
    InterviewListResponse,
    InterviewResponse,
)


class InterviewService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = InterviewRepository(session)

    async def get_interview(self, id: uuid.UUID) -> InterviewResponse:
        interview = await self.repo.get_with_questions(id)
        if not interview:
            raise EntityNotFoundError("Interview", str(id))
        return InterviewResponse.model_validate(interview)

    async def list_interviews(
        self, filters: InterviewFilterParams, pagination: PaginationParams
    ) -> dict:
        filter_dict = filters.model_dump(exclude_none=True)
        for key in list(filter_dict):
            val = filter_dict[key]
            if hasattr(val, "value"):
                filter_dict[key] = val.value

        items, total = await self.repo.find_filtered(
            filters=filter_dict,
            page=pagination.page,
            size=pagination.size,
            sort_by=pagination.sort_by,
            sort_order=pagination.sort_order,
        )

        response_items = []
        for item in items:
            item_dict = InterviewListResponse.model_validate(item).model_dump()
            item_dict["question_count"] = len(item.questions) if item.questions else 0
            response_items.append(item_dict)

        return build_paginated_response(
            items=response_items,
            total=total,
            page=pagination.page,
            size=pagination.size,
        )
