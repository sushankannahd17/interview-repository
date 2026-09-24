import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.progress import ProgressEntry
from app.repositories.base import BaseRepository


class ProgressRepository(BaseRepository[ProgressEntry]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ProgressEntry)

    async def find_by_study_plan(
        self,
        study_plan_id: uuid.UUID,
        page: int,
        size: int,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[ProgressEntry], int]:
        stmt = select(ProgressEntry).where(ProgressEntry.study_plan_id == study_plan_id)

        sort_column = getattr(ProgressEntry, sort_by, ProgressEntry.created_at)
        if sort_order == "asc":
            stmt = stmt.order_by(sort_column.asc())
        else:
            stmt = stmt.order_by(sort_column.desc())

        return await self.paginate(stmt, page, size)

    async def get_summary(self, study_plan_id: uuid.UUID) -> dict[str, int]:
        stmt = (
            select(ProgressEntry.status, func.count())
            .where(ProgressEntry.study_plan_id == study_plan_id)
            .group_by(ProgressEntry.status)
        )
        result = await self.session.execute(stmt)
        rows = result.all()

        summary = {"NOT_STARTED": 0, "IN_PROGRESS": 0, "COMPLETED": 0}
        total = 0
        for status, count in rows:
            summary[status] = count
            total += count
        summary["total"] = total
        return summary
