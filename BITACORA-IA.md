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

---

## Sesión 3: 2026-09-19 — Capa de Servicios, Reglas Innegociables y Algoritmo de Disponibilidad
* **Herramienta utilizada:** Antigravity (Google DeepMind).
* **Objetivo de la sesión:** Implementar la capa de servicios de dominio, codificar las 4 reglas de negocio innegociables, desarrollar el algoritmo de cálculo de espacios libres y formalizar `ADR-003`.

### 1. ¿Qué se le pidió al agente?
1. Continuar con el siguiente bloque del sistema para adelantar trabajo antes del cierre del fin de semana.
2. Presentar un plan de implementación para revisión antes de tocar el código.
3. Desarrollar la lógica de negocio y las pruebas automatizadas asociadas.

### 2. ¿Qué propuso el agente?
* **Separación de Servicios:** `app/services/agenda_service.py` (citas, solapamientos, cancelación y disponibilidad diaria) y `app/services/atencion_service.py` (cierre clínico y consulta de historial).
* **Esquemas Pydantic V2:** DTOs en `app/schemas/` para tipar solicitudes y respuestas.
* **Algoritmo de Detección de Cruces:** Intersección matemática de intervalos semiabiertos `[inicio, fin)` filtrados en BD.
* **Algoritmo de Barrido Temporal:** Algoritmo lineal (*sweep-line*) con puntero cursor para detectar huecos de tiempo entre citas de 08:00 a 18:00.
* **Gobernanza:** Redacción de `ADR-003` para sustentar el algoritmo de disponibilidad temporal frente a matrices de ranuras discretas.

### 3. ¿Qué se aceptó y qué se rechazó?
* ✅ **Aceptado:**
  * Plan de implementación aprobado mediante `implementation_plan.md`.
  * La fórmula de detección de colisión de intervalos y el cálculo continuo de huecos libres.
  * La regla estricta de cancelación: $\ge 2$ horas pasa a `cancelada`, $< 2$ horas pasa obligatoriamente a `inasistencia`.
  * Suite de 8 nuevas pruebas unitarias en `tests/test_agenda_service.py` (totalizando 13 pruebas aprobadas en menos de 1 segundo).
* ❌ **Rechazado / Descartado:**
  * Se descartó utilizar una matriz de slots fijos de 15 minutos en base de datos por ser rígida e incompatible con tipos de consulta heterogéneos (20, 30 y 60 min).

### 4. ¿Qué quedó sin verificar para las siguientes sesiones?
* Capa de presentación / API REST con FastAPI (rutas HTTP, inyección de dependencias y documentación Swagger UI).
* Script de inicialización de datos de prueba (*seed data*) con los 3 profesionales de la clínica.

---

## Sesión 4: 2026-09-20 — API REST con FastAPI, Seed Data, Pruebas E2E y Guía de Defensa
* **Herramienta utilizada:** Antigravity (Google DeepMind).
* **Objetivo de la sesión:** Concluir el 100% del sistema: exponer controladores HTTP modulares, sembrar datos de prueba con los 3 veterinarios, ejecutar pruebas de integración E2E y documentar la guía estratégica para la defensa oral de 6 minutos.

### 1. ¿Qué se le pidió al agente?
1. Terminar todo el sistema antes de la fecha límite dominical (23:59).
2. Implementar los endpoints de FastAPI y la documentación interactiva en Swagger.
3. Asegurar datos precargados para que el evaluador pueda probar el sistema de inmediato.
4. Elaborar una guía detallada para sostener con éxito la defensa oral frente a preguntas del jurado.

### 2. ¿Qué propuso el agente?
* **Arquitectura de Controladores (`app/routers/`):** Desacoplar rutas en `agenda.py`, `citas.py`, `atenciones.py` y `catalogos.py`.
* **Mapeo de Errores Limpio:** Manejadores globales en `app/main.py` traduciendo excepciones de dominio (`CruceHorarioError` $\to$ 409, `MascotaFallecidaError` $\to$ 400, etc.).
* **Siembra de Datos (`app/seed.py`):** Carga automática de los 3 profesionales, 3 tipos de consulta, casos de prueba con citas y mascota fallecida con historial previo.
* **Pruebas de Integración (`tests/test_api_endpoints.py`):** 8 pruebas E2E con `TestClient` simulando llamadas HTTP reales.
* **Guía de Defensa (`docs/GUIA-DEFENSA-ORAL.md`):** Libreto minuto a minuto (Min 1 a 6) y respuestas preparadas para las preguntas del jurado.

