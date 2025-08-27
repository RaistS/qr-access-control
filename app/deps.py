from fastapi import Depends
from sqlmodel import Session
from .database import get_session

def session_dep(session: Session = Depends(get_session)) -> Session:
    return session








