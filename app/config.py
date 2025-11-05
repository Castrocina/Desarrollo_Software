from __future__ import annotations

import os
from pathlib import Path
from typing import List

from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or `.env`."""

    database_url: str = "sqlite:///./complaints.db"
    secret_key: str = "change-me"
    session_cookie_name: str = "complaints_session"
    huggingface_token: str | None = None
    huggingface_model: str = "facebook/bart-large-mnli"
    seed_products: List[str] = [
        "Cuentas ahorro",
        "Cuenta nómina",
        "Tarjeta de crédito",
        "Crédito hipotecario",
        "Banca en línea",
    ]
    seed_areas: List[dict] = [
        {
            "nombre": "Seguridad Digital",
            "correo": "seguridad@example.com",
            "tipo_atencion": "Tecnología",
            "descripcion": "Incidentes relacionados con banca en línea y accesos.",
        },
        {
            "nombre": "Créditos Hipotecarios",
            "correo": "hipotecas@example.com",
            "tipo_atencion": "Hipotecario",
            "descripcion": "Atención a solicitudes y quejas de créditos hipotecarios.",
        },
        {
            "nombre": "Tarjetas y Pagos",
            "correo": "tarjetas@example.com",
            "tipo_atencion": "Operativa",
            "descripcion": "Problemas con tarjetas de crédito y débito.",
        },
        {
            "nombre": "Cuentas",
            "correo": "cuentas@example.com",
            "tipo_atencion": "Operativa",
            "descripcion": "Gestión de cuentas de ahorro y nómina.",
        },
        {
            "nombre": "Compensación",
            "correo": "compensacion@example.com",
            "tipo_atencion": "Operativa",
            "descripcion": "Casos especiales que requieren reembolso o compensación.",
        },
    ]

    class Config:
        env_file = ".env"
        case_sensitive = False

    @validator("database_url")
    def expand_sqlite_path(cls, value: str) -> str:
        if value.startswith("sqlite") and "///" in value and not value.startswith("sqlite:///" + os.sep):
            # ensure relative paths resolve relative to project root
            path = value.split("///", maxsplit=1)[1]
            if not Path(path).is_absolute():
                value = f"sqlite:///{Path(path).resolve()}"
        return value


settings = Settings()
