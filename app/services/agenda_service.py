"""Servicio de dominio para la gestión de citas y disponibilidad horaria.

Implementa las reglas de negocio innegociables:
1. No solapamiento temporal por profesional.
2. Cálculo de bloques dinámicos según TipoConsulta.
3. Ventana de cancelación de 2 horas (o inasistencia).
4. Restricción de citas para mascotas fallecidas.
5. Algoritmo de agenda diaria con cálculo explícito de espacios libres.
"""

from datetime import datetime, date, time, timedelta, timezone
from typing import List, Tuple, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models import Cita, Profesional, Mascota, TipoConsulta
from app.services.exceptions import (
    ReglaNegocioError,
    CruceHorarioError,
    MascotaFallecidaError,
    FueraDeJornadaError,
    EntidadNoEncontradaError
)

HORA_INICIO_JORNADA = time(8, 0)
HORA_FIN_JORNADA = time(18, 0)
TOTAL_MINUTOS_JORNADA = 600  # 10 horas de 08:00 a 18:00

def agendar_cita(
    db: Session,
    profesional_id: int,
    mascota_id: int,
    tipo_consulta_id: int,
    fecha_hora_inicio: datetime,
    motivo: Optional[str] = None
) -> Cita:
    """Agenda una cita médica verificando todas las reglas de negocio."""
    # 1. Validación de existencia de Mascota
    mascota = db.query(Mascota).filter(Mascota.id == mascota_id).first()
    if not mascota:
        raise EntidadNoEncontradaError(f"No existe ninguna mascota con el ID {mascota_id}.")

    # REGLA 4: Ninguna mascota con estado 'fallecida' puede ser agendada
    if mascota.estado_vital.lower() == "fallecida":
        raise MascotaFallecidaError(
            f"No es posible agendar citas para la mascota '{mascota.nombre}' "
            f"debido a que su estado vital es '{mascota.estado_vital}'."
        )

    # 2. Validación de existencia del Profesional
    profesional = db.query(Profesional).filter(Profesional.id == profesional_id).first()
    if not profesional:
        raise EntidadNoEncontradaError(f"No existe ningún profesional con el ID {profesional_id}.")
    if not profesional.activo:
        raise ReglaNegocioError(f"El profesional '{profesional.nombre_completo}' no se encuentra activo.")

    # 3. Validación de TipoConsulta y REGLA 2: Cálculo Dinámico del Bloque
    tipo_consulta = db.query(TipoConsulta).filter(TipoConsulta.id == tipo_consulta_id).first()
    if not tipo_consulta:
        raise EntidadNoEncontradaError(f"No existe el tipo de consulta con ID {tipo_consulta_id}.")
    if not tipo_consulta.activo:
        raise ReglaNegocioError(f"El tipo de consulta '{tipo_consulta.nombre}' no se encuentra activo.")

    # Cálculo automático e inmutable de la hora de finalización
    duracion = tipo_consulta.duracion_minutos
    fecha_hora_fin = fecha_hora_inicio + timedelta(minutes=duracion)

    # 4. Validación de Jornada Laboral (08:00 a 18:00 de Lunes a Sábado)
    if fecha_hora_inicio.weekday() == 6:  # 6 = Domingo
        raise FueraDeJornadaError("La clínica no presta servicios los días domingo.")

    hora_inicio = fecha_hora_inicio.time()
    hora_fin = fecha_hora_fin.time()

    if hora_inicio < HORA_INICIO_JORNADA or hora_fin > HORA_FIN_JORNADA or fecha_hora_fin.date() != fecha_hora_inicio.date():
        raise FueraDeJornadaError(
            f"El bloque solicitado ({hora_inicio.strftime('%H:%M')} - {hora_fin.strftime('%H:%M')}) "
            f"se encuentra fuera de la jornada laboral de atención (08:00 a 18:00)."
        )

    # REGLA 1: Validación de Cruces Temporales (No Solapamiento por Profesional)
    # Existe colisión si: inicio_existente < nuevo_fin AND fin_existente > nuevo_inicio
    cruce = db.query(Cita).filter(
        Cita.profesional_id == profesional_id,
        Cita.estado.in_(["programada", "completada"]),
        Cita.fecha_hora_inicio < fecha_hora_fin,
        Cita.fecha_hora_fin > fecha_hora_inicio
    ).first()

    if cruce:
        raise CruceHorarioError(
            f"Conflicto de horario: El profesional '{profesional.nombre_completo}' "
            f"ya tiene una cita asignada en ese bloque ({cruce.fecha_hora_inicio.strftime('%H:%M')} - "
            f"{cruce.fecha_hora_fin.strftime('%H:%M')})."
        )

    # Crear y persistir la cita
    nueva_cita = Cita(
        profesional_id=profesional_id,
        mascota_id=mascota_id,
        tipo_consulta_id=tipo_consulta_id,
        fecha_hora_inicio=fecha_hora_inicio,
        fecha_hora_fin=fecha_hora_fin,
        estado="programada",
        motivo=motivo
    )
    db.add(nueva_cita)
    db.commit()
    db.refresh(nueva_cita)
    return nueva_cita

