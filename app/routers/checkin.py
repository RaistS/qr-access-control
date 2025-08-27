from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select, Session
from ..models import Guest
from ..schemas import CheckinRequest
from ..deps import session_dep

router = APIRouter(prefix="/checkin", tags=["checkin"])

@router.post("/")
def do_checkin(payload: CheckinRequest, session: Session = Depends(session_dep)):
    guest = session.exec(select(Guest).where(Guest.token == payload.token)).first()
    if not guest:
        raise HTTPException(status_code=404, detail="Invalid token")

    if guest.checked_in_at is None:
        guest.checked_in_at = datetime.utcnow()
        session.add(guest)
        session.commit()
        status = "checked_in"
    else:
        status = "already_checked"

    return {
        "status": status,
        "guest_id": guest.id,
        "name": guest.name,
        "event_id": guest.event_id,
        "checked_in_at": guest.checked_in_at,
    }





