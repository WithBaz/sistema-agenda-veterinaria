"""Modelo para la entidad Propietario."""
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Propietario(Base):
    """Dueño o responsable legal del paciente veterinario."""
    __tablename__ = "propietarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    documento_identidad: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    nombre_completo: Mapped[str] = mapped_column(String(150), nullable=False)
    telefono: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    direccion: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relación 1:N con Mascota
    mascotas: Mapped[List["Mascota"]] = relationship(
        back_populates="propietario",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Propietario(id={self.id}, doc={self.documento_identidad}, nombre='{self.nombre_completo}')>"