def cancelar_cita(
    db: Session,
    cita_id: int,
    fecha_hora_solicitud: Optional[datetime] = None
) -> Dict[str, Any]:
    """Cancela una cita aplicando la REGLA 3: Límite estricto de 2 horas."""
    cita = db.query(Cita).filter(Cita.id == cita_id).first()
    if not cita:
        raise EntidadNoEncontradaError(f"No existe ninguna cita con el ID {cita_id}.")

    if cita.estado == "cancelada":
        raise ReglaNegocioError("La cita ya se encuentra en estado 'cancelada'.")
    if cita.estado == "completada":
        raise ReglaNegocioError("No se puede cancelar una cita médica que ya fue completada.")
    if cita.estado == "inasistencia":
        raise ReglaNegocioError("La cita ya fue registrada previamente como 'inasistencia'.")

    # Si no se envía el momento de la solicitud, se toma la hora actual
    if fecha_hora_solicitud is None:
        fecha_hora_solicitud = datetime.now(timezone.utc if cita.fecha_hora_inicio.tzinfo else None)
    elif cita.fecha_hora_inicio.tzinfo and not fecha_hora_solicitud.tzinfo:
        fecha_hora_solicitud = fecha_hora_solicitud.replace(tzinfo=timezone.utc)
    elif not cita.fecha_hora_inicio.tzinfo and fecha_hora_solicitud.tzinfo:
        fecha_hora_solicitud = fecha_hora_solicitud.replace(tzinfo=None)

    tiempo_restante = cita.fecha_hora_inicio - fecha_hora_solicitud
    horas_anticipacion = tiempo_restante.total_seconds() / 3600.0
    estado_anterior = cita.estado

    # REGLA 3: Si se solicita con al menos 2 horas de antelación
    if tiempo_restante >= timedelta(hours=2):
        cita.estado = "cancelada"
        mensaje = (
            f"Cancelación exitosa. La solicitud se realizó con {horas_anticipacion:.1f} horas "
            f"de anticipación (mínimo requerido: 2.0 horas)."
        )
    else:
        cita.estado = "inasistencia"
        mensaje = (
            f"Cancelación tardía. La solicitud se realizó con solo {max(0.0, horas_anticipacion):.1f} horas "
            f"de anticipación. De acuerdo a las reglas de la clínica (< 2 horas), la cita queda registrada como 'inasistencia'."
        )

    db.commit()
    db.refresh(cita)

    return {
        "cita_id": cita.id,
        "estado_anterior": estado_anterior,
        "nuevo_estado": cita.estado,
        "mensaje": mensaje,
        "horas_anticipacion": round(horas_anticipacion, 2)
    }

