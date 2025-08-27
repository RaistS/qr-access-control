﻿# app/database.py
from sqlmodel import SQLModel, create_engine, Session
from .config import settings
from . import models as _models  # <- IMPORTA LOS MODELOS

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

def init_db() -> None:
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session







