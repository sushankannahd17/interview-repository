import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.study_plan import StudyPlan
from app.repositories.base import BaseRepository


class StudyPlanRepository(BaseRepository[StudyPlan]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, StudyPlan)

    async def get_with_progress(self, id: uuid.UUID) -> StudyPlan | None:
        stmt = (
            select(StudyPlan)
            .options(selectinload(StudyPlan.progress_entries))
            .where(StudyPlan.id == id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_student(
        self,
        student_id: uuid.UUID | None,
        page: int,
        size: int,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[StudyPlan], int]:
        stmt = select(StudyPlan)

        if student_id is not None:
            stmt = stmt.where(StudyPlan.student_id == student_id)

        sort_column = getattr(StudyPlan, sort_by, StudyPlan.created_at)
        if sort_order == "asc":
            stmt = stmt.order_by(sort_column.asc())
        else:
            stmt = stmt.order_by(sort_column.desc())

        return await self.paginate(stmt, page, size)
