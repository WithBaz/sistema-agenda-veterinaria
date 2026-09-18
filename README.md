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
* **Consulta Inteligente de Disponibilidad:** Genera la agenda del día por profesional, mostrando tanto los turnos asignados como los intervalos libres disponibles en la jornada laboral (08:00 a 18:00).

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
* **Framework Web:** FastAPI (Arquitectura REST con documentación interactiva OpenAPI / Swagger)
* **Persistencia:** SQLite con SQLAlchemy (Motor relacional portable, ligero y consistente)
* **Validación y Esquemas:** Pydantic V2

## 📁 Documentación de Arquitectura y Proceso
* [AGENTS.md](AGENTS.md): Contexto operativo, restricciones y evolución de directrices para el agente de IA.
* [ASSUMPTIONS.md](ASSUMPTIONS.md): Registro explícito de asunciones técnicas y de negocio.
* [BITACORA-IA.md](BITACORA-IA.md): Registro de interacciones, decisiones y control del proceso con IA.
* [ADR-001](docs/adr/ADR-001-seleccion-herramienta-ia.md): Decisión arquitectónica sobre la elección del entorno agéntico de IA.