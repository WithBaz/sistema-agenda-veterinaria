# Sistema de Gestión y Agenda Veterinaria

Plataforma backend para la gestión automatizada de turnos médicos en clínicas veterinarias, diseñada para erradicar el solapamiento de consultas y la pérdida de historiales clínicos. Permite coordinar las agendas de múltiples profesionales en tiempo real, calculando la duración dinámica de cada cita y visibilizando los espacios libres de atención.

---

## 📌 Problemática que Resuelve
En entornos veterinarios donde la recepción y programación se gestiona mediante registros manuales o llamadas telefónicas, surgen fricciones operativas críticas:
* Cruces y solapamientos de turnos entre profesionales de la salud animal.
* Tiempos de atención mal calculados por falta de estandarización en los tipos de consulta.
* Desarticulación o extravío del historial clínico de los pacientes.

Este sistema centraliza el agendamiento mediante validaciones de concurrencia y reglas de negocio estrictas que aseguran una operación clínica fluida y confiable.

## 🎯 Capacidades Principales y Reglas de Negocio
* **Prevención de Solapamiento Temporal:** Garantiza a nivel de lógica de dominio que ningún profesional pueda tener citas que coincidan o se traslapen en el tiempo.
* **Bloques Dinámicos por Tipo de Consulta:** La duración de cada cita se determina automáticamente según el procedimiento requerido:
  * Control / Vacunación: 20 minutos.
  * Consulta General: 30 minutos.
  * Procedimiento / Especialidad: 60 minutos.
* **Política de Cancelaciones:** Permite cancelaciones con hasta 2 horas de anticipación a la cita programada; posterior a esa ventana, la cita se registra de forma obligatoria como inasistencia.
* **Restricción por Estado Vital:** Las mascotas marcadas como fallecidas quedan inhabilitadas para nuevas citas, preservando permanentemente su historial clínico para consultas.
* **Consulta Inteligente de Disponibilidad (Consulta Obligatoria):** Genera la agenda del día por profesional, mostrando tanto los turnos asignados como los intervalos libres disponibles en la jornada laboral (08:00 a 18:00).

## 🧱 Modelo de Dominio (7 Entidades)
1. **Propietario:** Responsable del paciente animal (documento, nombres, teléfono de contacto).
2. **Mascota:** Paciente veterinario asociado a un propietario (nombre, especie, raza, estado vital: activo/fallecido).
3. **Profesional:** Médico veterinario encargado de la atención clínica (capacidad para 3 profesionales concurrentes).
4. **TipoConsulta (Entidad Adicional):** Catálogo desacoplado de servicios veterinarios y sus duraciones estimadas estándar.
5. **Cita:** Registro estructurado de la reserva (profesional, mascota, tipo de consulta, rango horario y estado).
6. **Atención Registrada:** Registro médico generado tras la consulta (motivo, diagnóstico clínico y notas evolutivas).
7. **PrescripcionMedica (Entidad Adicional):** Detalle farmacológico estructurado (medicamento, dosis, duración de tratamiento) asociado a la atención médica.

## 🛠️ Stack Tecnológico
* **Lenguaje:** Python 3.12+
* **Framework Web:** FastAPI (Arquitectura REST con interfaz visual SPA y documentación Swagger OpenAPI)
* **Persistencia:** SQLite con SQLAlchemy 2.0 (Motor relacional portable, tipado estricto y claves foráneas activas `PRAGMA foreign_keys=ON;`)
* **Validación y Esquemas:** Pydantic V2
* **Pruebas Automatizadas:** Pytest con TestClient (22 pruebas unitarias y de integración E2E)

---

## 🚀 Instalación y Puesta en Marcha (Desde Cero)

### Método 1: Inicio Rápido en 1 Clic (Recomendado para Windows)
El proyecto incluye el ejecutable [`iniciar_sistema.bat`](iniciar_sistema.bat) en la raíz:
1. Haz **doble clic** sobre `iniciar_sistema.bat`.
2. El script detectará automáticamente el entorno virtual (lo creará e instalará dependencias si no existen), poblará la base de datos inicial con los datos de prueba (`seed.py`), levantará el servidor Uvicorn y abrirá directamente tu navegador en:
   - **Dashboard Visual:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
   - **Documentación Swagger:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### Método 2: Instalación Manual por Terminal (Multiplataforma)

