from __future__ import annotations

from datetime import datetime
from secrets import token_hex

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


def generate_folio() -> str:
    return token_hex(4).upper()


class Area(Base):
    __tablename__ = "areas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(250), unique=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    tipo_atencion = Column(String(100), nullable=False)
    correo = Column(String(250), nullable=False)

    complaints = relationship("Complaint", back_populates="area")


class Product(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(250), unique=True, nullable=False)

    complaints = relationship("Complaint", back_populates="product")


class User(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    correo = Column(String(250), unique=True, nullable=False)
    nombre = Column(String(250), nullable=False)
    role = Column(String(50), default="Cliente", nullable=False)
    hashed_password = Column(String(255), nullable=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    complaints = relationship("Complaint", back_populates="owner")


class Complaint(Base):
    __tablename__ = "reclamaciones"

    id = Column(Integer, primary_key=True, index=True)
    folio = Column(String(20), default=generate_folio, unique=True, nullable=False)
    descripcion = Column(Text, nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False)
    label = Column(String(250), nullable=False)
    score = Column(Float, nullable=False)
    owner_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    product = relationship("Product", back_populates="complaints")
    area = relationship("Area", back_populates="complaints")
    owner = relationship("User", back_populates="complaints")
