"""Servicio de dominio para el registro de atención médica, prescripciones e historial clínico."""
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models import Cita, Mascota, AtencionRegistrada, PrescripcionMedica
from app.services.exceptions import ReglaNegocioError, EntidadNoEncontradaError

def registrar_atencion_medica(
    db: Session,
    cita_id: int,
    diagnostico: str,
    peso_kg: Optional[float] = None,
    temperatura: Optional[float] = None,
    notas_evolucion: Optional[str] = None,
    prescripciones: Optional[List[Dict[str, Any]]] = None
) -> AtencionRegistrada:
    """Cierra clínicamente una cita, marca su estado como 'completada' y registra diagnósticos y prescripciones."""
    cita = db.query(Cita).filter(Cita.id == cita_id).first()
    if not cita:
        raise EntidadNoEncontradaError(f"No existe ninguna cita con el ID {cita_id}.")

    if cita.estado == "cancelada":
        raise ReglaNegocioError("No se puede registrar atención para una cita cancelada.")
    if cita.estado == "inasistencia":
        raise ReglaNegocioError("No se puede registrar atención para una cita marcada como inasistencia.")
    if cita.atencion:
        raise ReglaNegocioError("Esta cita ya cuenta con una atención médica registrada.")

    # Marcar cita como completada
    cita.estado = "completada"

    atencion = AtencionRegistrada(
        cita_id=cita.id,
        peso_kg=peso_kg,
        temperatura=temperatura,
        diagnostico=diagnostico,
        notas_evolucion=notas_evolucion,
        fecha_registro=datetime.now(timezone.utc)
    )
    db.add(atencion)
    db.flush()  # Para obtener atencion.id

    if prescripciones:
        for p_data in prescripciones:
            prescripcion = PrescripcionMedica(
                atencion_id=atencion.id,
                medicamento=p_data["medicamento"],
                dosis=p_data["dosis"],
                duracion_dias=p_data["duracion_dias"],
                indicaciones=p_data.get("indicaciones")
            )
            db.add(prescripcion)

    db.commit()
    db.refresh(atencion)
    return atencion

def obtener_historial_clinico_mascota(
    db: Session,
    mascota_id: int
) -> Dict[str, Any]:
    """REGLA 4: Consulta el historial clínico completo de la mascota (accesible incluso si está fallecida)."""
    mascota = db.query(Mascota).filter(Mascota.id == mascota_id).first()
    if not mascota:
        raise EntidadNoEncontradaError(f"No existe ninguna mascota con el ID {mascota_id}.")

    # Obtener todas las atenciones asociadas a las citas de la mascota
    citas = (
        db.query(Cita)
        .filter(Cita.mascota_id == mascota_id, Cita.estado == "completada")
        .order_by(Cita.fecha_hora_inicio.desc())
        .all()
    )

    atenciones_items = []
    for c in citas:
        if c.atencion:
            atenciones_items.append({
                "id": c.atencion.id,
                "cita_id": c.id,
                "fecha_registro": c.atencion.fecha_registro,
                "peso_kg": c.atencion.peso_kg,
                "temperatura": c.atencion.temperatura,
                "diagnostico": c.atencion.diagnostico,
                "notas_evolucion": c.atencion.notas_evolucion,
                "prescripciones": [
                    {
                        "id": p.id,
                        "atencion_id": p.atencion_id,
                        "medicamento": p.medicamento,
                        "dosis": p.dosis,
                        "duracion_dias": p.duracion_dias,
                        "indicaciones": p.indicaciones
                    }
                    for p in c.atencion.prescripciones
                ]
            })

    return {
        "mascota_id": mascota.id,
        "nombre": mascota.nombre,
        "especie": mascota.especie,
        "raza": mascota.raza,
        "estado_vital": mascota.estado_vital,
        "propietario_nombre": mascota.propietario.nombre_completo,
        "total_atenciones": len(atenciones_items),
        "atenciones": atenciones_items
    }