"""Entrypoint para despliegue serverless en Vercel."""
from app.main import app

# Exportar como app y handler para máxima compatibilidad con el runtime de Vercel
handler = app
