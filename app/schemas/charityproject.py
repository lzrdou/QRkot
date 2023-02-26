from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from pydantic.config import Extra

from app.schemas.utils import CLOSE_TIME, CREATE_TIME


class CharityProjectBase(BaseModel):
    name: str = Field(None, min_length=1, max_length=100)
    description: str = Field(None, min_length=1)
    full_amount: int = Field(None, gt=0)


class CharityProjectCreate(CharityProjectBase):
    pass


class CharityProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1)
    full_amount: Optional[int] = Field(None, ge=1)

    class Config:
        extra = Extra.forbid


class CharityProjectDB(CharityProjectBase):
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime = Field(..., example=CREATE_TIME)
    close_date: Optional[datetime] = Field(..., example=CLOSE_TIME)

    class Config:
        orm_mode = True
