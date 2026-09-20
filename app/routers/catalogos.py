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
from app.services.exceptions import EntidadNoEncontradaError, ReglaNegocioError

router = APIRouter(prefix="/catalogos", tags=["Catálogos y Entidades Base"])

# --- Propietarios ---
@router.post("/propietarios", response_model=PropietarioResponse, status_code=status.HTTP_201_CREATED)
def crear_propietario(payload: PropietarioCreate, db: Session = Depends(get_db)):
    existente = db.query(Propietario).filter(Propietario.documento_identidad == payload.documento_identidad).first()
    if existente:
        raise ReglaNegocioError(f"Ya existe un propietario registrado con documento {payload.documento_identidad}.")
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

# --- Profesionales (Veterinarios de la clínica) ---
@router.post("/profesionales", response_model=ProfesionalResponse, status_code=status.HTTP_201_CREATED)
def crear_profesional(payload: ProfesionalCreate, db: Session = Depends(get_db)):
    existente = db.query(Profesional).filter(Profesional.documento_identidad == payload.documento_identidad).first()
    if existente:
        raise ReglaNegocioError(f"Ya existe un profesional con documento {payload.documento_identidad}.")
    prof = Profesional(**payload.model_dump())
    db.add(prof)
    db.commit()
    db.refresh(prof)
    return prof

@router.get("/profesionales", response_model=List[ProfesionalResponse])
def listar_profesionales(db: Session = Depends(get_db)):
    return db.query(Profesional).all()

# --- Tipos de Consulta ---
@router.post("/tipos-consulta", response_model=TipoConsultaResponse, status_code=status.HTTP_201_CREATED)
def crear_tipo_consulta(payload: TipoConsultaCreate, db: Session = Depends(get_db)):
    existente = db.query(TipoConsulta).filter(TipoConsulta.nombre == payload.nombre).first()
    if existente:
        raise ReglaNegocioError(f"Ya existe un tipo de consulta con nombre '{payload.nombre}'.")
    tipo = TipoConsulta(**payload.model_dump())
    db.add(tipo)
    db.commit()
    db.refresh(tipo)
    return tipo

@router.get("/tipos-consulta", response_model=List[TipoConsultaResponse])
def listar_tipos_consulta(db: Session = Depends(get_db)):
    return db.query(TipoConsulta).all()