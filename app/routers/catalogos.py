"""Router para gestión de entidades base y catálogos (Propietarios, Mascotas, Profesionales, Tipos de Consulta)."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Propietario, Mascota, Profesional, TipoConsulta
from app.schemas.catalogos import (
    PropietarioCreate, PropietarioResponse,
    MascotaCreate, MascotaResponse,
    ProfesionalCreate, ProfesionalResponse,
    TipoConsultaCreate, TipoConsultaResponse
)
from app.services.exceptions import EntidadNoEncontradaError

router = APIRouter(prefix="/catalogos", tags=["Catálogos y Entidades Base"])

# --- Propietarios ---
@router.post("/propietarios", response_model=PropietarioResponse, status_code=status.HTTP_201_CREATED)
def crear_propietario(payload: PropietarioCreate, db: Session = Depends(get_db)):
    prop = Propietario(**payload.model_dump())
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop

@router.get("/propietarios", response_model=List[PropietarioResponse])
def listar_propietarios(db: Session = Depends(get_db)):
    return db.query(Propietario).all()

# --- Mascotas ---
@router.post("/mascotas", response_model=MascotaResponse, status_code=status.HTTP_201_CREATED)
def crear_mascota(payload: MascotaCreate, db: Session = Depends(get_db)):
    prop = db.query(Propietario).filter(Propietario.id == payload.propietario_id).first()
    if not prop:
        raise EntidadNoEncontradaError(f"No existe el propietario con ID {payload.propietario_id}.")
    mascota = Mascota(**payload.model_dump())
    db.add(mascota)
    db.commit()
    db.refresh(mascota)
    return mascota

@router.get("/mascotas", response_model=List[MascotaResponse])
def listar_mascotas(db: Session = Depends(get_db)):
    return db.query(Mascota).all()

# --- Profesionales (3 veterinarios de la clínica) ---
@router.get("/profesionales", response_model=List[ProfesionalResponse])
def listar_profesionales(db: Session = Depends(get_db)):
    return db.query(Profesional).all()

# --- Tipos de Consulta ---
@router.get("/tipos-consulta", response_model=List[TipoConsultaResponse])
def listar_tipos_consulta(db: Session = Depends(get_db)):
    return db.query(TipoConsulta).all()