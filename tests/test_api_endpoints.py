"""Pruebas de integración End-to-End (E2E) para la API REST con FastAPI TestClient."""
import pytest
from datetime import datetime, date, time, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Propietario, Mascota, Profesional, TipoConsulta, Cita

@pytest.fixture
def client():
    """Configura un cliente de prueba con base de datos SQLite en memoria aislada y StaticPool."""
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    @event.listens_for(test_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=test_engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    # Inserción de semillas mínimas para pruebas de endpoints
    db = TestingSessionLocal()
    prop = Propietario(documento_identidad="111222333", nombre_completo="Ana Maria Gomez", telefono="3109988776")
    prof1 = Profesional(documento_identidad="VET100", nombre_completo="Dr. Fernando Reyes", especialidad="Medicina General", telefono="3110001122")
    prof2 = Profesional(documento_identidad="VET200", nombre_completo="Dra. Camila Torres", especialidad="Cirugía", telefono="3110003344")
    prof3 = Profesional(documento_identidad="VET300", nombre_completo="Dr. Santiago Castro", especialidad="Dermatología", telefono="3110005566")

    tc_control = TipoConsulta(nombre="Control / Vacunación", duracion_minutos=20)
    tc_general = TipoConsulta(nombre="Consulta General", duracion_minutos=30)
    tc_cirugia = TipoConsulta(nombre="Procedimiento / Especialidad", duracion_minutos=60)

    db.add_all([prop, prof1, prof2, prof3, tc_control, tc_general, tc_cirugia])
    db.commit()

    m_viva = Mascota(propietario_id=prop.id, nombre="Max", especie="Canino", estado_vital="viva")
    m_muerta = Mascota(propietario_id=prop.id, nombre="Felix", especie="Felino", estado_vital="fallecida")
    db.add_all([m_viva, m_muerta])
    db.commit()

    # Dependencia override para FastAPI
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)

