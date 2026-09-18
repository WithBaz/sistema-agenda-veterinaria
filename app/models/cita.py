"""Modelo para la entidad Cita."""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Cita(Base):
    """Evento de agendamiento temporal de atención veterinaria."""
    __tablename__ = "citas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profesional_id: Mapped[int] = mapped_column(
        ForeignKey("profesionales.id"),
        nullable=False,
        index=True
    )
    mascota_id: Mapped[int] = mapped_column(
        ForeignKey("mascotas.id"),
        nullable=False,
        index=True
    )
    tipo_consulta_id: Mapped[int] = mapped_column(
        ForeignKey("tipos_consulta.id"),
        nullable=False
    )
    fecha_hora_inicio: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    fecha_hora_fin: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    # Estados: 'programada', 'completada', 'cancelada', 'inasistencia'
    estado: Mapped[str] = mapped_column(
        String(30),
        default="programada",
        nullable=False
    )
    motivo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relaciones
    profesional: Mapped["Profesional"] = relationship(back_populates="citas")
    mascota: Mapped["Mascota"] = relationship(back_populates="citas")
    tipo_consulta: Mapped["TipoConsulta"] = relationship(back_populates="citas")
    
    # Relación 1:1 con AtencionRegistrada
    atencion: Mapped[Optional["AtencionRegistrada"]] = relationship(
        back_populates="cita",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Cita(id={self.id}, prof_id={self.profesional_id}, pet_id={self.mascota_id}, "
            f"inicio='{self.fecha_hora_inicio}', fin='{self.fecha_hora_fin}', estado='{self.estado}')>"
        )