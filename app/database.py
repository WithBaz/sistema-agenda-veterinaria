"""Configuración de base de datos con SQLAlchemy 2.0 y SQLite.

Garantiza la activación estricta de claves foráneas en SQLite mediante eventos de conexión.
"""

import os
import shutil
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

# Configuración dinámica de base de datos para entorno local o Serverless (Vercel)
if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    TMP_DB = "/tmp/veterinaria.db"
    LOCAL_DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), "veterinaria.db")
    if not os.path.exists(TMP_DB) and os.path.exists(LOCAL_DB):
        try:
            shutil.copyfile(LOCAL_DB, TMP_DB)
        except Exception:
            pass
    DATABASE_URL = f"sqlite:///{TMP_DB}"
else:
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./veterinaria.db")

# Creación del motor de persistencia
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

# SQLite requiere activación explícita de integridad referencial (claves foráneas)
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Fuerza la activación de PRAGMA foreign_keys en cada conexión SQLite."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    """Clase base declarativa para todos los modelos del sistema."""
    pass

def get_db() -> Generator[Session, None, None]:
    """Generador de sesión de base de datos para inyección de dependencias en FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()