import csv
from datetime import datetime
from io import StringIO
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlmodel import select, Session

from ..models import Guest, Event
from ..schemas import GuestCreate, GuestRead
from ..deps import session_dep
from ..services.qr import make_qr_png
from ..services.emailer import send_qr_email
from ..config import settings

router = APIRouter(prefix="/guests", tags=["guests"])

@router.post("/", response_model=GuestRead)
async def create_guest(payload: GuestCreate, session: Session = Depends(session_dep)):
    event = session.get(Event, payload.event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    token = uuid4().hex
    guest = Guest(name=payload.name, email=payload.email, token=token, event_id=payload.event_id)
    session.add(guest)
    session.commit()
    session.refresh(guest)

    content = token
    if settings.QR_BASE_URL:
        base = str(settings.QR_BASE_URL).rstrip("/")
        content = f"{base}/checkin?token={token}"

    png = make_qr_png(content)

    subject = f"Tu QR de acceso — {event.name}"
    body = (
        f"Hola {guest.name},\n\n"
        f"Adjuntamos tu QR para el evento '{event.name}'.\n"
        f"Guárdalo en tu teléfono y muéstralo en el acceso.\n\n"
        f"Si no puedes escanearlo, tu código es: {token}\n"
    )

    try:
        await send_qr_email(
            to_email=guest.email,
            subject=subject,
            body_text=body,
            attachment_bytes=png,
            attachment_filename=f"qr_{guest.id}.png",
        )
        guest.sent_at = datetime.utcnow()
        session.add(guest)
        session.commit()
    except Exception as e:
        print("Email error:", e)

    return guest


@router.post("/import", response_model=list[GuestRead])
async def import_guests(
    event_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(session_dep),
):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    contents = await file.read()
    reader = csv.DictReader(StringIO(contents.decode("utf-8")))

    created: list[Guest] = []
    for row in reader:
        name = row.get("name")
        email = row.get("email")
        if not name or not email:
            continue

        token = uuid4().hex
        guest = Guest(name=name, email=email, token=token, event_id=event_id)
        session.add(guest)
        session.commit()
        session.refresh(guest)

        content = token
        if settings.QR_BASE_URL:
            base = str(settings.QR_BASE_URL).rstrip("/")
            content = f"{base}/checkin?token={token}"

        png = make_qr_png(content)
        subject = f"Tu QR de acceso — {event.name}"
        body = (
            f"Hola {guest.name},\n\n"
            f"Adjuntamos tu QR para el evento '{event.name}'.\n"
            f"Guárdalo en tu teléfono y muéstralo en el acceso.\n\n"
            f"Si no puedes escanearlo, tu código es: {token}\n"
        )
        try:
            await send_qr_email(
                to_email=guest.email,
                subject=subject,
                body_text=body,
                attachment_bytes=png,
                attachment_filename=f"qr_{guest.id}.png",
            )
            guest.sent_at = datetime.utcnow()
            session.add(guest)
            session.commit()
        except Exception as e:
            print("Email error:", e)

        created.append(guest)

    return created

@router.get("/", response_model=list[GuestRead])
def list_guests(event_id: int | None = None, session: Session = Depends(session_dep)):
    query = select(Guest)
    if event_id:
        query = query.where(Guest.event_id == event_id)
    guests = session.exec(query.order_by(Guest.created_at.desc())).all()
    return guests

@router.post("/{guest_id}/resend", response_model=GuestRead)
async def resend_qr(guest_id: int, session: Session = Depends(session_dep)):
    guest = session.get(Guest, guest_id)
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    event = session.get(Event, guest.event_id)

    content = guest.token
    if settings.QR_BASE_URL:
        base = str(settings.QR_BASE_URL).rstrip("/")
        content = f"{base}/checkin?token={guest.token}"

    png = make_qr_png(content)
    subject = f"(Reenvío) Tu QR de acceso — {event.name}"
    body = f"Hola {guest.name}, reenvío de tu QR para '{event.name}'."

    await send_qr_email(
        to_email=guest.email,
        subject=subject,
        body_text=body,
        attachment_bytes=png,
        attachment_filename=f"qr_{guest.id}.png",
    )
    guest.sent_at = datetime.utcnow()
    session.add(guest)
    session.commit()
    session.refresh(guest)
    return guest

@router.get("/qr/{guest_id}.png")
def qr_png(guest_id: int, session: Session = Depends(session_dep)):
    guest = session.get(Guest, guest_id)
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")

    content = guest.token
    if settings.QR_BASE_URL:
        base = str(settings.QR_BASE_URL).rstrip("/")
        content = f"{base}/checkin?token={guest.token}"

    png = make_qr_png(content)
    return StreamingResponse(iter([png]), media_type="image/png")





