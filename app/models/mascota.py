"""Modelo para la entidad Mascota."""
from datetime import datetime, date, timezone
from typing import List, Optional
from sqlalchemy import String, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Mascota(Base):
    """Paciente sujeto de atención en la clínica veterinaria."""
    __tablename__ = "mascotas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    propietario_id: Mapped[int] = mapped_column(
        ForeignKey("propietarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    especie: Mapped[str] = mapped_column(String(50), nullable=False)  # Canino, Felino, etc.
    raza: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    fecha_nacimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Regla de negocio innegociable: 'viva' o 'fallecida'
    estado_vital: Mapped[str] = mapped_column(
        String(20),
        default="viva",
        nullable=False
    )
    notas_alergias: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relaciones
    propietario: Mapped["Propietario"] = relationship(back_populates="mascotas")
    citas: Mapped[List["Cita"]] = relationship(
        back_populates="mascota",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Mascota(id={self.id}, nombre='{self.nombre}', especie='{self.especie}', estado_vital='{self.estado_vital}')>"