import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.exceptions import EntityNotFoundError
from app.repositories.question_repository import QuestionRepository
from app.schemas.common import PaginationParams, build_paginated_response
from app.schemas.question import QuestionFilterParams, QuestionResponse


class QuestionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = QuestionRepository(session)

    async def get_question(self, id: uuid.UUID) -> QuestionResponse:
        question = await self.repo.get_by_id(id)
        if not question:
            raise EntityNotFoundError("Question", str(id))
        return QuestionResponse.model_validate(question)

    async def list_questions(
        self, filters: QuestionFilterParams, pagination: PaginationParams
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

        response_items = [QuestionResponse.model_validate(item).model_dump() for item in items]

        return build_paginated_response(
            items=response_items,
            total=total,
            page=pagination.page,
            size=pagination.size,
        )
