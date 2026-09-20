# AGENTS.md — Contexto Operativo para el Agente de IA

Este documento define el contexto, las restricciones de dominio, los principios arquitectónicos y las pautas operativas que el agente de IA debe acatar rigurosamente en el desarrollo del **Sistema de Gestión y Agenda Veterinaria**.

---

## 1. Misión del Sistema
Construir una solución robusta y estructurada para la gestión de turnos y agendas médicas de una clínica veterinaria con 3 profesionales, garantizando consistencia horaria, trazabilidad de historiales clínicos y estricto cumplimiento de las reglas de negocio.

## 2. Restricciones y Reglas de Negocio Innegociables
El agente de IA debe implementar y verificar en la lógica de negocio las siguientes reglas:
1. **Validación de Cruces Temporales:** Ningún profesional puede tener citas concurrentes o que se solapen en el tiempo.
2. **Cálculo de Bloques de Consulta:** La hora de finalización de una cita se calcula estrictamente a partir de la hora de inicio y la duración configurada en `TipoConsulta` (20, 30 o 60 minutos según corresponda).
3. **Restricción de Cancelación:** La cancelación de una cita solo es válida si se solicita con al menos 2 horas de antelación respecto a la hora programada (`tiempo_solicitud <= hora_inicio - 2 horas`). Superado ese límite, la cita debe registrarse obligatoriamente con el estado `inasistencia`.
4. **Validación de Estado Vital de Paciente:** Ninguna mascota con estado `fallecida` puede ser agendada para una nueva cita. Sin embargo, su historial clínico y atenciones pasadas deben mantenerse accesibles para consulta.
5. **Algoritmo de Agenda Diaria y Espacios Libres:** La consulta de agenda por profesional para una fecha determinada debe retornar las citas programadas y calcular explícitamente los intervalos de tiempo libres dentro de la jornada laboral establecida (08:00 a 18:00).

## 3. Modelo de Entidades Reconocidas
El sistema opera sobre 7 entidades relacionadas:
1. `Propietario`: Dueño o responsable del animal.
2. `Mascota`: Paciente sujeto de atención.
3. `Profesional`: Veterinario asignado al turno (3 profesionales).
4. `TipoConsulta`: Catálogo de tipos de consulta y tiempos estándar de atención.
5. `Cita`: Evento de agendamiento temporal.
6. `AtencionRegistrada`: Cierre clínico y diagnóstico de una cita efectuada.
7. `PrescripcionMedica`: Indicaciones farmacológicas asociadas a la atención médica.

## 4. Principios de Arquitectura y Buenas Prácticas
* **Separación de Responsabilidades en Capas:**
  * **Capa de Dominio / Servicios:** Donde residen las reglas de negocio, validaciones y algoritmos de disponibilidad horaria.
  * **Capa de Persistencia / Repositorios:** Abstracción para el almacenamiento y consultas en base de datos con SQLAlchemy 2.0 y SQLite.
  * **Capa de Entrada / API:** Controladores REST con FastAPI, validación Pydantic V2 y documentación Swagger OpenAPI.
* **Transparencia y Explicabilidad:** Toda decisión técnica y fragmento de código debe ser claro, mantenible y fundamentado. Evitar código innecesariamente complejo.
* **Persistencia Robusta:** Esquema relacional con claves foráneas activadas mediante eventos de conexión (`PRAGMA foreign_keys=ON;`).

## 5. Registro de Evolución del Contexto (Changelog)
* **2026-09-18 (Versión Inicial):**
  - Formalización del alcance del sistema, entidades nucleares y reglas de validación de turnos veterinarios.
  - Definición de parámetros de jornada laboral (08:00 a 18:00) y tiempos estándar por tipo de consulta.
* **2026-09-18 (Iteración 2 - Enriquecimiento del Modelo y Gobernanza):**
  - Incorporación de las entidades `TipoConsulta` (desacople de duraciones) y `PrescripcionMedica` (trazabilidad del historial clínico).
  - Integración de `ASSUMPTIONS.md`, `BITACORA-IA.md` y `ADR-001` (Selección de herramienta agéntica de IA).
* **2026-09-19 (Iteración 3 - Lógica de Dominio y Algoritmos de Disponibilidad):**
  - Formalización de la capa de servicios (`app/services/`): detección de colisiones mediante intersección de intervalos semiabiertos.
  - Especificación del algoritmo de barrido lineal para el cálculo exacto de huecos libres dentro de los 600 minutos diarios.
  - Incorporación de `ADR-003` y suite de pruebas unitarias con Pytest.
* **2026-09-20 (Iteración 4 - Culminación del Sistema, API REST y Cierre):**
  - Exposición de endpoints REST modulares bajo `/api/v1` en FastAPI con documentación Swagger interactiva.
  - Siembra de datos automática (`seed.py`) con los 3 profesionales, tipos de consulta y casos de prueba.
  - Suite de integración E2E completando 21 pruebas automatizadas con 100% de éxito.
* **2026-09-20 (Iteración 5 - Usabilidad, Interfaz Web y Despliegue en 1 Clic):**
  - Extracción de la guía oral hacia formato Word (.docx) en el Escritorio local fuera del repositorio público.
  - Creación del Dashboard Visual SPA (`app/static/index.html`) para control de agenda diaria y consulta de historiales.
  - Incorporación del script ejecutable `iniciar_sistema.bat` con detección y creación automática de entorno virtual.
  - Habilitación de endpoints y formularios de registro para entidades base (`Propietario`, `Mascota`, `Profesional`).
  - Suite completa de 22 pruebas automatizadas pasando al 100%.