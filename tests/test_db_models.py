"""Pruebas automatizadas de la capa de persistencia y modelos relacionales."""
import pytest
from datetime import datetime, date, timedelta, timezone
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.models import (
    Base,
    Propietario,
    Mascota,
    Profesional,
    TipoConsulta,
    Cita,
    AtencionRegistrada,
    PrescripcionMedica,
)

@pytest.fixture
def db_session():
    """Crea una base de datos SQLite en memoria con claves foráneas activadas para pruebas."""
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )

    @event.listens_for(test_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=test_engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSession()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)

def test_creacion_tablas(db_session):
    """Verifica que las 7 tablas se hayan creado en la base de datos."""
    tablas_esperadas = {
        "propietarios",
        "mascotas",
        "profesionales",
        "tipos_consulta",
        "citas",
        "atenciones_registradas",
        "prescripciones_medicas"
    }
    tablas_existentes = set(Base.metadata.tables.keys())
    assert tablas_esperadas.issubset(tablas_existentes)

def test_flujo_completo_insercion_y_relaciones(db_session):
    """Inserta las 7 entidades y valida la navegación relacional bidireccional."""
    # 1. Propietario
    prop = Propietario(
        documento_identidad="1098765432",
        nombre_completo="Carlos Andrés Perez",
        telefono="3001234567",
        email="carlos.perez@example.com"
    )
    db_session.add(prop)
    db_session.commit()
    db_session.refresh(prop)
    assert prop.id is not None

    # 2. Mascota
    mascota = Mascota(
        propietario_id=prop.id,
        nombre="Firulais",
        especie="Canino",
        raza="Golden Retriever",
        fecha_nacimiento=date(2022, 5, 10),
        estado_vital="viva"
    )
    db_session.add(mascota)
    db_session.commit()
    db_session.refresh(mascota)
    assert mascota.id is not None
    assert mascota.propietario.nombre_completo == "Carlos Andrés Perez"
    assert len(prop.mascotas) == 1

    # 3. Profesional
    prof = Profesional(
        documento_identidad="13579246",
        nombre_completo="Dra. Valentina Gomez",
        especialidad="Medicina General y Cirugía",
        telefono="3159876543"
    )
    db_session.add(prof)
    db_session.commit()

    # 4. TipoConsulta (Catálogo desacoplado)
    tc = TipoConsulta(
        nombre="Consulta General",
        duracion_minutos=30,
        descripcion="Revisión médica integral"
    )
    db_session.add(tc)
    db_session.commit()

    # 5. Cita
    inicio = datetime(2026, 9, 20, 9, 0)
    fin = inicio + timedelta(minutes=tc.duracion_minutos)
    cita = Cita(
        profesional_id=prof.id,
        mascota_id=mascota.id,
        tipo_consulta_id=tc.id,
        fecha_hora_inicio=inicio,
        fecha_hora_fin=fin,
        estado="completada",
        motivo="Chequeo semestral y decaimiento"
    )
    db_session.add(cita)
    db_session.commit()
    assert cita.id is not None
    assert cita.profesional.nombre_completo == "Dra. Valentina Gomez"
    assert cita.mascota.nombre == "Firulais"
    assert cita.tipo_consulta.duracion_minutos == 30

    # 6. AtencionRegistrada (1:1 con Cita)
    atencion = AtencionRegistrada(
        cita_id=cita.id,
        peso_kg=24.5,
        temperatura=38.6,
        diagnostico="Gastroenteritis leve por ingesta alimentaria",
        notas_evolucion="Paciente alerta y con hidratación adecuada"
    )
    db_session.add(atencion)
    db_session.commit()
    assert atencion.id is not None
    assert cita.atencion.diagnostico == atencion.diagnostico

    # 7. PrescripcionMedica (1:N con AtencionRegistrada)
    presc1 = PrescripcionMedica(
        atencion_id=atencion.id,
        medicamento="Metronidazol Suspensión",
        dosis="5 ml cada 12 horas",
        duracion_dias=5,
        indicaciones="Administrar junto con alimentos blandos"
    )
    presc2 = PrescripcionMedica(
        atencion_id=atencion.id,
        medicamento="Probióticos Caninos",
        dosis="1 cápsula diaria",
        duracion_dias=7,
        indicaciones="En ayunas por la mañana"
    )
    db_session.add_all([presc1, presc2])
    db_session.commit()

    # Verificación de navegación profunda en historial clínico
    db_session.refresh(mascota)
    assert len(mascota.citas) == 1
    cita_paciente = mascota.citas[0]
    assert cita_paciente.atencion is not None
    assert len(cita_paciente.atencion.prescripciones) == 2
    nombres_meds = [p.medicamento for p in cita_paciente.atencion.prescripciones]
    assert "Metronidazol Suspensión" in nombres_meds
    assert "Probióticos Caninos" in nombres_meds

def test_restriccion_clave_foranea_sqlite(db_session):
    """Verifica que SQLite rechace inserciones con IDs foráneos inexistentes."""
    mascota_invalida = Mascota(
        propietario_id=9999,  # No existe
        nombre="Fantasma",
        especie="Felino",
        estado_vital="viva"
    )
    db_session.add(mascota_invalida)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

def test_unicidad_documentos(db_session):
    """Verifica que no se puedan registrar propietarios con el mismo documento."""
    prop1 = Propietario(documento_identidad="CC123", nombre_completo="A", telefono="1")
    prop2 = Propietario(documento_identidad="CC123", nombre_completo="B", telefono="2")
    db_session.add(prop1)
    db_session.commit()
    db_session.add(prop2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

def test_cascada_atencion_prescripcion(db_session):
    """Verifica que eliminar una atención elimine en cascada sus prescripciones asociadas."""
    now_utc = datetime.now(timezone.utc)
    prop = Propietario(documento_identidad="CC456", nombre_completo="Test", telefono="123")
    prof = Profesional(documento_identidad="VET1", nombre_completo="Dr", especialidad="Gen", telefono="456")
    tc = TipoConsulta(nombre="Control", duracion_minutos=20)
    db_session.add_all([prop, prof, tc])
    db_session.commit()

    mascota = Mascota(propietario_id=prop.id, nombre="Rex", especie="Canino")
    db_session.add(mascota)
    db_session.commit()

    cita = Cita(
        profesional_id=prof.id,
        mascota_id=mascota.id,
        tipo_consulta_id=tc.id,
        fecha_hora_inicio=now_utc,
        fecha_hora_fin=now_utc + timedelta(minutes=20)
    )
    db_session.add(cita)
    db_session.commit()

    atencion = AtencionRegistrada(cita_id=cita.id, diagnostico="Sano")
    db_session.add(atencion)
    db_session.commit()

    presc = PrescripcionMedica(atencion_id=atencion.id, medicamento="Vacuna Rabia", dosis="1 dosis", duracion_dias=1)
    db_session.add(presc)
    db_session.commit()

    assert db_session.query(PrescripcionMedica).count() == 1

    # Eliminación en cascada
    db_session.delete(atencion)
    db_session.commit()

    assert db_session.query(PrescripcionMedica).count() == 0