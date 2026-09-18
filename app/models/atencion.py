"""Modelo para la entidad AtencionRegistrada."""
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class AtencionRegistrada(Base):
    """Cierre clínico, diagnóstico y notas médicas tras una cita efectuada."""
    __tablename__ = "atenciones_registradas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cita_id: Mapped[int] = mapped_column(
        ForeignKey("citas.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    peso_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    temperatura: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    diagnostico: Mapped[str] = mapped_column(Text, nullable=False)
    notas_evolucion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones
    cita: Mapped["Cita"] = relationship(back_populates="atencion")
    prescripciones: Mapped[List["PrescripcionMedica"]] = relationship(
        back_populates="atencion",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<AtencionRegistrada(id={self.id}, cita_id={self.cita_id}, diag='{self.diagnostico[:30]}...')>"