from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Guest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    token: str = Field(index=True, unique=True)
    event_id: int = Field(foreign_key="event.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    checked_in_at: Optional[datetime] = None
