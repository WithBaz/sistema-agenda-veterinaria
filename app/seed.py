"""Script de inicialización y siembra de datos (Seed Data).

Puebla la base de datos con los 3 profesionales requeridos por el enunciado,
los tipos de consulta estandarizados, propietarios, mascotas de prueba y registros históricos.
"""

from datetime import datetime, date, time, timedelta, timezone
from app.database import engine, SessionLocal, Base
from app.models import (
    Propietario,
    Mascota,
    Profesional,
    TipoConsulta,
    Cita,
    AtencionRegistrada,
    PrescripcionMedica
)

def poblar_datos():
    """Ejecuta la siembra de datos iniciales en la base de datos SQLite."""
    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Verificar si ya existen profesionales para no duplicar
        if db.query(Profesional).count() > 0:
            print("[INFO] La base de datos ya contiene datos. Omitiendo siembra.")
            return

        print("[INFO] Iniciando siembra de datos para la Clínica Veterinaria...")

        # 2. Los 3 Profesionales requeridos por el enunciado
        profesionales = [
            Profesional(
                documento_identidad="VET001",
                nombre_completo="Dr. Carlos Mendoza",
                especialidad="Medicina General y Diagnóstico",
                telefono="3001112233",
                email="carlos.mendoza@veterinaria.com",
                activo=True
            ),
            Profesional(
                documento_identidad="VET002",
                nombre_completo="Dra. Laura Rios",
                especialidad="Cirugía y Ortopedia Veterinaria",
                telefono="3002223344",
                email="laura.rios@veterinaria.com",
                activo=True
            ),
            Profesional(
                documento_identidad="VET003",
                nombre_completo="Dr. Andrés Gómez",
                especialidad="Dermatología y Medicina Preventiva",
                telefono="3003334455",
                email="andres.gomez@veterinaria.com",
                activo=True
            ),
        ]
        db.add_all(profesionales)
        db.flush()

        # 3. Tipos de Consulta (Catálogo desacoplado de duraciones)
        tipos_consulta = [
            TipoConsulta(
                nombre="Control / Vacunación",
                duracion_minutos=20,
                descripcion="Revisión básica de rutina, control de peso y aplicación de biológicos.",
                activo=True
            ),
            TipoConsulta(
                nombre="Consulta General",
                duracion_minutos=30,
                descripcion="Evaluación médica completa, anamnesis y diagnóstico preventivo.",
                activo=True
            ),
            TipoConsulta(
                nombre="Procedimiento / Especialidad",
                duracion_minutos=60,
                descripcion="Intervenciones menores, curaciones complejas, limpiezas y ecografías.",
                activo=True
            ),
        ]
        db.add_all(tipos_consulta)
        db.flush()

        # 4. Propietarios de ejemplo
        prop1 = Propietario(
            documento_identidad="1098765432",
            nombre_completo="Juan David Pérez Gómez",
            telefono="3159988776",
            email="juan.perez@email.com",
            direccion="Calle 45 # 23-10"
        )
        prop2 = Propietario(
            documento_identidad="1098123456",
            nombre_completo="María Fernanda López Díaz",
            telefono="3165544332",
            email="maria.lopez@email.com",
            direccion="Carrera 15 # 80-45"
        )
        db.add_all([prop1, prop2])
        db.flush()

        # 5. Mascotas (incluyendo caso de mascota fallecida con historial)
        mascota1 = Mascota(
            propietario_id=prop1.id,
            nombre="Rocky",
            especie="Canino",
            raza="Golden Retriever",
            fecha_nacimiento=date(2021, 3, 15),
            estado_vital="viva",
            notas_alergias="Alérgico a ciertos alimentos procesados con pollo."
        )
        mascota2 = Mascota(
            propietario_id=prop1.id,
            nombre="Luna",
            especie="Felino",
            raza="Siamés",
            fecha_nacimiento=date(2018, 6, 20),
            estado_vital="fallecida",  # REGLA 4: Fallecida
            notas_alergias="Paciente geriátrico con falla renal crónica."
        )
        mascota3 = Mascota(
            propietario_id=prop2.id,
            nombre="Lucas",
            especie="Canino",
            raza="Beagle",
            fecha_nacimiento=date(2023, 1, 10),
            estado_vital="viva",
            notas_alergias="Sin alergias conocidas."
        )
        db.add_all([mascota1, mascota2, mascota3])
        db.flush()

        # 6. Historial previo para la mascota fallecida (Luna)
        cita_historica = Cita(
            profesional_id=profesionales[0].id,
            mascota_id=mascota2.id,
            tipo_consulta_id=tipos_consulta[1].id,  # 30 min
            fecha_hora_inicio=datetime(2025, 11, 10, 10, 0),
            fecha_hora_fin=datetime(2025, 11, 10, 10, 30),
            estado="completada",
            motivo="Chequeo por pérdida de peso progresiva"
        )
        db.add(cita_historica)
        db.flush()

        atencion_historica = AtencionRegistrada(
            cita_id=cita_historica.id,
            fecha_registro=datetime(2025, 11, 10, 10, 30),
            peso_kg=3.4,
            temperatura=38.3,
            diagnostico="Enfermedad Renal Crónica Estadio III",
            notas_evolucion="Se indica cambio inmediato a dieta renal estricta y suplementación."
        )
        db.add(atencion_historica)
        db.flush()

        presc_historica = PrescripcionMedica(
            atencion_id=atencion_historica.id,
            medicamento="Quelante de Fósforo",
            dosis="1/2 tableta cada 12 horas",
            duracion_dias=30,
            indicaciones="Mezclar pulverizado con el alimento húmedo."
        )
        db.add(presc_historica)

        # 7. Citas para demostración de agenda diaria y cálculo de espacios libres
        # Programadas para el próximo lunes a las 09:00 y 11:00
        proximo_lunes = date.today() + timedelta(days=(7 - date.today().weekday()) % 7 or 7)
        
        cita_demo1 = Cita(
            profesional_id=profesionales[0].id,  # Dr. Carlos Mendoza
            mascota_id=mascota1.id,             # Rocky
            tipo_consulta_id=tipos_consulta[1].id,  # Consulta General (30 min)
            fecha_hora_inicio=datetime.combine(proximo_lunes, time(9, 0)),
            fecha_hora_fin=datetime.combine(proximo_lunes, time(9, 30)),
            estado="programada",
            motivo="Control periódico y chequeo articular"
        )
        cita_demo2 = Cita(
            profesional_id=profesionales[0].id,  # Dr. Carlos Mendoza
            mascota_id=mascota3.id,             # Lucas
            tipo_consulta_id=tipos_consulta[2].id,  # Procedimiento (60 min)
            fecha_hora_inicio=datetime.combine(proximo_lunes, time(11, 0)),
            fecha_hora_fin=datetime.combine(proximo_lunes, time(12, 0)),
            estado="programada",
            motivo="Limpieza dental profunda"
        )
        db.add_all([cita_demo1, cita_demo2])

        db.commit()
        print("[ÉXITO] Semilla de datos completada satisfactoriamente:")
        print(f"  - 3 Profesionales registrados ({', '.join(p.nombre_completo for p in profesionales)})")
        print(f"  - 3 Tipos de consulta (20, 30 y 60 min)")
        print(f"  - 2 Propietarios y 3 Mascotas (incluye paciente fallecido con historial)")
        print(f"  - Citas de demostración agendadas para el día {proximo_lunes.strftime('%Y-%m-%d')}")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Falló la siembra de datos: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    poblar_datos()