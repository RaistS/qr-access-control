from fastapi import FastAPI
from .config import settings
from .database import init_db
from .routers import health, events, guests, checkin
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title=settings.APP_NAME)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # abrir en dev
    allow_credentials=False,  # con "*" no se permiten credenciales
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(health.router)
app.include_router(events.router)
app.include_router(guests.router)
app.include_router(checkin.router)








