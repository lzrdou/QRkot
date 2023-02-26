from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase):
    async def get_project_id_by_name(
            self, project_name: str, session: AsyncSession
    ) -> Optional[int]:
        db_project_id = await session.execute(
            select(CharityProject).where(CharityProject.name == project_name)
        )
        db_project_id = db_project_id.scalars().first()
        return db_project_id

    async def get_projects_by_completion_rate(
            self, session: AsyncSession
    ) -> Optional[CharityProject]:
        projects = await session.execute(
            select(CharityProject).where(CharityProject.fully_invested)
        )
        if projects is not None:
            projects = projects.order_by(CharityProject.create_date - CharityProject.close_date)
            projects = projects.scalars().all()
            return projects


charityproject_crud = CRUDCharityProject(CharityProject)
