from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.utils import CLOSE_TIME, CREATE_TIME


class DonationBase(BaseModel):
    full_amount: int = Field(None, gt=0)
    comment: Optional[str] = Field(None, min_length=1)


class DonationCreate(DonationBase):
    pass


class DonationDB(DonationBase):
    id: int
    create_date: datetime = Field(..., example=CREATE_TIME)

    class Config:
        orm_mode = True


class DonationDBMult(DonationDB):
    user_id: int
    invested_amount: int
    fully_invested: bool
    close_date: Optional[datetime] = Field(..., example=CLOSE_TIME)
