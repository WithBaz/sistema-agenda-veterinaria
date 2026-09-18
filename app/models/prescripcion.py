"""Modelo para la entidad PrescripcionMedica (Historial Farmacológico)."""
from typing import Optional
from sqlalchemy import String, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class PrescripcionMedica(Base):
    """Indicaciones farmacológicas y posología asociadas a la atención médica."""
    __tablename__ = "prescripciones_medicas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    atencion_id: Mapped[int] = mapped_column(
        ForeignKey("atenciones_registradas.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    medicamento: Mapped[str] = mapped_column(String(150), nullable=False)
    dosis: Mapped[str] = mapped_column(String(100), nullable=False)  # Ej. "250 mg cada 12 horas"
    duracion_dias: Mapped[int] = mapped_column(Integer, nullable=False)
    indicaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relación
    atencion: Mapped["AtencionRegistrada"] = relationship(back_populates="prescripciones")

    def __repr__(self) -> str:
        return f"<PrescripcionMedica(id={self.id}, med='{self.medicamento}', dosis='{self.dosis}')>"