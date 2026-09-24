import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alumni import PlacedAlumni
from app.repositories.base import BaseRepository


class AlumniRepository(BaseRepository[PlacedAlumni]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PlacedAlumni)

    async def find_all(
        self,
        company_id: uuid.UUID | None,
        page: int,
        size: int,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> tuple[list[PlacedAlumni], int]:
        stmt = select(PlacedAlumni)

        if company_id is not None:
            stmt = stmt.where(PlacedAlumni.company_id == company_id)

        sort_column = getattr(PlacedAlumni, sort_by, PlacedAlumni.name)
        if sort_order == "asc":
            stmt = stmt.order_by(sort_column.asc())
        else:
            stmt = stmt.order_by(sort_column.desc())

        return await self.paginate(stmt, page, size)
