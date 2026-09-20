"""Excepciones de dominio para las reglas de negocio veterinarias."""

class ReglaNegocioError(Exception):
    """Excepción base para violaciones de reglas de negocio."""
    pass

class CruceHorarioError(ReglaNegocioError):
    """Lanzada cuando se intenta agendar una cita que se solapa con otra del mismo profesional."""
    pass

class MascotaFallecidaError(ReglaNegocioError):
    """Lanzada cuando se intenta agendar una cita para una mascota fallecida."""
    pass

class CancelacionTardiaError(ReglaNegocioError):
    """Lanzada o referenciada en políticas de cancelación fuera de tiempo."""
    pass

class FueraDeJornadaError(ReglaNegocioError):
    """Lanzada cuando una cita se intenta agendar fuera de la jornada laboral (08:00 a 18:00)."""
    pass

class EntidadNoEncontradaError(ReglaNegocioError):
    """Lanzada cuando un recurso requerido no existe en la base de datos."""
    pass