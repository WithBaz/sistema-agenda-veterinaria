"""Configuración de base de datos con SQLAlchemy 2.0 y SQLite.

Garantiza la activación estricta de claves foráneas en SQLite mediante eventos de conexión.
"""

from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

# URL de conexión SQLite local
DATABASE_URL = "sqlite:///./veterinaria.db"

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