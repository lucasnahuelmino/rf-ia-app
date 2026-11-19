@echo off
setlocal

set "ROOT=%~dp0"

echo Iniciando RF Monitor...

start "RF Monitor Backend" cmd /k "cd /d "%ROOT%backend" && "%ROOT%.venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

start "RF Monitor Frontend" cmd /k "cd /d "%ROOT%frontend" && npm run dev"

echo.
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://127.0.0.1:5173
echo.
echo Cierre las ventanas de consola para detener los servidores.
pause