#### 1. Clonar y Configurar Entorno
```bash
git clone https://github.com/WithBaz/sistema-agenda-veterinaria.git
cd sistema-agenda-veterinaria
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

#### 2. Poblar Datos de Prueba (Seed Data)
Precarga automáticamente los 3 profesionales requeridos, catálogo de consultas, propietarios y pacientes demo:
```bash
python -m app.seed
```

#### 3. Ejecutar el Servidor Web
```bash
uvicorn app.main:app --reload
```
Abre en tu navegador:  
* 👉 **Interfaz Gráfica / Dashboard:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)  
* 👉 **Swagger UI (OpenAPI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
* 👉 **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

### Método 3: Despliegue en la Nube con Vercel (1 Clic desde GitHub)
El proyecto está preconfigurado para Vercel Serverless Functions ([`vercel.json`](vercel.json) y [`api/index.py`](api/index.py)):
1. Entra a [Vercel](https://vercel.com) e inicia sesión con tu usuario de GitHub.
2. Haz clic en **Add New...** > **Project**.
3. Selecciona tu repositorio: `WithBaz/sistema-agenda-veterinaria` y haz clic en **Import**.
4. Mantén la configuración por defecto (*Framework Preset: Other*, *Root Directory: ./*).
5. Haz clic en **Deploy**. En menos de 1 minuto tendrás una URL pública activa (ej. `https://sistema-agenda-veterinaria.vercel.app`) con la interfaz gráfica, el modo oscuro y Swagger operativos.

---

## 🧪 Pruebas Automatizadas
El sistema cuenta con una suite completa de **22 pruebas automatizadas** que validan la persistencia de modelos, restricciones de unicidad, el algoritmo de detección de solapamientos, el barrido lineal de espacios libres, la política de cancelación de 2 horas y el bloqueo de mascotas fallecidas:
```bash
pytest -v
```

---

## 📡 Resumen de Endpoints de la API REST

| Módulo | Método | Endpoint | Descripción |
|---|---|---|---|
| **Agenda** | `GET` | `/api/v1/agenda/profesional/{id}?fecha=YYYY-MM-DD` | Consulta obligatoria: citas del día e intervalos libres calculados (08:00 a 18:00) |
| **Citas** | `POST` | `/api/v1/citas/` | Agendar nueva cita médica con validación de no solapamiento y estado vital |
| **Citas** | `PATCH` | `/api/v1/citas/{id}/cancelar` | Cancelar cita (aplica regla de antelación $\ge 2$ horas o marca inasistencia) |
| **Atenciones** | `POST` | `/api/v1/atenciones/` | Registrar atención clínica y diagnósticos tras culminar cita |
| **Atenciones** | `GET` | `/api/v1/atenciones/mascota/{id}/historial` | Historial médico completo y prescripciones (accesible incluso si la mascota falleció) |
| **Catálogos** | `POST` / `GET` | `/api/v1/catalogos/propietarios` | Crear y listar propietarios / tutores |
| **Catálogos** | `POST` / `GET` | `/api/v1/catalogos/mascotas` | Crear y listar mascotas pacientes |
| **Catálogos** | `POST` / `GET` | `/api/v1/catalogos/profesionales` | Crear y listar médicos veterinarios |
| **Catálogos** | `POST` / `GET` | `/api/v1/catalogos/tipos-consulta` | Crear y listar tipos de consulta y duraciones |

---

## 📁 Documentación de Arquitectura y Gobernanza
* [AGENTS.md](AGENTS.md): Contexto operativo, restricciones y evolución de directrices para el agente de IA.
* [ASSUMPTIONS.md](ASSUMPTIONS.md): Registro explícito de asunciones técnicas y de negocio.
* [BITACORA-IA.md](BITACORA-IA.md): Auditoría completa del proceso y sesiones de trabajo con IA.
* [ADR-001: Elección de Herramienta de IA](docs/adr/ADR-001-seleccion-herramienta-ia.md): Decisión sobre Antigravity (Google DeepMind).
* [ADR-002: Persistencia Relacional](docs/adr/ADR-002-persistencia-sqlalchemy-sqlite.md): Decisión sobre SQLite y SQLAlchemy 2.0.
* [ADR-003: Algoritmo de Disponibilidad](docs/adr/ADR-003-algoritmo-disponibilidad-agenda.md): Decisión sobre algoritmo de barrido lineal continuo vs ranuras fijas.