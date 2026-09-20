"""Aplicación Principal FastAPI — Sistema de Gestión y Agenda Veterinaria.

Provee una API REST modular, fuertemente tipada y con documentación interactiva Swagger/OpenAPI.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import agenda_router, citas_router, atenciones_router, catalogos_router
from app.services.exceptions import (
    ReglaNegocioError,
    CruceHorarioError,
    MascotaFallecidaError,
    FueraDeJornadaError,
    EntidadNoEncontradaError
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicialización de la persistencia al levantar la aplicación."""
    # Asegura que las 7 tablas existan en SQLite
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Sistema de Gestión y Agenda Veterinaria",
    description=(
        "API REST para la gestión integral de turnos médicos en una clínica veterinaria con 3 profesionales. "
        "Garantiza el cumplimiento innegociable de reglas de negocio: no solapamiento temporal, bloques dinámicos "
        "según el tipo de consulta, política estricta de cancelación (2 horas / inasistencia), restricción "
        "de agendamiento para mascotas fallecidas y cálculo automático de espacios libres en la jornada laboral."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# MANEJADORES CENTRALIZADOS DE EXCEPCIONES DE NEGOCIO
# ============================================================================

@app.exception_handler(CruceHorarioError)
async def cruce_horario_handler(request: Request, exc: CruceHorarioError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"error": "CruceHorarioError", "detalle": str(exc)}
    )

@app.exception_handler(MascotaFallecidaError)
async def mascota_fallecida_handler(request: Request, exc: MascotaFallecidaError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "MascotaFallecidaError", "detalle": str(exc)}
    )

@app.exception_handler(FueraDeJornadaError)
async def fuera_de_jornada_handler(request: Request, exc: FueraDeJornadaError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "FueraDeJornadaError", "detalle": str(exc)}
    )

@app.exception_handler(EntidadNoEncontradaError)
async def entidad_no_encontrada_handler(request: Request, exc: EntidadNoEncontradaError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "EntidadNoEncontradaError", "detalle": str(exc)}
    )

@app.exception_handler(ReglaNegocioError)
async def regla_negocio_handler(request: Request, exc: ReglaNegocioError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "ReglaNegocioError", "detalle": str(exc)}
    )

# ============================================================================
# MONTAJE DE CONTROLADORES MODULARES (RUTAS API v1)
# ============================================================================
app.include_router(agenda_router, prefix="/api/v1")
app.include_router(citas_router, prefix="/api/v1")
app.include_router(atenciones_router, prefix="/api/v1")
app.include_router(catalogos_router, prefix="/api/v1")

@app.get("/", include_in_schema=False)
def root():
    """Redirige automáticamente la raíz hacia la documentación interactiva Swagger UI."""
    return RedirectResponse(url="/docs")

@app.get("/health", tags=["Estado del Sistema"])
def health_check():
    """Comprobación de salud de la API."""
    return {"status": "ok", "servicio": "Sistema Agenda Veterinaria", "version": "1.0.0"}