# ============================================================================
# PRUEBAS DE ESTADO Y CATÁLOGOS
# ============================================================================
def test_health_check(client):
    """Verifica que el servicio esté operativo."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_listar_tres_profesionales(client):
    """Verifica que la clínica cuente con los 3 profesionales disponibles."""
    response = client.get("/api/v1/catalogos/profesionales")
    assert response.status_code == 200
    profesionales = response.json()
    assert len(profesionales) == 3

# ============================================================================
# REGLAS DE NEGOCIO: AGENDAMIENTO, SOLAPAMIENTO Y ESTADO VITAL
# ============================================================================
def test_agendar_cita_exitoso_duracion_calculada(client):
    """Agendar una cita calcula automáticamente la hora de finalización (Regla 2)."""
    payload = {
        "profesional_id": 1,
        "mascota_id": 1,
        "tipo_consulta_id": 2,  # Consulta General (30 min)
        "fecha_hora_inicio": "2026-09-21T09:00:00",
        "motivo": "Revisión rutinaria de oído"
    }
    response = client.post("/api/v1/citas/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["fecha_hora_inicio"] == "2026-09-21T09:00:00"
    assert data["fecha_hora_fin"] == "2026-09-21T09:30:00"  # +30 min exactos
    assert data["estado"] == "programada"

def test_rechazo_cruce_horario_solapamiento(client):
    """Verifica que se rechace una cita solapada con código 409 Conflict (Regla 1)."""
    # Cita 1: 09:00 a 09:30
    client.post("/api/v1/citas/", json={
        "profesional_id": 1,
        "mascota_id": 1,
        "tipo_consulta_id": 2,
        "fecha_hora_inicio": "2026-09-21T09:00:00"
    })

    # Cita 2 que colisiona: 09:15 a 09:45
    response = client.post("/api/v1/citas/", json={
        "profesional_id": 1,
        "mascota_id": 1,
        "tipo_consulta_id": 2,
        "fecha_hora_inicio": "2026-09-21T09:15:00"
    })
    assert response.status_code == 409
    assert response.json()["error"] == "CruceHorarioError"

def test_bloqueo_agendamiento_mascota_fallecida(client):
    """Verifica que una mascota fallecida sea rechazada con 400 Bad Request (Regla 4)."""
    response = client.post("/api/v1/citas/", json={
        "profesional_id": 1,
        "mascota_id": 2,  # Felix (fallecida)
        "tipo_consulta_id": 1,
        "fecha_hora_inicio": "2026-09-21T10:00:00"
    })
    assert response.status_code == 400
    assert response.json()["error"] == "MascotaFallecidaError"

# ============================================================================
# REGLA DE NEGOCIO: POLÍTICA DE CANCELACIÓN (2 HORAS)
# ============================================================================
def test_cancelacion_oportuna_vs_inasistencia(client):
    """Prueba la política de las 2 horas para cancelación oportuna vs inasistencia (Regla 3)."""
    # Cita a las 15:00
    cita_res = client.post("/api/v1/citas/", json={
        "profesional_id": 1,
        "mascota_id": 1,
        "tipo_consulta_id": 2,
        "fecha_hora_inicio": "2026-09-21T15:00:00"
    }).json()
    cita_id = cita_res["id"]

    # Caso A: Solicitud con 3 horas de antelación (12:00) -> CANCELADA
    res_cancel_ok = client.post(
        f"/api/v1/citas/{cita_id}/cancelar",
        json={"fecha_hora_solicitud": "2026-09-21T12:00:00"}
    )
    assert res_cancel_ok.status_code == 200
    assert res_cancel_ok.json()["nuevo_estado"] == "cancelada"

    # Nueva cita para probar Caso B (menos de 2 horas)
    cita2_res = client.post("/api/v1/citas/", json={
        "profesional_id": 1,
        "mascota_id": 1,
        "tipo_consulta_id": 2,
        "fecha_hora_inicio": "2026-09-21T16:00:00"
    }).json()
    cita2_id = cita2_res["id"]

    # Caso B: Solicitud con 45 minutos de antelación (15:15) -> INASISTENCIA
    res_cancel_tarde = client.post(
        f"/api/v1/citas/{cita2_id}/cancelar",
        json={"fecha_hora_solicitud": "2026-09-21T15:15:00"}
    )
    assert res_cancel_tarde.status_code == 200
    assert res_cancel_tarde.json()["nuevo_estado"] == "inasistencia"

# ============================================================================
# CONSULTA OBLIGATORIA: AGENDA DEL DÍA CON ESPACIOS LIBRES VISIBLES
# ============================================================================
def test_consulta_agenda_diaria_con_espacios_libres(client):
    """Verifica que la consulta obligatoria de agenda retorne los intervalos libres exactos."""
    # Programamos cita de 09:00 a 09:30 (30 min)
    client.post("/api/v1/citas/", json={
        "profesional_id": 1,
        "mascota_id": 1,
        "tipo_consulta_id": 2,
        "fecha_hora_inicio": "2026-09-22T09:00:00"
    })
    # Programamos cita de 14:00 a 15:00 (60 min)
    client.post("/api/v1/citas/", json={
        "profesional_id": 1,
        "mascota_id": 1,
        "tipo_consulta_id": 3,
        "fecha_hora_inicio": "2026-09-22T14:00:00"
    })

    res = client.get("/api/v1/agenda/profesional/1?fecha=2026-09-22")
    assert res.status_code == 200
    data = res.json()

    assert data["profesional_nombre"] == "Dr. Fernando Reyes"
    assert data["minutos_ocupados"] == 90   # 30 + 60
    assert data["minutos_libres"] == 510    # 600 - 90
    assert len(data["citas_programadas"]) == 2

    # Espacios libres esperados:
    # 08:00 - 09:00 (60 min)
    # 09:30 - 14:00 (270 min)
    # 15:00 - 18:00 (180 min)
    espacios = data["espacios_libres"]
    assert len(espacios) == 3
    assert espacios[0] == {"inicio": "08:00", "fin": "09:00", "duracion_minutos": 60}
    assert espacios[1] == {"inicio": "09:30", "fin": "14:00", "duracion_minutos": 270}
    assert espacios[2] == {"inicio": "15:00", "fin": "18:00", "duracion_minutos": 180}

# ============================================================================
# ATENCIÓN MÉDICA, PRESCRIPCIONES E HISTORIAL RETROSPECTIVO
# ============================================================================
def test_registro_atencion_y_consulta_historial_completo(client):
    """Cierre clínico, generación de recetas y consulta de historial para mascota fallecida."""
    # 1. Agendar y atender
    cita = client.post("/api/v1/citas/", json={
        "profesional_id": 2,
        "mascota_id": 1,
        "tipo_consulta_id": 1,
        "fecha_hora_inicio": "2026-09-23T08:30:00"
    }).json()

    atencion_payload = {
        "cita_id": cita["id"],
        "peso_kg": 28.5,
        "temperatura": 38.5,
        "diagnostico": "Dermatitis alérgica por pulgas",
        "notas_evolucion": "Buen ánimo, sin fiebre",
        "prescripciones": [
            {
                "medicamento": "Apoquel 16mg",
                "dosis": "1 tableta cada 24 horas",
                "duracion_dias": 14,
                "indicaciones": "Vía oral en la mañana con comida"
            }
        ]
    }
    res_atencion = client.post("/api/v1/atenciones/", json=atencion_payload)
    assert res_atencion.status_code == 201
    assert len(res_atencion.json()["prescripciones"]) == 1

    # 2. Consultar historial médico de Max
    res_historial = client.get("/api/v1/atenciones/mascota/1/historial")
    assert res_historial.status_code == 200
    historial = res_historial.json()
    assert historial["nombre"] == "Max"
    assert historial["total_atenciones"] == 1
    assert historial["atenciones"][0]["diagnostico"] == "Dermatitis alérgica por pulgas"

    # 3. Historial de mascota fallecida (Felix) sigue consultable
    res_historial_muerta = client.get("/api/v1/atenciones/mascota/2/historial")
    assert res_historial_muerta.status_code == 200
    assert res_historial_muerta.json()["estado_vital"] == "fallecida"


def test_creacion_entidades_base(client: TestClient):
    """Verifica la creación mediante API de Propietario, Mascota y Profesional."""
    # 1. Crear nuevo propietario
    res_prop = client.post("/api/v1/catalogos/propietarios", json={
        "documento_identidad": "999888777",
        "nombre_completo": "Carlos Mendoza",
        "telefono": "3151234567",
        "email": "carlos@example.com"
    })
    assert res_prop.status_code == 201
    prop_data = res_prop.json()
    assert prop_data["id"] is not None
    assert prop_data["nombre_completo"] == "Carlos Mendoza"

    # 2. Crear nueva mascota asociada al propietario
    res_masc = client.post("/api/v1/catalogos/mascotas", json={
        "propietario_id": prop_data["id"],
        "nombre": "Rocky",
        "especie": "Canino",
        "raza": "Golden Retriever",
        "estado_vital": "viva"
    })
    assert res_masc.status_code == 201
    masc_data = res_masc.json()
    assert masc_data["nombre"] == "Rocky"
    assert masc_data["propietario_id"] == prop_data["id"]

    # 3. Crear nuevo profesional
    res_prof = client.post("/api/v1/catalogos/profesionales", json={
        "documento_identidad": "VET400",
        "nombre_completo": "Dra. Laura Jimenez",
        "especialidad": "Oftalmología",
        "telefono": "3209876543"
    })
    assert res_prof.status_code == 201
    prof_data = res_prof.json()
    assert prof_data["nombre_completo"] == "Dra. Laura Jimenez"
    assert prof_data["especialidad"] == "Oftalmología"