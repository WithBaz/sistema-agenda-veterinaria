# ADR-003: Algoritmo de Cálculo de Disponibilidad y Detección de Solapamiento Temporal

* **Estado:** Aceptado
* **Fecha:** 2026-09-19
* **Autor:** Jorge Sebastian Florez Diaz

---

## 1. Contexto y Planteamiento del Problema
El sistema de agenda veterinaria debe cumplir dos requisitos temporales estrictos:
1. Impedir que un profesional de la salud animal tenga dos citas simultáneas o solapadas.
2. Proveer una consulta diaria por profesional que no solo liste las citas programadas, sino que calcule e identifique explícitamente todos los intervalos de tiempo libres dentro de la jornada laboral (08:00 a 18:00).
Adicionalmente, las consultas tienen duraciones heterogéneas (20, 30 y 60 minutos), lo que descarta el uso de bloques uniformes fijos.

## 2. Decisión
Se implementa una solución en la capa de servicios de dominio fundamentada en dos algoritmos de intervalo continuo:

1. **Detección de Solapamiento por Intersección de Intervalos:**
   Una nueva cita con rango $[\text{inicio}_{\text{nueva}}, \text{fin}_{\text{nueva}})$ colisiona con una cita activa existente si y solo si:
   $$\text{inicio}_{\text{existente}} < \text{fin}_{\text{nueva}} \quad \land \quad \text{fin}_{\text{existente}} > \text{inicio}_{\text{nueva}}$$
   Esta comprobación se realiza mediante consulta filtrada e indexada en base de datos sobre citas activas (`programada`, `completada`), rechazando la operación con `CruceHorarioError` antes de persistir.

2. **Algoritmo de Barrido Lineal (*Sweep-line*) para Espacios Libres:**
   Se establece una jornada continua de 600 minutos ($08:00$ a $18:00$). Las citas activas del día se ordenan cronológicamente.
   Un puntero temporal (`cursor`) inicia en las $08:00$:
   * Para cada cita ordenada, si $\text{inicio}_{\text{cita}} > \text{cursor}$, se detecta un hueco libre en $[\text{cursor}, \text{inicio}_{\text{cita}})$, cuya duración en minutos se calcula y registra.
   * El puntero se desplaza a $\max(\text{cursor}, \text{fin}_{\text{cita}})$.
   * Al finalizar las citas, si $\text{cursor} < 18:00$, se emite el último espacio libre hasta el cierre de la jornada.

## 3. Alternativas Descartadas

1. **Discretización en Matriz de Ranuras Fijas (Slots de 10 o 15 minutos en Base de Datos):**
   * *Motivo de descarte:* Fragmenta la base de datos con cientos de registros vacíos diarios por profesional. Dado que los tipos de consulta varían en 20, 30 y 60 minutos, sincronizar y bloquear múltiples ranuras discretas introduce una complejidad accidental excesiva y riesgo de desalineación.
2. **Validación de Cruces Exclusivamente en Memoria:**
   * *Motivo de descarte:* Cargar todas las citas del profesional en memoria para validar cruces puede ocasionar condiciones de carrera si dos usuarios agendan concurrentemente. La validación delegada con índices en base de datos es atómica y determinista.

## 4. Consecuencias

### Positivas
* **Flexibilidad Total de Duraciones:** El sistema soporta cualquier duración configurada en `TipoConsulta` sin requerir cambios de código o migraciones de base de datos.
* **Precisión Matemática Absoluta:** La suma de minutos ocupados y minutos libres totaliza exactamente los 600 minutos de la jornada laboral diaria.
* **Rendimiento:** El algoritmo de barrido es $O(N \log N)$ debido al ordenamiento de citas, lo cual es instantáneo para el volumen diario de una clínica veterinaria (menos de 1 milisegundo por consulta).

### Negativas y Mitigaciones
* Requiere que las fechas y horas registradas sean consistentes en zona horaria para evitar desfasajes en la resta de tiempos. Se mitiga normalizando el uso de datetimes comparables.