### 3. ¿Qué se aceptó y qué se rechazó?
* ✅ **Aceptado:**
  * Plan de implementación definitivo aprobado.
  * Los 4 routers HTTP modulares y la redirección automática de `/` a `/docs`.
  * La incorporación de `StaticPool` en la configuración de pruebas para solucionar el aislamiento de SQLite `:memory:` entre hilos en `TestClient`.
  * La estructura de la defensa oral orientada al criterio y decisiones de arquitectura.
* ❌ **Modificado durante el proceso:**
  * Se instaló la dependencia `httpx` requerida por `fastapi.testclient.TestClient` y se actualizó `requirements.txt`.

### 4. Estado Final de Verificación:
* **21 pruebas automatizadas aprobadas (100% de éxito en 1.05 segundos).**
* Base de datos poblada y lista para ejecutar con un solo comando.
* Entregable completo y listo para defensa oral.

---

## Sesión 5: Usabilidad, Frontend Interactivo, Despliegue en 1 Clic y Entidades Base
* **Fecha:** 2026-09-20 (Jornada Nocturna)
* **Herramienta utilizada:** Antigravity (Google DeepMind).
* **Objetivo de la sesión:** Incorporar una interfaz de usuario visual SPA completa, automatizar el arranque en 1 clic para Windows (`iniciar_sistema.bat`), completar endpoints de registro para Propietarios, Mascotas y Profesionales, y extraer la guía oral a formato Word en el escritorio del usuario.

### 1. ¿Qué se le pidió al agente?
1. Proveer una interfaz visual funcional para que el sistema no dependa únicamente de Swagger.
2. Extraer la guía de defensa oral fuera del repositorio público de GitHub y entregarla como documento Word en el escritorio.
3. Facilitar la ejecución desde cero en la máquina del usuario y en cualquier PC que clone el repositorio.
4. Responder y resolver si era necesario crear mascotas, propietarios o profesionales en la aplicación.

### 2. ¿Qué propuso el agente?
* **Dashboard Visual Integrado (`app/static/index.html`):** Interfaz SPA con Tailwind CSS que renderiza la línea de tiempo del veterinario, métricas de ocupación, espacios libres con agendamiento directo, cancelación con regla de 2 horas y visor del historial médico.
* **Script de Despliegue Automático (`iniciar_sistema.bat`):** Script que detecta la existencia de `.venv` (creándolo e instalando dependencias si no existe), ejecuta la siembra de base de datos (`seed.py`), levanta el servidor Uvicorn y abre el navegador por defecto.
* **Extensión de Endpoints y UI de Catálogos:** Adición de rutas POST para `Profesional` y `TipoConsulta`, junto con un modal en la interfaz web para registrar nuevos Propietarios y Mascotas con validación de estado vital.
* **Guía Oral en Word:** Generación vía `python-docx` del archivo `Guia_Defensa_Oral_Veterinaria.docx` ubicado en el escritorio local y desvinculado del repositorio Git.

### 3. ¿Qué se aceptó y qué se rechazó?
* ✅ **Aceptado:**
  * Eliminación de `docs/GUIA-DEFENSA-ORAL.md` del repositorio para proteger la privacidad académica.
  * Inclusión del script `iniciar_sistema.bat` documentado en el `README.md`.
  * Formulario modal en la interfaz web para registrar clientes y mascotas de forma ágil.
  * Incorporación de la prueba unitaria 22 cubriendo el alta de entidades base.

### 4. Estado Final de Verificación:
* **22 pruebas automatizadas aprobadas (100% de éxito).**
* Interfaz gráfica y API REST sincronizadas y completamente operativas.
* Repositorio Git limpio, profesional y sincronizado con GitHub.