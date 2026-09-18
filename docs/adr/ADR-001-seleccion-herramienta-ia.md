# ADR-001: Selección de Antigravity como Herramienta Agéntica de Desarrollo

* **Estado:** Aceptado
* **Fecha:** 2026-09-18
* **Autor:** Jorge Sebastian Florez Diaz

---

## 1. Contexto y Planteamiento del Problema
Para la construcción del Sistema de Agenda de la Clínica Veterinaria se requiere una herramienta de inteligencia artificial que asista en la especificación, diseño de arquitectura, generación modular de código y mantenimiento de documentación viva. 
La restricción principal del proyecto exige resolver el desarrollo utilizando herramientas accesibles en capa gratuita, garantizando al mismo tiempo que el desarrollador comprenda, controle y pueda defender técnicamente cada decisión frente a preguntas de diseño.

## 2. Decisión
Se selecciona **Antigravity (Google DeepMind)** como el entorno y agente de IA principal para el ciclo de vida del proyecto.

## 3. Alternativas Descartadas

1. **GitHub Copilot (Student Pack):**
   * *Motivo de descarte:* Aunque ofrece buen autocompletado en el editor, su modo agéntico tiene cuotas mensuales acotadas que pueden ser impredecibles en sesiones de refactorización profunda, y su capacidad de gestionar el repositorio local de forma completamente autónoma es más limitada en comparación con un entorno agéntico dedicado.
2. **ChatGPT / Codex (Capa Gratuita):**
   * *Motivo de descarte:* Opera primordialmente como un chat en navegador web. Requiere copiar y pegar código constantemente de forma manual, lo que incrementa el riesgo de desincronización y dificulta la trazabilidad en vivo de los archivos del repositorio.
3. **Claude (Anthropic):**
   * *Motivo de descarte:* La capa gratuita solo está disponible en interfaz web conversacional. Su agente de terminal (`Claude Code`) requiere una suscripción de pago o consumo por tokens mediante API key de pago, lo que incumple la premisa de costo cero.

## 4. Consecuencias

### Positivas
* **Capacidad Agéntica Nativa:** Permite inspección directa del sistema de archivos, ejecución de comandos en consola (pruebas, git, dependencias) y edición granular de archivos sin intervención manual de copia y pega.
* **Trazabilidad de Contexto:** Soporta el uso explícito de archivos de contexto como `AGENTS.md`, permitiendo auditar la evolución de las instrucciones dadas al agente durante el proyecto.
* **Cero Costo Económico:** Opera en versión preliminar gratuita con capacidades agénticas de nivel avanzado.

### Negativas y Mitigaciones
* **Límites de Cuota por Día:** El agente cuenta con un número delimitado de solicitudes diarias.
  * *Mitigación:* Se planifican sesiones de desarrollo con objetivos claros y atómicos, evitando conversaciones dispersas y usando prompts estructurados con decisiones técnicas pre-evaluadas.