from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session

from ..models import Event
from ..schemas import EventCreate, EventRead
from ..deps import session_dep


router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=EventRead, status_code=201)
def create_event(payload: EventCreate, session: Session = Depends(session_dep)):
    try:
        if not payload.name.strip():
            raise HTTPException(status_code=400, detail="name is required")
        event = Event(name=payload.name, date=payload.date)
        session.add(event)
        session.commit()
        session.refresh(event)
        return EventRead.model_validate(event)
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"create_event error: {e}")


@router.get("/", response_model=List[EventRead])
def list_events(session: Session = Depends(session_dep)):
    try:
        events = session.exec(select(Event).order_by(Event.created_at.desc())).all()
        return [EventRead.model_validate(ev) for ev in events]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"list_events error: {e}")

