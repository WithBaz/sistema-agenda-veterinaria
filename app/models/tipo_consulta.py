"""Modelo para la entidad TipoConsulta (Catálogo de Servicios)."""
from typing import List, Optional
from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class TipoConsulta(Base):
    """Catálogo desacoplado de tipos de consulta y sus tiempos estándar."""
    __tablename__ = "tipos_consulta"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    duracion_minutos: Mapped[int] = mapped_column(Integer, nullable=False)  # Ej. 20, 30, 60
    descripcion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relaciones
    citas: Mapped[List["Cita"]] = relationship(back_populates="tipo_consulta")

    def __repr__(self) -> str:
        return f"<TipoConsulta(id={self.id}, nombre='{self.nombre}', duracion={self.duracion_minutos}min)>"