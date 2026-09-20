@echo off
title Sistema Agenda Veterinaria - VetSchedule
echo ========================================================
echo      Iniciando Sistema de Agenda Veterinaria
echo ========================================================
echo.
cd /d "%~dp0"
echo [1/2] Verificando base de datos y siembra de datos...
.\.venv\Scripts\python.exe -m app.seed
echo.
echo [2/2] Levantando servidor web en http://127.0.0.1:8000 ...
echo.
echo ========================================================
echo Interfaz Web lista en: http://127.0.0.1:8000
echo Documentacion API en:  http://127.0.0.1:8000/docs
echo (Presiona Ctrl + C en esta ventana para apagar el servidor)
echo ========================================================
echo.
start http://127.0.0.1:8000
.\.venv\Scripts\uvicorn.exe app.main:app --reload