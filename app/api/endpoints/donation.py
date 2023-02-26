from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import check_full_amount
from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.donation import donation_crud
from app.models import Donation, User
from app.schemas.donation import DonationCreate, DonationDB, DonationDBMult
from app.services.services import invest

router = APIRouter()


@router.get(
    "/",
    dependencies=[Depends(current_superuser)],
    response_model=List[DonationDBMult],
    response_model_exclude_none=True,
)
async def get_all_donations(session: AsyncSession = Depends(get_async_session)):
    """Только для суперюзеров."""
    return await donation_crud.get_multi(session)


@router.post(
    "/",
    response_model=DonationDB,
    response_model_exclude_none=True,
)
async def create_donation(
    donation: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """Сделать пожертвование."""
    check_full_amount(Donation, donation.full_amount)
    new_donation = await donation_crud.create(donation, session, user)
    new_donation.create_date = datetime.now()
    await invest(new_donation, session)
    return new_donation


@router.get(
    "/my",
    response_model=List[DonationDB],
)
async def get_my_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """Получить список моих пожертвований."""
    return await donation_crud.get_by_user(user=user, session=session)
