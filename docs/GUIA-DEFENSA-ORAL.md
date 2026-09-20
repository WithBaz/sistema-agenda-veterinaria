# Guía Estratégica para la Defensa Oral (6 Minutos + 2 Minutos de Preguntas)

> **Herramientas de Empleabilidad en Ingeniería de Sistemas**  
> **Sistema B:** Agenda de una Clínica Veterinaria  
> **Estudiante:** Jorge Sebastian Florez Diaz (Código: 1152243)  
> **Ponderación de la Defensa:** **50% de la Calificación Final**

---

## ⏱️ Cronograma y Guion Minuto a Minuto (6 Minutos de Exposición)

### Minuto 1: Qué construí y qué decidí dejar por fuera (Delimitación del Alcance)
* **El Problema:** *"Buenos días. El Sistema B resuelve la problemática de una clínica veterinaria con 3 profesionales que tradicionalmente gestionaba sus citas en papel o por teléfono, sufriendo cruces de citas y pérdida de historiales clínicos."*
* **Qué construí:** *"Construí una API REST robusta y desacoplada en Python con FastAPI, SQLite y SQLAlchemy 2.0. El sistema modela 7 entidades relacionales, aplica automáticamente 4 reglas de negocio innegociables y provee una consulta diaria con cálculo matemático exacto de espacios libres de 08:00 a 18:00."*
* **Qué decidí dejar por fuera y por qué:** *"Dejé deliberadamente fuera autenticación con OAuth/JWT, pasarelas de pago y despliegues en la nube. ¿Por qué? Para evitar complejidad accidental y garantizar portabilidad absoluta: el evaluador puede clonar el repositorio, ejecutar las 21 pruebas unitarias en un segundo o correr el servidor en local con un solo comando sin depender de infraestructura pesada como Docker."*

---

### Minuto 2: Arquitectura del Sistema (Por qué está separada así y dónde vive cada regla)
* **Separación en 3 Capas Estrictas:**
  1. **Capa de Persistencia (`app/models/` y `app/database.py`):** Modelos SQLAlchemy 2.0 puramente declarativos. Maneja las 7 tablas e integridad referencial forzada (`PRAGMA foreign_keys=ON;`).
  2. **Capa de Dominio / Servicios (`app/services/`):** El "cerebro" del sistema. **Aquí vive el 100% de las reglas de negocio**, completamente desacopladas de la API y del protocolo HTTP.
  3. **Capa de Entrada / API REST (`app/routers/` y `app/schemas/`):** Controladores FastAPI y validación estricta con Pydantic V2. Solo recibe peticiones, inyecta la sesión de base de datos y serializa respuestas.
* **Dónde vive cada regla de negocio:**
  * *Regla 1 (No solapamiento):* En `app/services/agenda_service.py` -> función `agendar_cita()`.
  * *Regla 2 (Duración dinámica):* En `agenda_service.py` derivando el fin desde `TipoConsulta.duracion_minutos`.
  * *Regla 3 (Cancelación 2 horas / Inasistencia):* En `agenda_service.py` -> función `cancelar_cita()`.
  * *Regla 4 (Mascotas fallecidas):* En `agenda_service.py` (bloqueo al agendar) y `atencion_service.py` (historial médico siempre accesible).
  * *Consulta obligatoria (Espacios libres):* En `agenda_service.py` -> función `obtener_agenda_diaria()`.

---

### Minuto 3 & 4: Tres Decisiones de Arquitectura Importantes (ADRs) y Alternativas Descartadas
* **Decisión 1 (ADR-001 - Elección de Herramienta de IA):**
  * *Decisión:* Seleccioné **Antigravity (Google DeepMind)** en versión preliminar gratuita.
  * *Alternativas descartadas:* Descarté ChatGPT/Codex y Claude web porque operan como chats externos sin acceso agéntico nativo al sistema de archivos ni ejecución de terminal, lo que obligaría a copiar y pegar código a mano. Descarté GitHub Copilot por restricciones de cuotas mensuales en refactorización profunda.
* **Decisión 2 (ADR-002 - Persistencia con SQLite y SQLAlchemy 2.0):**
  * *Decisión:* SQLite con listener de eventos para claves foráneas y tipado moderno (`Mapped`, `mapped_column`).
  * *Alternativas descartadas:* Descarté PostgreSQL en Docker porque exige que el jurado tenga instalado y configurado Docker en su máquina para calificar. Descarté SQL plano (`sqlite3` nativo) por riesgo de inyecciones SQL y mantenimiento engorroso.
* **Decisión 3 (ADR-003 - Algoritmo de Disponibilidad y Espacios Libres):**
  * *Decisión:* Algoritmo de barrido lineal (*sweep-line*) con puntero continuo sobre la jornada de 600 minutos.
  * *Alternativas descartadas:* Descarté una matriz de slots fijos de 15 minutos en base de datos. Una matriz de slots fijos es rígida y fragmenta la base de datos; al tener consultas de 20, 30 y 60 minutos, el cálculo continuo por intervalos semiabiertos `[inicio, fin)` es matemáticamente exacto y soporta cualquier duración futura sin tocar código.

