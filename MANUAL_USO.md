# RF Monitor - Manual de uso inicial

## 1. Requisitos

- Windows 10/11 x64.
- Python 3.13 con entorno virtual `.venv`.
- Node.js y npm para el frontend.
- (Opcional) Signal Hound BB60C conectado.
- (Opcional) Ollama para el asistente IA.

## 2. Inicio rápido

Doble clic en `start_rf_monitor.bat`.

Se abrirán dos consolas:
- Backend: http://127.0.0.1:8000
- Frontend: http://127.0.0.1:5173

Abrir el frontend en el navegador.

## 3. Inicio manual

Backend:
```
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend:
```
cd frontend
npm run dev
```

## 4. Uso básico

1. Verificar estado de conexión en el panel de espectro.
2. Configurar frecuencia, span, RBW, VBW y nivel de referencia.
3. Observar el espectro y el waterfall.
4. Usar marcadores para mediciones puntuales.
5. Ejecutar peak search y mediciones.
6. Grabar IQ o audio si es necesario.
7. Consultar sesiones, campañas y exportaciones.

## 5. Modo simulado

Si no hay BB60C conectado, la aplicación utiliza una fuente sintética automáticamente.
El estado de fuente se muestra como `SIMULATED`.

## 6. GPS

- Conectar un GPS USB o usar el modo simulado.
- Leer posiciones y asociarlas a mediciones.
- Visualizar recorridos en el mapa.

## 7. Pruebas

Backend:
```
cd backend
..\.venv\Scripts\python.exe -m pytest -m "not hardware"
```

Frontend:
```
cd frontend
npm run build
```

## 8. Notas

- No se requieren pruebas físicas para validar la lógica.
- Las funciones dependientes de hardware quedan pendientes de validación física.