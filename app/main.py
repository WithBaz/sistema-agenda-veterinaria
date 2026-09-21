"""Aplicación Principal FastAPI — Sistema de Gestión y Agenda Veterinaria.

Provee una API REST modular, interfaz web interactiva y documentación interactiva Swagger/OpenAPI.
"""

from contextlib import asynccontextmanager
import os
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base, SessionLocal
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
    # En entornos Serverless como Vercel, si la base de datos está vacía, se auto-siembra
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        try:
            from app.models import Profesional
            from app.seed import poblar_datos
            with SessionLocal() as session:
                if session.query(Profesional).count() == 0:
                    poblar_datos()
        except Exception as e:
            print(f"[WARN] Error durante inicialización en Vercel: {e}")
    yield

app = FastAPI(
    title="Sistema de Gestión y Agenda Veterinaria",
    description=(
        "API REST y Dashboard para la gestión integral de turnos médicos en una clínica veterinaria con 3 profesionales. "
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

@app.middleware("http")
async def normalizar_rutas_vercel(request: Request, call_next):
    """Normaliza rutas y prefijos de proxy o rewrite generados por entornos serverless como Vercel."""
    # 1. Si Vercel envió la ruta coincidente original en el header x-matched-path
    matched_path = request.headers.get("x-matched-path")
    if matched_path and matched_path not in ("/api/index.py", "/api/index") and not matched_path.endswith("404"):
        request.scope["path"] = matched_path
    else:
        path = request.scope.get("path", "")
        for prefix in ("/api/index.py", "/api/index"):
            if path == prefix:
                request.scope["path"] = "/"
                break
            elif path.startswith(prefix + "/"):
                request.scope["path"] = path[len(prefix):]
                break
    return await call_next(request)

# Montaje de archivos estáticos (Frontend)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

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
@app.get("/api/index.py", include_in_schema=False)
@app.get("/api", include_in_schema=False)
def root():
    """Sirve la interfaz web interactiva en la raíz del sistema."""
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "VetSchedule API activa. Visita /docs para Swagger UI."}

@app.get("/api/debug-vercel", include_in_schema=False)
def debug_vercel(request: Request):
    """Endpoint de diagnóstico para inspeccionar headers y paths de Vercel."""
    return {
        "headers": dict(request.headers),
        "url_path": request.url.path,
        "scope_path": request.scope.get("path"),
        "matched_path": request.headers.get("x-matched-path"),
    }

@app.get("/health", tags=["Estado del Sistema"])
def health_check():
    """Comprobación de salud de la API."""
    return {"status": "ok", "servicio": "Sistema Agenda Veterinaria", "version": "1.0.0"}