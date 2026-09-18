# BITACORA-IA.md — Registro de Interacción y Uso de Inteligencia Artificial

Documento de auditoría del proceso de colaboración con herramientas de IA, registrando las peticiones realizadas, propuestas del agente, decisiones del desarrollador y elementos pendientes de verificación técnica.

---

## Sesión 1: 2026-09-18 — Definición del Sistema, Alcance y Primeros Commits
* **Herramienta utilizada:** Antigravity (Google DeepMind) en versión preliminar.
* **Objetivo de la sesión:** Analizar el documento de requerimientos, identificar la asignación individual, definir la arquitectura inicial, redactar directrices en `AGENTS.md` y publicar los dos primeros commits obligatorios.

### 1. ¿Qué se le pidió al agente?
1. Leer el documento de Word de la prueba técnica en el Escritorio y extraer la asignación correspondiente al código estudiantil (`1152243`).
2. Desglosar las reglas de negocio del Sistema B (Clínica Veterinaria) y los entregables obligatorios.
3. Proponer el stack tecnológico, la estructura inicial del proyecto y la configuración con el repositorio remoto de GitHub.
4. Diseñar extensiones del modelo de datos para enriquecer las 5 entidades mínimas del enunciado.

### 2. ¿Qué propuso el agente?
* **Stack:** Python 3.12 + FastAPI + SQLite + SQLAlchemy.
* **Modelo inicial:** Incluir datos de la universidad y del estudiante en el encabezado del `README.md`.
* **Ampliación de entidades:** Proponer `TipoConsulta` (para desacoplar duraciones de servicios) y `PrescripcionMedica` (para dar trazabilidad real al historial médico).
* **Estructura de gobernanza:** Crear el primer ADR formal sobre la elección de la herramienta de IA y el archivo `ASSUMPTIONS.md`.

### 3. ¿Qué se aceptó y qué se rechazó?
* ✅ **Aceptado:** 
  * La elección de Python y FastAPI por su agilidad, documentación interactiva Swagger y robustez de tipado.
  * La incorporación de las 2 entidades adicionales (`TipoConsulta` y `PrescripcionMedica`) por aportar alto valor al dominio sin sobrecargar el alcance.
  * La estructura del primer commit con `AGENTS.md` y `.gitignore`.
* ❌ **Rechazado / Modificado:**
  * **Rechazado el formato del README propuesto inicialmente:** Se eliminó cualquier referencia a datos universitarios/académicos para mantener un estándar 100% profesional de portafolio.
  * **Condición obligatoria exigida por el desarrollador:** Las dos primeras líneas del `README.md` debían describir de forma concisa y directa qué es el software y qué problema resuelve antes de cualquier otro detalle.

### 4. ¿Qué quedó sin verificar para las siguientes sesiones?
* Implementación del código ejecutable en FastAPI (modelos SQLAlchemy y endpoints).
* Pruebas automáticas del algoritmo de cálculo de espacios libres en la agenda diaria.
* Pruebas de concurrencia para evitar citas simultáneas de un mismo profesional.

---

## Sesión 2: 2026-09-18 — Modelado de Persistencia Relacional y Pruebas Unitarias
* **Herramienta utilizada:** Antigravity (Google DeepMind).
* **Objetivo de la sesión:** Diseñar e implementar los modelos de base de datos para las 7 entidades con SQLAlchemy 2.0 y SQLite, verificando integridad referencial y relaciones mediante pruebas automatizadas.

### 1. ¿Qué se le pidió al agente?
1. Iniciar con el apartado de los modelos de base de datos del sistema.
2. Presentar un plan de implementación detallado para aprobación previa.
3. Construir la estructura modular de la capa de datos.

### 2. ¿Qué propuso el agente?
* **Diseño modular:** Separar cada modelo en su propio módulo bajo `app/models/`, exportados centralizadamente desde `app/models/__init__.py`.
* **SQLAlchemy 2.0:** Emplear `Mapped` y `mapped_column` para tipado estricto de campos.
* **Integridad en SQLite:** Configurar un listener a nivel de eventos de conexión (`PRAGMA foreign_keys=ON`), dado que SQLite desactiva las claves foráneas por defecto.
* **Gobernanza:** Redactar `ADR-002: Persistencia Relacional con SQLite y SQLAlchemy 2.0` y suite de pruebas unitarias automatizadas con `pytest`.

### 3. ¿Qué se aceptó y qué se rechazó?
* ✅ **Aceptado:**
  * Plan de implementación completo (`implementation_plan.md`).
  * Estructura modular de 7 entidades y activación de claves foráneas por pragma.
  * Suite de 5 pruebas automatizadas (creación de esquema, inserción completa, claves foráneas, unicidad y cascadas).
* ❌ **Rechazado / Modificado:**
  * Se corrigieron advertencias de deprecación de fechas de Python 3.12 (`datetime.utcnow()` reemplazado por objetos timezone-aware con `timezone.utc`).

### 4. ¿Qué quedó sin verificar para las siguientes sesiones?
* Capa de servicios de dominio (algoritmo de cálculo de espacios libres y validación de solapamiento de citas).
* Endpoints REST en FastAPI y serializadores Pydantic.