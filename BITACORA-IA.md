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