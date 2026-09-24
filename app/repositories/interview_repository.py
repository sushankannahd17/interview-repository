import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.interview import InterviewExperience
from app.repositories.base import BaseRepository


class InterviewRepository(BaseRepository[InterviewExperience]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, InterviewExperience)

    async def find_by_source(
        self, source_system: str, source_record_id: str
    ) -> InterviewExperience | None:
        stmt = select(InterviewExperience).where(
            InterviewExperience.source_system == source_system,
            InterviewExperience.source_record_id == source_record_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_questions(
        self, id: uuid.UUID
    ) -> InterviewExperience | None:
        stmt = (
            select(InterviewExperience)
            .options(selectinload(InterviewExperience.questions))
            .where(InterviewExperience.id == id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_filtered(
        self,
        filters: dict,
        page: int,
        size: int,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[InterviewExperience], int]:
        stmt = select(InterviewExperience)

        if "company_id" in filters:
            stmt = stmt.where(
                InterviewExperience.company_id == filters["company_id"]
            )
        if "role" in filters:
            stmt = stmt.where(InterviewExperience.role.ilike(f"%{filters['role']}%"))
        if "difficulty" in filters:
            stmt = stmt.where(
                InterviewExperience.difficulty == filters["difficulty"]
            )
        if "status" in filters:
            stmt = stmt.where(InterviewExperience.status == filters["status"])
        if "date_from" in filters:
            stmt = stmt.where(
                InterviewExperience.interview_date >= filters["date_from"]
            )
        if "date_to" in filters:
            stmt = stmt.where(
                InterviewExperience.interview_date <= filters["date_to"]
            )

        sort_column = getattr(InterviewExperience, sort_by, InterviewExperience.created_at)
        if sort_order == "asc":
            stmt = stmt.order_by(sort_column.asc())
        else:
            stmt = stmt.order_by(sort_column.desc())

        return await self.paginate(stmt, page, size)

    async def create_with_questions(
        self, interview: InterviewExperience
    ) -> InterviewExperience:
        self.session.add(interview)
        await self.session.flush()
        return interview
