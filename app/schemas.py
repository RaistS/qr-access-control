from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class EventCreate(BaseModel):
    name: str
    date: Optional[datetime] = None


class EventRead(BaseModel):
    id: int
    name: str
    date: Optional[datetime]
    created_at: datetime

    # Pydantic v2
    model_config = ConfigDict(from_attributes=True)


class GuestCreate(BaseModel):
    name: str
    email: EmailStr
    event_id: int


class GuestRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    token: str
    event_id: int
    created_at: datetime
    sent_at: Optional[datetime]
    checked_in_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class CheckinRequest(BaseModel):
    token: str