def obtener_agenda_diaria(
    db: Session,
    profesional_id: int,
    fecha: date
) -> Dict[str, Any]:
    """CONSULTA OBLIGATORIA: Retorna citas del día y calcula los espacios libres de 08:00 a 18:00."""
    profesional = db.query(Profesional).filter(Profesional.id == profesional_id).first()
    if not profesional:
        raise EntidadNoEncontradaError(f"No existe ningún profesional con el ID {profesional_id}.")

    inicio_jornada = datetime.combine(fecha, HORA_INICIO_JORNADA)
    fin_jornada = datetime.combine(fecha, HORA_FIN_JORNADA)

    # Citas activas del día ordenadas cronológicamente
    citas = (
        db.query(Cita)
        .filter(
            Cita.profesional_id == profesional_id,
            Cita.fecha_hora_inicio >= inicio_jornada,
            Cita.fecha_hora_fin <= fin_jornada,
            Cita.estado.in_(["programada", "completada"])
        )
        .order_by(Cita.fecha_hora_inicio.asc())
        .all()
    )

    # ALGORITMO DE CÁLCULO DE ESPACIOS LIBRES
    espacios_libres: List[Dict[str, Any]] = []
    cursor = inicio_jornada
    minutos_ocupados = 0

    citas_items = []
    for c in citas:
        # 1. Si hay un hueco entre el cursor y el inicio de la siguiente cita
        if c.fecha_hora_inicio > cursor:
            duracion_libre = int((c.fecha_hora_inicio - cursor).total_seconds() // 60)
            if duracion_libre > 0:
                espacios_libres.append({
                    "inicio": cursor.strftime("%H:%M"),
                    "fin": c.fecha_hora_inicio.strftime("%H:%M"),
                    "duracion_minutos": duracion_libre
                })

        # 2. Acumular duración ocupada
        duracion_cita = int((c.fecha_hora_fin - c.fecha_hora_inicio).total_seconds() // 60)
        minutos_ocupados += duracion_cita
        cursor = max(cursor, c.fecha_hora_fin)

        citas_items.append({
            "id": c.id,
            "mascota_id": c.mascota_id,
            "mascota_nombre": c.mascota.nombre,
            "especie": c.mascota.especie,
            "propietario_nombre": c.mascota.propietario.nombre_completo,
            "tipo_consulta_nombre": c.tipo_consulta.nombre,
            "duracion_minutos": c.tipo_consulta.duracion_minutos,
            "fecha_hora_inicio": c.fecha_hora_inicio,
            "fecha_hora_fin": c.fecha_hora_fin,
            "estado": c.estado,
            "motivo": c.motivo
        })

    # 3. Hueco restante desde la última cita hasta el cierre de la jornada (18:00)
    if cursor < fin_jornada:
        duracion_libre_final = int((fin_jornada - cursor).total_seconds() // 60)
        if duracion_libre_final > 0:
            espacios_libres.append({
                "inicio": cursor.strftime("%H:%M"),
                "fin": fin_jornada.strftime("%H:%M"),
                "duracion_minutos": duracion_libre_final
            })

    minutos_libres = max(0, TOTAL_MINUTOS_JORNADA - minutos_ocupados)
    porcentaje_ocupacion = round((minutos_ocupados / TOTAL_MINUTOS_JORNADA) * 100, 2)

    return {
        "profesional_id": profesional.id,
        "profesional_nombre": profesional.nombre_completo,
        "especialidad": profesional.especialidad,
        "fecha": fecha.strftime("%Y-%m-%d"),
        "jornada_laboral": "08:00 - 18:00",
        "citas_programadas": citas_items,
        "espacios_libres": espacios_libres,
        "minutos_ocupados": minutos_ocupados,
        "minutos_libres": minutos_libres,
        "porcentaje_ocupacion": porcentaje_ocupacion
    }