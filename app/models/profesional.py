"""Modelo para la entidad Profesional."""
from typing import List, Optional
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Profesional(Base):
    """Médico veterinario adscrito a la clínica."""
    __tablename__ = "profesionales"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    documento_identidad: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    nombre_completo: Mapped[str] = mapped_column(String(150), nullable=False)
    especialidad: Mapped[str] = mapped_column(String(100), nullable=False)
    telefono: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relaciones
    citas: Mapped[List["Cita"]] = relationship(back_populates="profesional")

    def __repr__(self) -> str:
        return f"<Profesional(id={self.id}, nombre='{self.nombre_completo}', esp='{self.especialidad}')>"