---

### Minuto 5: Cómo usé la IA (Qué delegué, qué rechacé y por qué)
* **Qué le delegué:** *"Le delegué la generación de estructuras repetitivas (modelos Pydantic, esqueletos de pruebas Pytest, sintaxis de SQLAlchemy 2.0 y scripts de seed data)."*
* **Qué le rechacé y corregí (Criterio del desarrollador):**
  1. *Rechazo en README:* La IA propuso inicialmente encabezados con datos universitarios y académicos. **Se lo rechacé** para mantener un estándar 100% profesional de portafolio y le exigí que las dos primeras líneas definieran exactamente el problema que resuelve el software.
  2. *Rechazo en modelo de 5 entidades:* El enunciado pedía solo 5 entidades mínimas. Decidí ampliar a 7 entidades introduciendo `TipoConsulta` (para desacoplar los tiempos de atención y no 'quemar' duraciones en el código) y `PrescripcionMedica` (para evitar la pérdida real de información farmacológica en el historial).
  3. *Corrección técnica de fechas:* Corregí llamadas a `datetime.utcnow()` que generaban advertencias de deprecación en Python 3.12, migrando a objetos timezone-aware con `timezone.utc`.
  4. *Corrección en SQLite TestClient:* Detecté que SQLite en memoria creaba bases de datos separadas por hilo en FastAPI, forzando la implementación de `StaticPool` para las pruebas E2E.

---

### Minuto 6: Demostración Rápida del Sistema
* Abrir la terminal y mostrar que corren las **21 pruebas automatizadas** en 1 segundo: `pytest -v`.
* Abrir Swagger UI en `http://127.0.0.1:8000/docs`.
* Mostrar el endpoint estrella: `GET /api/v1/agenda/profesional/1?fecha=2026-09-21`.
  * Mostrar cómo calcula automáticamente las citas y la lista de `espacios_libres` entre ellas sumando exactamente los 600 minutos diarios.
* Mostrar la cancelación: enviar una cita a cancelar con menos de 2 horas y demostrar cómo el sistema la marca automáticamente como `inasistencia`.

---

## ❓ Banco de Preguntas Difíciles del Jurado (2 Minutos de Preguntas)

#### P1: *"¿Por qué creaste 7 entidades si el enunciado solo pedía 5?"*
> **Tu respuesta:** *"El enunciado planteaba 5 entidades mínimas. Identifiqué dos riesgos de diseño: primero, si dejaba las duraciones de 20, 30 y 60 minutos quemadas en el código, el sistema sería rígido; por eso creé `TipoConsulta`. Segundo, el enunciado dice que 'se pierden historiales'; un historial no es un texto plano, requiere registrar prescripciones y medicamentos administrados; por eso creé `PrescripcionMedica`. Ambas decisiones están respaldadas en `ASSUMPTIONS.md` y `AGENTS.md`."*

#### P2: *"¿Dónde y cómo validas que dos citas no se solapen?"*
> **Tu respuesta:** *"Vive en la capa de servicios, en `agendar_cita()` dentro de `agenda_service.py`. Utilizo la condición de intersección de intervalos semiabiertos: una colisión ocurre si `inicio_existente < fin_nuevo AND fin_existente > inicio_nuevo` para citas del mismo profesional con estado programada o completada. Si colisiona, lanza un `CruceHorarioError` que FastAPI transforma limpiamente en un `HTTP 409 Conflict`."*

#### P3: *"¿Qué pasa si la clínica decide abrir los domingos o cambiar el horario de 08:00 a 18:00?"*
> **Tu respuesta:** *"Los límites de jornada están centralizados como constantes de dominio (`HORA_INICIO_JORNADA`, `HORA_FIN_JORNADA`, `TOTAL_MINUTOS_JORNADA`) en el servicio de agenda. Al cambiar esas constantes, tanto el validador de agendamiento como el algoritmo de espacios libres se adaptan automáticamente sin alterar la base de datos ni los controladores."*

#### P4: *"¿Cómo aseguras que el historial de una mascota fallecida no se borre?"*
> **Tu respuesta:** *"En la entidad `Mascota` el estado vital es un campo (`viva`/`fallecida`). En `agendar_cita()` se valida si está fallecida y se bloquea el agendamiento con `MascotaFallecidaError` (`HTTP 400`). Sin embargo, en `atencion_service.py` la consulta de historial no filtra por estado vital, permitiendo recorrer todas las atenciones y prescripciones históricas de la mascota para auditoría clínica permanente."*

#### P5: *"¿Qué parte del código escribió la IA que tú no entendieras al principio?"*
> **Tu respuesta:** *"Inicialmente, cuando se ejecutaron las pruebas con el `TestClient` de FastAPI, SQLite en memoria arrojaba que las tablas no existían a pesar de haberse creado en el fixture. Al investigar comprendí que SQLite `:memory:` asigna una base de datos nueva a cada hilo de conexión. Entendí la causa raíz y configuré `poolclass=StaticPool` en SQLAlchemy para forzar una única conexión compartida entre el servidor de prueba y el cliente HTTP."*