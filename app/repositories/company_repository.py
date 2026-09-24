from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.repositories.base import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Company)

    async def find_all(
        self,
        page: int,
        size: int,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> tuple[list[Company], int]:
        stmt = select(Company)

        sort_column = getattr(Company, sort_by, Company.name)
        if sort_order == "asc":
            stmt = stmt.order_by(sort_column.asc())
        else:
            stmt = stmt.order_by(sort_column.desc())

        return await self.paginate(stmt, page, size)
