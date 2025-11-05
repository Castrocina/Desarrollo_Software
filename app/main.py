from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

from .auth import get_password_hash
from .config import settings
from .database import Base, engine, get_session
from .models import Area, Product, User
from .routers import web

app = FastAPI(title="Sistema de Gestión de Quejas")

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie=settings.session_cookie_name,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(web.router)


@app.on_event("startup")
def startup_event() -> None:
    Base.metadata.create_all(bind=engine)
    with get_session() as session:
        if session.query(Product).count() == 0:
            for name in settings.seed_products:
                session.add(Product(nombre=name))
        if session.query(Area).count() == 0:
            for area in settings.seed_areas:
                session.add(Area(**area))
        if not session.query(User).filter(User.correo == "admin@example.com").first():
            admin = User(
                correo="admin@example.com",
                nombre="Administrador",
                role="Administrador",
                hashed_password=get_password_hash("admin123"),
            )
            session.add(admin)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
