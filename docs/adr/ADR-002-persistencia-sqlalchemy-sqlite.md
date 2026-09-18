# ADR-002: Persistencia Relacional con SQLite y SQLAlchemy 2.0

* **Estado:** Aceptado
* **Fecha:** 2026-09-18
* **Autor:** Jorge Sebastian Florez Diaz

---

## 1. Contexto y Planteamiento del Problema
El sistema requiere persistencia de datos para 7 entidades interconectadas, con soporte para consultas complejas de solapamiento de horarios, cálculo de intervalos libres y preservación inmutable de historiales clínicos.
Asimismo, el proyecto exige que el sistema pueda ejecutarse desde cero en cualquier máquina evaluadora de forma rápida, sin dependencias de infraestructura pesada o configuraciones complejas de servidores externos.

## 2. Decisión
Se selecciona **SQLite** como motor de persistencia relacional embebido junto con **SQLAlchemy 2.0** como biblioteca de mapeo objeto-relacional (ORM) en Python.
Para garantizar la integridad referencial en SQLite, se implementa un listener a nivel de eventos de conexión (`event.listens_for(Engine, "connect")`) que fuerza la activación de `PRAGMA foreign_keys=ON` en cada sesión.

## 3. Alternativas Descartadas

1. **Uso de `sqlite3` nativo con consultas SQL en crudo (Raw SQL):**
   * *Motivo de descarte:* Obliga a escribir cadenas SQL dispersas, aumentando el riesgo de errores de sintaxis, dificultando el tipado estricto y haciendo tedioso el mapeo manual hacia modelos de dominio y esquemas Pydantic.
2. **PostgreSQL o MySQL mediante contenedores Docker:**
   * *Motivo de descarte:* Añade una sobrecarga operativa y de infraestructura innecesaria para el alcance de una clínica con 3 profesionales. Además, exigiría que el evaluador tenga instalado y corriendo Docker en su máquina para revisar el proyecto, violando el principio de simplicidad y facilidad de ejecución.
3. **Bases de datos Documentales NoSQL (ej. MongoDB o archivos JSON):**
   * *Motivo de descarte:* No garantizan integridad referencial nativa ni restricciones de clave foránea inmediatas, lo que comprometería la coherencia del historial clínico y complicaría la detección de solapamiento temporal de citas.

## 4. Consecuencias

### Positivas
* **Portabilidad Absoluta:** La base de datos se almacena en un único archivo local (`veterinaria.db`), permitiendo que el sistema corra desde cero tras clonar el repositorio e instalar requerimientos.
* **Tipado Estricto con SQLAlchemy 2.0:** Uso de `Mapped` y `mapped_column`, permitiendo autocompletado y validación estática de tipos en el IDE.
* **Facilidad de Pruebas Unitarias:** Permite ejecutar la suite completa de pruebas sobre SQLite en memoria (`sqlite:///:memory:`) en menos de 1 segundo de forma totalmente aislada.
* **Integridad Garantizada:** Claves foráneas y eliminación en cascada controlada (`cascade="all, delete-orphan"`).

### Negativas y Mitigaciones
* **Concurrencia de Escritura en SQLite:** SQLite bloquea el archivo durante las transacciones de escritura.
  * *Mitigación:* Para una clínica veterinaria con 3 profesionales y un volumen moderado de citas, el impacto es nulo. Se configura `check_same_thread=False` y transacciones atómicas de corta duración.