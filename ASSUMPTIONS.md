# ASSUMPTIONS.md — Asunciones y Decisiones de Diseño

Este documento registra de forma explícita todas las decisiones, parámetros y restricciones operativas asumidas para resolver las ambigüedades deliberadas del enunciado del **Sistema de Gestión y Agenda Veterinaria**.

---

## 1. Jornada Laboral y Disponibilidad
* **Horario de Operación:** La clínica veterinaria opera en una jornada continua de **08:00 a 18:00** (10 horas = 600 minutos disponibles por día por profesional).
* **Días de Atención:** Lunes a Sábado.
* **Disponibilidad Concurrente:** Cada uno de los 3 profesionales cuenta con su propia agenda independiente. La clínica puede atender hasta 3 mascotas simultáneamente, siempre que cada una esté asignada a un profesional distinto.

## 2. Tipos de Consulta y Duración Dinámica
Para evitar valores fijos (*hardcoded*) en el código, se parametriza la entidad `TipoConsulta` con los siguientes estándares iniciales:
* **Control / Vacunación:** 20 minutos de duración.
* **Consulta General:** 30 minutos de duración.
* **Procedimiento / Especialidad:** 60 minutos de duración.
* *Asunción técnica:* La hora de finalización de la cita (`fecha_hora_fin`) se calcula de forma automática e inmutable a partir de `fecha_hora_inicio + duracion_minutos`.

## 3. Política y Ventana de Cancelación
* **Límite Temporal de Cancelación:** Se establece una ventana estricta de **2 horas** antes de la hora programada de la cita.
* **Comportamiento ante cancelación tardía:** Si la solicitud de cancelación ocurre con menos de 2 horas de antelación (`tiempo_solicitud > hora_inicio - 2 horas`), el sistema rechaza la cancelación como tal y actualiza automáticamente el estado de la cita a `inasistencia`. Esto garantiza métricas reales sobre el ausentismo sin liberar el espacio a destiempo.

## 4. Gestión de Pacientes Fallecidos
* **Condición de Bloqueo:** Cuando una mascota tiene el estado vital `fallecida`, el sistema bloquea cualquier intento de inserción de una nueva cita (`HTTP 400 - Bad Request`).
* **Preservación Histórica:** La información del paciente, sus citas históricas, diagnósticos y prescripciones médicas pasadas se mantienen intactas en la base de datos para auditoría médica y consultas retrospectivas.

## 5. Expansión del Modelo de Dominio (7 Entidades)
El enunciado estipula 5 entidades mínimas (`Propietario`, `Mascota`, `Profesional`, `Cita`, `Atención Registrada`). Se incorporan deliberadamente 2 entidades complementarias:
1. **`TipoConsulta`:** Desacopla la duración y nombre del servicio del código fuente, permitiendo a la clínica configurar o añadir nuevos tipos de servicio sin desplegar nuevo código.
2. **`PrescripcionMedica`:** Resuelve de raíz la problemática de *"se pierden historiales"*, formalizando qué fármacos, dosis y duración de tratamiento fueron formulados en cada atención médica.

## 6. Selección de Interfaz Operativa
* **Elección:** API REST con FastAPI (OpenAPI / Swagger UI interactivo).
* **Justificación:** Prioriza una arquitectura desacoplada, facilitando la validación inmediata de todas las reglas de negocio en endpoints bien documentados, con serialización estricta mediante Pydantic y pruebas reproducibles.