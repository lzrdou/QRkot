from datetime import datetime
from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (check_description, check_full_amount,
                                check_name, check_project_before_edit,
                                check_project_exists)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charityproject import charityproject_crud
from app.models import CharityProject
from app.schemas.charityproject import (CharityProjectCreate, CharityProjectDB,
                                        CharityProjectUpdate)
from app.services.services import invest

router = APIRouter()


@router.get(
    "/",
    response_model=List[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_charity_projects(session: AsyncSession = Depends(get_async_session)):
    return await charityproject_crud.get_multi(session)


@router.post(
    "/",
    dependencies=[Depends(current_superuser)],
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
)
async def create_charity_project(
    charity_project: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session),
):
    await check_name(charity_project.name, session)
    check_description(charity_project.description)
    check_full_amount(CharityProject, charity_project.full_amount)
    new_project = await charityproject_crud.create(charity_project, session)
    new_project.create_date = datetime.now()
    await invest(new_project, session)
    return new_project


@router.delete(
    "/{project_id}",
    dependencies=[Depends(current_superuser)],
    response_model=CharityProjectDB,
)
async def remove_charity_project(
    project_id: int, session: AsyncSession = Depends(get_async_session)
):
    """Только для суперюзеров."""
    charity_project = await check_project_exists(project_id, session)
    if charity_project.invested_amount > 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST.value,
            detail="В проект были внесены средства, не подлежит удалению!",
        )
    charity_project = await charityproject_crud.remove(charity_project, session)
    return charity_project


@router.patch(
    "/{project_id}",
    dependencies=[Depends(current_superuser)],
    response_model=CharityProjectDB,
)
async def update_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров."""
    charity_project = await check_project_exists(project_id, session)
    await check_project_before_edit(charity_project, obj_in, session)
    if charity_project.invested_amount == obj_in.full_amount:
        charity_project.fully_invested = True
        charity_project.close_date = datetime.now()
    charity_project = await charityproject_crud.update(
        db_obj=charity_project, obj_in=obj_in, session=session
    )
    return charity_project
