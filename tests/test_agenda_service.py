"""Pruebas unitarias de la capa de servicios y reglas de negocio innegociables."""
import pytest
from datetime import datetime, date, time, timedelta, timezone
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.models import Base, Propietario, Mascota, Profesional, TipoConsulta, Cita
from app.services.agenda_service import (
    agendar_cita,
    cancelar_cita,
    obtener_agenda_diaria,
)
from app.services.atencion_service import (
    registrar_atencion_medica,
    obtener_historial_clinico_mascota,
)
from app.services.exceptions import (
    CruceHorarioError,
    MascotaFallecidaError,
    FueraDeJornadaError,
    ReglaNegocioError,
)

@pytest.fixture
def db():
    """Inicializa una base de datos SQLite en memoria con semillas mínimas para pruebas."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()

    # Semillas de prueba
    prop = Propietario(documento_identidad="1098765432", nombre_completo="Juan Perez", telefono="3001234567")
    prof1 = Profesional(documento_identidad="VET01", nombre_completo="Dr. Carlos Mendoza", especialidad="Medicina General", telefono="3111111111")
    prof2 = Profesional(documento_identidad="VET02", nombre_completo="Dra. Laura Rios", especialidad="Cirugía Veterinaria", telefono="3222222222")
    
    tc_control = TipoConsulta(nombre="Control / Vacunación", duracion_minutos=20)
    tc_general = TipoConsulta(nombre="Consulta General", duracion_minutos=30)
    tc_cirugia = TipoConsulta(nombre="Procedimiento / Especialidad", duracion_minutos=60)

    session.add_all([prop, prof1, prof2, tc_control, tc_general, tc_cirugia])
    session.commit()

    mascota_viva = Mascota(propietario_id=prop.id, nombre="Rocky", especie="Canino", estado_vital="viva")
    mascota_muerta = Mascota(propietario_id=prop.id, nombre="Luna", especie="Felino", estado_vital="fallecida")
    session.add_all([mascota_viva, mascota_muerta])
    session.commit()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

# =========================================================================
# REGLA 2: Duración dinámica por tipo de consulta
# =========================================================================
def test_duracion_dinamica_calculada(db):
    """Verifica que la hora de fin se derive automáticamente del TipoConsulta."""
    prof = db.query(Profesional).first()
    mascota = db.query(Mascota).filter(Mascota.nombre == "Rocky").first()
    tc20 = db.query(TipoConsulta).filter(TipoConsulta.duracion_minutos == 20).first()
    tc60 = db.query(TipoConsulta).filter(TipoConsulta.duracion_minutos == 60).first()

    inicio = datetime(2026, 9, 21, 9, 0)  # Lunes 09:00

    cita20 = agendar_cita(db, prof.id, mascota.id, tc20.id, inicio, "Vacuna rabia")
    assert cita20.fecha_hora_fin == inicio + timedelta(minutes=20)

    inicio2 = datetime(2026, 9, 21, 10, 0)
    cita60 = agendar_cita(db, prof.id, mascota.id, tc60.id, inicio2, "Cirugía menor")
    assert cita60.fecha_hora_fin == inicio2 + timedelta(minutes=60)

# =========================================================================
# REGLA 1: No solapamiento temporal por profesional
# =========================================================================
def test_deteccion_cruce_horario_mismo_profesional(db):
    """Un profesional no puede tener dos citas que se crucen en el tiempo."""
    prof = db.query(Profesional).first()
    mascota = db.query(Mascota).filter(Mascota.nombre == "Rocky").first()
    tc = db.query(TipoConsulta).filter(TipoConsulta.duracion_minutos == 30).first()

    # Cita base: 09:00 a 09:30
    inicio_base = datetime(2026, 9, 21, 9, 0)
    agendar_cita(db, prof.id, mascota.id, tc.id, inicio_base, "Cita base")

    # Intento 1: Inicia adentro (09:15 a 09:45)
    with pytest.raises(CruceHorarioError):
        agendar_cita(db, prof.id, mascota.id, tc.id, datetime(2026, 9, 21, 9, 15))

    # Intento 2: Empieza antes y termina adentro (08:45 a 09:15)
    with pytest.raises(CruceHorarioError):
        agendar_cita(db, prof.id, mascota.id, tc.id, datetime(2026, 9, 21, 8, 45))

    # Intento 3: Mismo bloque exacto (09:00 a 09:30)
    with pytest.raises(CruceHorarioError):
        agendar_cita(db, prof.id, mascota.id, tc.id, inicio_base)

def test_permite_citas_simultaneas_diferentes_profesionales(db):
    """Dos profesionales distintos sí pueden atender al mismo tiempo en la clínica."""
    prof1 = db.query(Profesional).filter(Profesional.documento_identidad == "VET01").first()
    prof2 = db.query(Profesional).filter(Profesional.documento_identidad == "VET02").first()
    mascota = db.query(Mascota).filter(Mascota.nombre == "Rocky").first()
    tc = db.query(TipoConsulta).filter(TipoConsulta.duracion_minutos == 30).first()

    inicio = datetime(2026, 9, 21, 9, 0)
    cita1 = agendar_cita(db, prof1.id, mascota.id, tc.id, inicio)
    cita2 = agendar_cita(db, prof2.id, mascota.id, tc.id, inicio)

    assert cita1.id != cita2.id
    assert cita1.fecha_hora_inicio == cita2.fecha_hora_inicio

# =========================================================================
# REGLA 3: Restricción de cancelación (2 horas de antelación)
# =========================================================================
def test_cancelacion_oportuna_mas_de_2_horas(db):
    """Cancelación con >= 2 horas de antelación pasa a estado 'cancelada'."""
    prof = db.query(Profesional).first()
    mascota = db.query(Mascota).filter(Mascota.nombre == "Rocky").first()
    tc = db.query(TipoConsulta).filter(TipoConsulta.duracion_minutos == 30).first()

    inicio = datetime(2026, 9, 21, 15, 0)  # 15:00
    cita = agendar_cita(db, prof.id, mascota.id, tc.id, inicio)

    # Solicitud a las 11:00 (4 horas de anticipación)
    solicitud = datetime(2026, 9, 21, 11, 0)
    resultado = cancelar_cita(db, cita.id, fecha_hora_solicitud=solicitud)

    assert resultado["nuevo_estado"] == "cancelada"
    assert resultado["horas_anticipacion"] == 4.0
    assert cita.estado == "cancelada"

def test_cancelacion_tardia_pasa_a_inasistencia(db):
    """Cancelación con < 2 horas de antelación pasa obligatoriamente a 'inasistencia'."""
    prof = db.query(Profesional).first()
    mascota = db.query(Mascota).filter(Mascota.nombre == "Rocky").first()
    tc = db.query(TipoConsulta).filter(TipoConsulta.duracion_minutos == 30).first()

    inicio = datetime(2026, 9, 21, 15, 0)  # 15:00
    cita = agendar_cita(db, prof.id, mascota.id, tc.id, inicio)

    # Solicitud a las 14:15 (solo 45 minutos de anticipación)
    solicitud = datetime(2026, 9, 21, 14, 15)
    resultado = cancelar_cita(db, cita.id, fecha_hora_solicitud=solicitud)

    assert resultado["nuevo_estado"] == "inasistencia"
    assert resultado["horas_anticipacion"] == 0.75
    assert cita.estado == "inasistencia"

# =========================================================================
# REGLA 4: Estado vital de mascota (fallecida)
# =========================================================================
def test_bloqueo_agendamiento_mascota_fallecida(db):
    """Una mascota con estado 'fallecida' no admite citas nuevas."""
    prof = db.query(Profesional).first()
    mascota_muerta = db.query(Mascota).filter(Mascota.nombre == "Luna").first()
    tc = db.query(TipoConsulta).first()

    with pytest.raises(MascotaFallecidaError):
        agendar_cita(db, prof.id, mascota_muerta.id, tc.id, datetime(2026, 9, 21, 11, 0))

def test_historial_consultable_mascota_fallecida(db):
    """El historial clínico de una mascota fallecida debe mantenerse completamente accesible."""
    prof = db.query(Profesional).first()
    mascota_muerta = db.query(Mascota).filter(Mascota.nombre == "Luna").first()
    tc = db.query(TipoConsulta).first()

    # Insertamos una cita y atención pasada simulada
    cita_pasada = Cita(
        profesional_id=prof.id,
        mascota_id=mascota_muerta.id,
        tipo_consulta_id=tc.id,
        fecha_hora_inicio=datetime(2025, 1, 10, 10, 0),
        fecha_hora_fin=datetime(2025, 1, 10, 10, 30),
        estado="programada"
    )
    db.add(cita_pasada)
    db.commit()

    atencion = registrar_atencion_medica(
        db=db,
        cita_id=cita_pasada.id,
        diagnostico="Insuficiencia renal crónica avanzada",
        peso_kg=3.8,
        temperatura=38.2,
        prescripciones=[
            {"medicamento": "Fluidoterapia Ringer", "dosis": "100ml SC diario", "duracion_dias": 5}
        ]
    )

    historial = obtener_historial_clinico_mascota(db, mascota_muerta.id)
    assert historial["mascota_id"] == mascota_muerta.id
    assert historial["estado_vital"] == "fallecida"
    assert historial["total_atenciones"] == 1
    assert historial["atenciones"][0]["diagnostico"] == "Insuficiencia renal crónica avanzada"
    assert len(historial["atenciones"][0]["prescripciones"]) == 1

# =========================================================================
# CONSULTA OBLIGATORIA: Algoritmo de agenda diaria y cálculo de espacios libres
# =========================================================================
def test_algoritmo_agenda_diaria_calculo_espacios_libres(db):
    """Valida que los intervalos libres de 08:00 a 18:00 se calculen matemáticamente exactos."""
    prof = db.query(Profesional).first()
    mascota = db.query(Mascota).filter(Mascota.nombre == "Rocky").first()
    tc_general = db.query(TipoConsulta).filter(TipoConsulta.duracion_minutos == 30).first()
    tc_cirugia = db.query(TipoConsulta).filter(TipoConsulta.duracion_minutos == 60).first()

    dia_agenda = date(2026, 9, 22)

    # 1. Cita: 09:00 a 09:30 (30 min)
    agendar_cita(db, prof.id, mascota.id, tc_general.id, datetime.combine(dia_agenda, time(9, 0)))

    # 2. Cita: 11:00 a 12:00 (60 min)
    agendar_cita(db, prof.id, mascota.id, tc_cirugia.id, datetime.combine(dia_agenda, time(11, 0)))

    # 3. Cita: 15:00 a 15:30 (30 min)
    agendar_cita(db, prof.id, mascota.id, tc_general.id, datetime.combine(dia_agenda, time(15, 0)))

    agenda = obtener_agenda_diaria(db, prof.id, dia_agenda)

    # Verificaciones de totales (Jornada: 600 minutos)
    assert len(agenda["citas_programadas"]) == 3
    assert agenda["minutos_ocupados"] == 120  # 30 + 60 + 30
    assert agenda["minutos_libres"] == 480   # 600 - 120
    assert agenda["porcentaje_ocupacion"] == 20.0

    # Espacios libres esperados:
    # Hueco 1: 08:00 - 09:00 (60 min)
    # Hueco 2: 09:30 - 11:00 (90 min)
    # Hueco 3: 12:00 - 15:00 (180 min)
    # Hueco 4: 15:30 - 18:00 (150 min)
    espacios = agenda["espacios_libres"]
    assert len(espacios) == 4
    assert espacios[0] == {"inicio": "08:00", "fin": "09:00", "duracion_minutos": 60}
    assert espacios[1] == {"inicio": "09:30", "fin": "11:00", "duracion_minutos": 90}
    assert espacios[2] == {"inicio": "12:00", "fin": "15:00", "duracion_minutos": 180}
    assert espacios[3] == {"inicio": "15:30", "fin": "18:00", "duracion_minutos": 150}