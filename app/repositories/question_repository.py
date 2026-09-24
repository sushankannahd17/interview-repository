import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interview import InterviewExperience
from app.models.question import Question
from app.repositories.base import BaseRepository


class QuestionRepository(BaseRepository[Question]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Question)

    async def find_filtered(
        self,
        filters: dict,
        page: int,
        size: int,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[Question], int]:
        stmt = select(Question)

        if "company_id" in filters:
            stmt = stmt.join(InterviewExperience).where(
                InterviewExperience.company_id == filters["company_id"]
            )
        if "interview_experience_id" in filters:
            stmt = stmt.where(
                Question.interview_experience_id
                == filters["interview_experience_id"]
            )
        if "category" in filters:
            stmt = stmt.where(Question.category == filters["category"])
        if "difficulty" in filters:
            stmt = stmt.where(Question.difficulty == filters["difficulty"])

        sort_column = getattr(Question, sort_by, Question.created_at)
        if sort_order == "asc":
            stmt = stmt.order_by(sort_column.asc())
        else:
            stmt = stmt.order_by(sort_column.desc())

        return await self.paginate(stmt, page, size)
