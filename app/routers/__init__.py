"""Controladores HTTP de la API REST."""
from app.routers.agenda import router as agenda_router
from app.routers.citas import router as citas_router
from app.routers.atenciones import router as atenciones_router
from app.routers.catalogos import router as catalogos_router

__all__ = ["agenda_router", "citas_router", "atenciones_router", "catalogos_router"]