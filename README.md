# SNCTE RF Analyzer v1.0

## Sistema Nacional de Comprobación Técnica de Emisiones

Plataforma de monitoreo y análisis de espectro radioeléctrico desarrollada para operaciones de inspección, supervisión y análisis técnico utilizando receptores Signal Hound BB60C.

---

# Objetivos del Proyecto

SNCTE RF Analyzer tiene como finalidad proporcionar una interfaz moderna para:

- Monitoreo espectral en tiempo real.
- Análisis de señales RF.
- Medición mediante markers.
- Detección de picos espectrales.
- Configuración dinámica del analizador.
- Supervisión técnica de emisiones.
- Base futura para waterfall, captura IQ y generación de reportes.

---

# Arquitectura General

BB60C Hardware
    ↓
Backend FastAPI
    ↓
REST API + WebSocket
    ↓
Frontend Vue 3 + TypeScript
    ↓
Canvas Spectrum Analyzer

---

# Tecnologías

## Backend

- Python
- FastAPI
- Uvicorn
- WebSockets
- Signal Hound BB60C API

## Frontend

- Vue 3
- TypeScript
- Composition API
- HTML5 Canvas
- CSS3

---

# Estructura del Proyecto

frontend/
│
├── src/
│   ├── components/
│   ├── composables/
│   ├── services/
│   ├── data/
│   └── assets/
│
backend/
│
├── app/
├── services/
├── spectrum/
└── main.py

---

# Componentes Frontend

## App.vue

Componente raíz.

Responsabilidades:

- Inicialización.
- Conexión al backend.
- Layout principal.
- Integración de módulos.

---

## AppHeader.vue

Cabecera institucional.

Contiene:

- Logo ENACOM.
- Logo SNCTE.
- Nombre del sistema.

---

## DevicePanel.vue

Información del instrumento.

Campos:

- Modelo.
- Estado.
- Firmware.
- Temperatura.
- Voltaje.
- Corriente.

---

## SpectrumControls.vue

Configuración RF.

Parámetros:

- Frecuencia Inicio.
- Frecuencia Fin.
- Frecuencia Central.
- Span.
- RBW.
- VBW.
- Reference Level.

Funciones:

- Aplicar configuración.
- Cargar favoritos.
- Cargar presets.

---

## SpectrumPresetSelector.vue

Selección de:

- Categoría.
- Preset RF.

Ejemplos:

- FM Comercial.
- Banda Aérea.
- LTE700.
- 5G.
- ISM 433.

---

## SpectrumStatus.vue

Resumen operacional del análisis.

Muestra:

- Equipo.
- Frecuencia Central.
- Nivel.
- Peak Frequency.
- Peak Level.
- Span.

---

## SpectrumCanvas.vue

Motor gráfico principal.

Funciones:

- Render de espectro.
- Escala dBm.
- Escala frecuencia.
- Dibujado de markers.
- Cursor.
- Peak visual.
- Max Hold.
- Average.

Funciones internas:

- draw().
- drawGrid().
- drawTrace().
- drawMarkers().
- drawCursor().
- drawSpectrum().

---

## AnalyzerTools.vue

Herramientas operativas.

Markers:

- CENTRO.
- M1.
- M2.
- M3.
- M4.
- M5.

Funciones:

- PEAK.
- DELTA.
- MAX.
- MIN.
- AVG.
- CENTRAR M1.
- LIMPIAR.

---

## MarkerBar.vue

Barra horizontal de markers.

Información por marker:

- Identificador.
- Frecuencia.
- Nivel.

---

## MarkerTable.vue

Vista detallada.

Incluye:

- Marker.
- Frecuencia.
- Nivel.
- Delta F.
- Delta P.

---

## CollapsiblePanel.vue

Panel reutilizable plegable.

Usado en:

- Estado Instrumento.
- Herramientas.
- Tabla de Markers.

---

# Composables

## useSpectrum.ts

Gestiona:

- WebSocket.
- Snapshot espectral.
- Estado de conexión.

Expone:

- spectrum.
- connect().

---

## useMarkers.ts

Repositorio global de markers.

Modelo:

- id
- enabled
- selected
- frequencyHz
- powerDbm

Markers actuales:

- CENTRO
- M1
- M2
- M3
- M4
- M5

Funciones:

- selectMarker()
- clearMarkers()

---

# Servicios

## configService.ts

Funciones:

- getSpectrumConfig()
- updateSpectrumConfig()

Responsabilidad:

Comunicación REST con backend.

---

# Backend

## API REST

Configuración:

GET /spectrum/config

POST /spectrum/config

---

## WebSocket

/ws/spectrum

Responsable de:

- Streaming espectral.
- Entrega de snapshots.

---

# Funcionalidades Implementadas

## UI

- Branding ENACOM.
- Branding SNCTE.
- Layout profesional.
- Barra lateral de control.
- Panels plegables.

## RF

- Configuración frecuencia.
- Frecuencia central.
- Span.
- Presets.
- Favoritos.

## Spectrum

- Visualización tiempo real.
- Escalas.
- Peak visual.
- Cursor.

## Markers

- CENTRO.
- M1-M5.
- Selección interactiva.
- Posicionamiento sobre espectro.
- Delta automático.

---

# Flujo Operativo

## Marker

Seleccionar marker
↓
Click en espectro
↓
Actualización de frecuencia
↓
Actualización de nivel

---

## Frecuencia Central

Seleccionar CENTRO
↓
Click en espectro
↓
Posicionamiento del centro de análisis

---

## Peak Search

PEAK
↓
Búsqueda del máximo espectral
↓
Asignación a M1

---

## Delta Marker

M1
+
M2
↓
Δ Frecuencia
Δ Nivel

---

# Estado Actual

## Completado

- UI institucional.
- Layout operativo.
- Presets RF.
- Favoritos RF.
- Marker system.
- Delta Marker.
- Spectrum Canvas.
- Device Monitoring.

## En Desarrollo

- Peak Search persistente.
- Center On Marker.
- Barra horizontal completa de markers.

---

# Roadmap

## Fase 4B

- Peak Search avanzado.
- Center Marker.
- Delta avanzado.

## Fase 4C

- Zoom.
- Pan.
- Reset View.

## Fase 4D

- Waterfall.
- Historial temporal.

## Fase 5

- Captura IQ.
- Grabación.
- Exportación CSV.
- Exportación PNG.
- Reportes PDF.

---

# Instalación

## Backend

uvicorn app.main:app --reload

## Frontend

npm install
npm run dev

---

# Licencia

Uso interno ENACOM / SNCTE.
