from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..auth import authenticate_user, get_password_hash, get_user_by_email
from ..database import get_db
from ..ml import classify_area
from ..models import Area, Complaint, Product, User

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter()


def get_flash(request: Request) -> Optional[dict]:
    return request.session.pop("flash", None)


def set_flash(request: Request, message: str, category: str = "info") -> None:
    request.session["flash"] = {"message": message, "category": category}


@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request) -> HTMLResponse:
    flash = get_flash(request)
    return templates.TemplateResponse("login.html", {"request": request, "flash": flash})


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "flash": {"message": "Credenciales inválidas", "category": "error"}},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    request.session["user_id"] = user.id
    request.session["user_name"] = user.nombre
    return RedirectResponse(url="/queja", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/registro", response_class=HTMLResponse)
async def register_page(request: Request) -> HTMLResponse:
    flash = get_flash(request)
    return templates.TemplateResponse("register.html", {"request": request, "flash": flash})


@router.post("/registro")
async def register(
    request: Request,
    nombre: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    existing = get_user_by_email(db, email)
    if existing:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "flash": {"message": "El correo ya está registrado", "category": "error"},
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    hashed_password = get_password_hash(password)
    user = User(correo=email, nombre=nombre, hashed_password=hashed_password)
    db.add(user)
    db.flush()
    set_flash(request, "Usuario creado correctamente. Inicie sesión.", "success")
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/logout")
async def logout(request: Request) -> RedirectResponse:
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/queja", response_class=HTMLResponse)
async def complaint_form(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    user_id = request.session.get("user_id")
    if not user_id:
        set_flash(request, "Debe iniciar sesión para continuar", "error")
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    products = db.query(Product).order_by(Product.nombre).all()
    complaints = (
        db.query(Complaint)
        .filter(Complaint.owner_id == user_id)
        .order_by(Complaint.created_at.desc())
        .all()
    )
    flash = get_flash(request)
    return templates.TemplateResponse(
        "complaint_form.html",
        {
            "request": request,
            "products": products,
            "complaints": complaints,
            "flash": flash,
            "user_name": request.session.get("user_name"),
        },
    )


@router.post("/queja")
async def submit_complaint(
    request: Request,
    producto_id: int = Form(...),
    descripcion: str = Form(...),
    db: Session = Depends(get_db),
):
    user_id = request.session.get("user_id")
    if not user_id:
        set_flash(request, "Sesión expirada. Vuelva a iniciar sesión.", "error")
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    product = db.query(Product).get(producto_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Producto inválido")

    areas = db.query(Area).order_by(Area.nombre).all()
    if not areas:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No hay áreas configuradas")

    label, score = classify_area(product.nombre, descripcion, [area.nombre for area in areas])
    selected_area = next((area for area in areas if area.nombre.lower() == label.lower()), areas[0])

    complaint = Complaint(
        descripcion=descripcion,
        producto_id=product.id,
        area_id=selected_area.id,
        label=label,
        score=score,
        owner_id=user_id,
    )
    db.add(complaint)
    db.flush()

    set_flash(
        request,
        f"Queja registrada con folio {complaint.folio} y asignada a {selected_area.nombre} (confianza {score:.2f}).",
        "success",
    )
    return RedirectResponse(url="/queja", status_code=status.HTTP_303_SEE_OTHER)
