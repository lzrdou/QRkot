from datetime import datetime

from sqlalchemy import not_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation


async def invest(obj, session: AsyncSession):
    if type(obj) == CharityProject:
        project = obj
        donations = await session.execute(
            select(Donation).where(not_(Donation.fully_invested))
        )
        donations = donations.scalars().all()
        for donation in donations:
            investment_loop(project, donation)
            if project.invested_amount == project.full_amount:
                break
    else:
        donation = obj
        projects = await session.execute(
            select(CharityProject).where(not_(CharityProject.fully_invested))
        )
        projects = projects.scalars().all()
        for project in projects:
            investment_loop(project, donation)
            if donation.invested_amount == donation.full_amount:
                break
    await session.commit()
    await session.refresh(obj)


def investment_loop(project: CharityProject, donation: Donation):
    if project.full_amount - project.invested_amount >= donation.full_amount:
        donation.invested_amount = donation.full_amount
        donation.fully_invested = True
        donation.close_date = datetime.now()
        project.invested_amount += donation.full_amount
        if project.invested_amount == project.full_amount:
            project.fully_invested = True
            project.close_date = datetime.now()
    else:
        donation.invested_amount += project.full_amount - project.invested_amount
        project.invested_amount = project.full_amount
        project.fully_invested = True
        project.close_date = datetime.now()
