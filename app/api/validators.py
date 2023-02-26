from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charityproject import charityproject_crud
from app.models import CharityProject
from app.schemas.charityproject import CharityProjectUpdate


async def check_name(project_name: str, session: AsyncSession) -> None:
    if project_name is None or len(project_name) > 100:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY.value,
            detail="Создание проектов с пустым названием или с названием длиннее 100 символов запрещено.",
        )
    project_id = await charityproject_crud.get_project_id_by_name(project_name, session)
    if project_id is not None:
        raise HTTPException(
            status_code=400, detail="Проект с таким именем уже существует!"
        )


def check_description(project_description: str) -> None:
    if project_description is None:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY.value, detail="Создание проектов с пустым описанием запрещено."
        )


def check_full_amount(model, full_amount: int) -> None:
    if not full_amount or full_amount < 0:
        if model == CharityProject:
            detail = "Требуемая сумма (full_amount) проекта должна быть целочисленной и больше 0."
        else:
            detail = "Сумма пожертвования должна быть целочисленной и больше 0."
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY.value, detail=detail)


async def check_project_exists(
    project_id: int, session: AsyncSession
) -> CharityProject:
    charity_project = await charityproject_crud.get(obj_id=project_id, session=session)
    if charity_project is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND.value, detail="Проект не найден!")
    return charity_project


async def check_project_before_edit(
        project: CharityProject,
        obj_in: CharityProjectUpdate,
        session: AsyncSession

):
    if project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST.value, detail="Закрытый проект нельзя редактировать!"
        )
    if len(obj_in.dict(exclude_unset=True)) == 0:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY.value,
            detail="Название, описание и цель не могут быть пустыми!"
        )
    if obj_in.name is not None:
        await check_name(obj_in.name, session)
    if obj_in.full_amount is not None:
        if obj_in.full_amount < project.invested_amount:
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY.value,
                detail="Невозможно установить цель меньше инвестированной!",
            )
