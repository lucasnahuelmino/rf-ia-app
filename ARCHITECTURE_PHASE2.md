# RF Monitor - Arquitectura Fase 2: ML/AI Integration

**Documento de Diseño Arquitectónico**  
**Autor**: AI Assistant  
**Fecha**: 2026-08-18  
**Estado**: Propuesta para validación  
**Versión**: 0.1

---

## Tabla de Contenidos
1. [Análisis de Estado Actual](#análisis-de-estado-actual)
2. [Principios de Diseño](#principios-de-diseño)
3. [Arquitectura Conceptual de 9 Capas](#arquitectura-conceptual-de-9-capas)
4. [Separación ML vs LLM](#separación-ml-vs-llm)
5. [Flujo de Datos Completo](#flujo-de-datos-completo)
6. [Arquitectura de Adquisición IQ/Espectro](#arquitectura-de-adquisición-iqespectro)
7. [Arquitectura de Datasets](#arquitectura-de-datasets)
8. [Arquitectura de Entrenamiento ML](#arquitectura-de-entrenamiento-ml)
9. [Arquitectura de Inferencia](#arquitectura-de-inferencia)
10. [Integración Ollama](#integración-ollama)
11. [Estructura de Carpetas Propuesta](#estructura-de-carpetas-propuesta)
12. [Modelos de Datos Completos](#modelos-de-datos-completos)
13. [Roadmap de Fases](#roadmap-de-fases)
14. [FASE 2A: Objetivos y Tareas](#fase-2a-objetivos-y-tareas)

---

## 1. Análisis de Estado Actual

### 1.1 Fortalezas de la Base Actual

```
✅ FastAPI + Uvicorn
   - Asincronismo nativo
   - WebSocket soporte
   - Arquitectura limpia

✅ BB60CAdapter implementa patrón Adapter
   - Extensible para otros dispositivos
   - Interfaz RFDevice clara
   - Encapsulación del SDK

✅ Thread-safety
   - Spectrum State con Lock
   - SpectrumWorker en daemon thread
   - Config con versionado

✅ Adquisición de Espectro
   - Ciclo de 50ms
   - Streaming WebSocket
   - Configuración dinámica
```

### 1.2 Limitaciones Actuales

```
❌ SOLO adquisición de espectro
   - NO hay captura de IQ
   - NO hay almacenamiento persistente
   - NO hay grabaciones

❌ Modelos de datos muy básicos
   - SpectrumSnapshot: timestamp + trace
   - TraceData: min/max traces
   - Sin metadatos sobre la adquisición
   - Sin información de configuración capturada

❌ Sin capas de datos
   - Sin definición de Dataset
   - Sin etiquetado
   - Sin versionado de datos
   - Sin división train/test

❌ Sin ML
   - Sin feature extraction
   - Sin modelos
   - Sin inferencia
   - Sin modelo registry

❌ Sin Ollama
   - Sin lenguaje natural
   - Sin orquestación

❌ Sin persistencia
   - Todo en memoria
   - Config se pierde al reiniciar
   - No hay auditoría de eventos
```

### 1.3 Cambios Requeridos

**Modelos de Datos**: Expandir de 2 tipos a 8+ tipos con metadata completa

**Servicios**: Pasar de 3 (device/config/spectrum) a 15+ (recording/dataset/ml/ai/storage, etc.)

**API**: Pasar de 6 endpoints a 40+ endpoints

**Frontend**: Pasar de 8 componentes a 20+ componentes

**Base de datos**: Introducir persistencia (SQLite inicialmente)

---

## 2. Principios de Diseño

### 2.1 Responsabilidad Única

```
┌─────────────────────────────────────────────────────┐
│ RF ENGINE                                           │
├─────────────────────────────────────────────────────┤
│ ✓ Controla BB60C                                   │
│ ✓ Captura espectro/IQ                              │
│ ✓ Almacena datos                                   │
│ ✗ NO interpreta datos                              │
│ ✗ NO entrena modelos                               │
│ ✗ NO habla con el usuario                          │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ ML ENGINE                                           │
├─────────────────────────────────────────────────────┤
│ ✓ Extrae características                           │
│ ✓ Entrena modelos                                  │
│ ✓ Realiza inferencia                               │
│ ✗ NO controla hardware                             │
│ ✗ NO habla con usuario (solo métricas)            │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ AI LAYER (Ollama)                                   │
├─────────────────────────────────────────────────────┤
│ ✓ Comprende lenguaje natural                       │
│ ✓ Genera intenciones estructuradas                 │
│ ✓ Interpreta resultados para el usuario            │
│ ✗ NO ejecuta comandos directamente                 │
│ ✗ NO entrena modelos                               │
│ ✗ NO accede a hardware                             │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ COMMAND ENGINE                                      │
├─────────────────────────────────────────────────────┤
│ ✓ Valida intenciones de Ollama                     │
│ ✓ Ejecuta comandos validados                       │
│ ✓ Orquesta RF + ML                                 │
│ ✗ NO interpreta lenguaje                           │
│ ✗ NO entrena                                       │
└─────────────────────────────────────────────────────┘
```

### 2.2 No Data Leakage

**Estrategia de División de Datos**:
```
Dataset
  ├─ Recording_001 (80%)  → TRAIN
  │   ├─ Session_01 → features
  │   └─ Session_02 → features
  ├─ Recording_002 (80%)  → TRAIN
  └─ Recording_003 (20%)  → TEST

✓ División por RECORDING (no por muestras)
✓ Evita leakage temporal
✓ Preserva correlaciones
```

### 2.3 Arquitectura Extensible

```
Nuevo modelo XYZ
   ↓
├─ Implementar: ModelTrainer
├─ Implementar: ModelPredictor
├─ Registrar en: ModelRegistry
├─ Agregar a: ModelEvaluator
└─ Listo para usar

SIN modificar:
  - Pipeline existente
  - Modelos anteriores
  - API
  - Frontend
```

### 2.4 Schemas Claros

Cada entidad debe tener:
- Schema Pydantic
- Validación
- Serialización JSON
- Documentación OpenAPI

---

## 3. Arquitectura Conceptual de 9 Capas

```
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 1: USER INTERFACE                                          │
│ (Vue.js Componentes)                                             │
│ - SpectrumViewer                                                 │
│ - RecordingPanel                                                 │
│ - ModelDashboard                                                 │
│ - AIChat                                                         │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 2: API GATEWAY (FastAPI Routers)                           │
│ - /devices/*                                                     │
│ - /spectrum/*                                                    │
│ - /recordings/*                                                  │
│ - /datasets/*                                                    │
│ - /models/*                                                      │
│ - /ai/*                                                          │
│ - /commands/*                                                    │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 3: COMMAND ENGINE                                          │
│ - Ollama Intent → Schema validation                              │
│ - Safety checks                                                  │
│ - Permission verification                                        │
│ - State machine                                                  │
└──────────────────────────────────────────────────────────────────┘
                         ↙        ↘
            ┌─────────────────┐  ┌──────────────────┐
            │                 │  │                  │
┌──────────────────────────┐ ┌──────────────────────────────┐
│ LAYER 4A: AI LAYER       │ │ LAYER 4B: RF ENGINE + ML    │
│ (Ollama + RAG)           │ │                              │
│ - Natural Language Proc  │ │ ┌──────────────────────────┐ │
│ - Intent Generation      │ │ │ 5A: Device Service      │ │
│ - Result Interpretation  │ │ │ - BB60C control         │ │
│ - Tool Selection         │ │ │ - Device mgmt           │ │
│                          │ │ │ - Diagnostics           │ │
│                          │ │ └──────────────────────────┘ │
│                          │ │ ┌──────────────────────────┐ │
│                          │ │ │ 5B: Acquisition Service │ │
│                          │ │ │ - Sweep capture         │ │
│                          │ │ │ - IQ recording          │ │
│                          │ │ │ - Waterfall buffer      │ │
│                          │ │ │ - Metadata collection   │ │
│                          │ │ └──────────────────────────┘ │
│                          │ │ ┌──────────────────────────┐ │
│                          │ │ │ 5C: ML Pipeline         │ │
│                          │ │ │ - Feature extraction    │ │
│                          │ │ │ - Preprocessing         │ │
│                          │ │ │ - Model inference       │ │
│                          │ │ │ - Prediction            │ │
│                          │ │ └──────────────────────────┘ │
│                          │ │ ┌──────────────────────────┐ │
│                          │ │ │ 5D: Training Service    │ │
│                          │ │ │ - Model training        │ │
│                          │ │ │ - Evaluation            │ │
│                          │ │ │ - Hyperparameter tuning │ │
│                          │ │ └──────────────────────────┘ │
│                          │ │ ┌──────────────────────────┐ │
│                          │ │ │ 5E: Dataset Service     │ │
│                          │ │ │ - Recording import      │ │
│                          │ │ │ - Labeling              │
│                          │ │ │ - Versioning            │
│                          │ │ │ - Splitting             │
│                          │ │ └──────────────────────────┘ │
└──────────────────────────┘ └──────────────────────────────┘
            │                          │
            └──────────────┬───────────┘
                           ↓
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 6: BUSINESS LOGIC SERVICES                                 │
│ - ConfigService                                                  │
│ - RecordingService                                               │
│ - StorageService                                                 │
│ - EventService                                                   │
│ - NotificationService                                            │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 7: DATA ACCESS LAYER                                       │
│ - SQLite Repository                                              │
│ - File System Manager                                            │
│ - Cache Layer                                                    │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 8: STORAGE                                                 │
│ - Local Database (SQLite)                                        │
│ - File System                                                    │
│ - Model Registry                                                 │
│ - Dataset Storage                                                │
│ - IQ Archives                                                    │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 9: HARDWARE                                                │
│ - BB60C Device                                                   │
│ - Ollama Local Server                                            │
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. Separación ML vs LLM

### 4.1 Arquitectura Conceptual

```
┌─────────────────────────────────────────────────────────────┐
│                     USUARIO                                │
│              "¿Hay interferencias?"                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
         ┌───────────────────────────────────┐
         │ OLLAMA (LLM)                      │
         │                                   │
         │ Intent: "analyze_for_interference"│
         │ Params:                           │
         │   - type: "INTERFERENCE"          │
         │   - action: "detect"              │
         └──────────────┬──────────────────┘
                        │
                        ↓
         ┌───────────────────────────────────┐
         │ COMMAND VALIDATOR                 │
         │ ✓ Validar intent                  │
         │ ✓ Validar parámetros              │
         │ ✓ Validar permisos                │
         └──────────────┬──────────────────┘
                        │
                        ↓
         ┌───────────────────────────────────┐
         │ COMMAND ENGINE                    │
         │ route → detect_interference()     │
         └──────────────┬──────────────────┘
                        │
         ┌──────────────┴──────────────────┐
         │                                 │
         ↓                                 ↓
    ┌─────────────┐          ┌──────────────────┐
    │ RF ENGINE   │          │ ML ENGINE        │
    │             │          │                  │
    │ 1. Get      │          │ 1. Extract IQ    │
    │    current  │          │    features      │
    │    snapshot │          │                  │
    │             │          │ 2. Run models:   │
    │ 2. Get      │          │  - XGBoost       │
    │    historical│          │  - RandomForest  │
    │    data     │          │  - IsolationForest
    │             │          │                  │
    └─────┬───────┘          │ 3. Aggregate    │
         │                   │    predictions   │
         │                   │                  │
         │                   │ 4. Return scores:│
         │                   │    - Class:      │
         │                   │      INTERFERENCE│
         │                   │    - Confidence: │
         │                   │      0.92        │
         │                   │    - Model: XGBoost
         └─────┬─────────────┘
               │
               ↓
         ┌───────────────────────────────────┐
         │ RESULT AGGREGATOR                 │
         │                                   │
         │ Combine RF + ML results           │
         │ Generate structured output        │
         └──────────────┬──────────────────┘
                        │
                        ↓
         ┌───────────────────────────────────┐
         │ OLLAMA (LLM)                      │
         │ Interpret results for user        │
         │                                   │
         │ Input:                            │
         │  - RF data: power levels          │
         │  - ML prediction: INTERFERENCE    │
         │  - Confidence: 0.92               │
         │                                   │
         │ Output (natural language):        │
         │ "Se detectó una posible           │
         │  interferencia en 118.2 MHz       │
         │  con probabilidad del 92%.        │
         │  La señal presenta características│
         │  de jamming. Recomiendo..."       │
         └──────────────┬──────────────────┘
                        │
                        ↓
            ┌────────────────────────┐
            │ USUARIO (respuesta)    │
            │                        │
            │ "Se detectó una posible│
            │  interferencia..."     │
            └────────────────────────┘
```

### 4.2 Responsabilidades Claras

```
┌──────────────────────────────────────────────────────────────┐
│ OLLAMA (LLM)                                                 │
├──────────────────────────────────────────────────────────────┤
│ Entrada: Lenguaje natural                                    │
│ Salida: Intent + parámetros estructurados                    │
│                                                              │
│ Ejemplo:                                                     │
│ IN:  "Monitoreá la banda de aviones durante 10 minutos"     │
│ OUT: {                                                       │
│        "action": "start_monitoring",                        │
│        "band": "AVIATION",                                   │
│        "duration_seconds": 600                              │
│      }                                                       │
│                                                              │
│ Interpretación de resultados:                               │
│ IN:  Métricas + predicciones ML                             │
│ OUT: Explicación en lenguaje natural                        │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ ML ENGINE (Modelos Clásicos)                                 │
├──────────────────────────────────────────────────────────────┤
│ Entrada: Features extraídas de IQ/Espectro                   │
│ Salida: Predicción + confianza                              │
│                                                              │
│ Ejemplo:                                                     │
│ IN:  [power, spectral_entropy, peak_count, ...]             │
│ OUT: {                                                       │
│        "class": "INTERFERENCE",                             │
│        "confidence": 0.92,                                   │
│        "model": "xgboost_v3",                                │
│        "probabilities": {                                    │
│          "NORMAL": 0.05,                                     │
│          "INTERFERENCE": 0.92,                               │
│          "NOISE": 0.03                                       │
│        }                                                     │
│      }                                                       │
│                                                              │
│ NO genera lenguaje natural                                  │
│ NO controla hardware                                         │
│ NO interpreta para usuario                                  │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ RF ENGINE                                                    │
├──────────────────────────────────────────────────────────────┤
│ Entrada: Comandos de control                                │
│ Salida: Datos de RF + metadatos                              │
│                                                              │
│ Ejemplo:                                                     │
│ IN:  {                                                       │
│        "action": "capture_sweep",                           │
│        "center_freq": 118000000,                             │
│        "span": 20000000                                      │
│      }                                                       │
│ OUT: {                                                       │
│        "timestamp": 1724073600,                              │
│        "center_freq": 118000000,                             │
│        "span": 20000000,                                     │
│        "trace": [...],                                       │
│        "peak_freq": 118245000,                               │
│        "peak_power": -72.4                                   │
│      }                                                       │
└──────────────────────────────────────────────────────────────┘
```

---

## 5. Flujo de Datos Completo

```
A) CAPTURA Y ALMACENAMIENTO
═════════════════════════════════════════════════════════════

BB60C
  ├─ Snap 1: Espectro completo (50ms) → snapshot
  │   └─ Almacenar en SpectrumState (en memoria, corta duración)
  │      └─ Stream vía WebSocket → Frontend
  │
  └─ Grabación IQ: 30 segundos @ 40 MSps (comando explícito)
      └─ Buffer de IQ (RAM)
         └─ Guardar en disco: recording_20260818_120545.iq
            └─ Crear metadata: {timestamp, config, hash, label}
               └─ Registrar en DB
                  └─ Mostrar en Dataset Browser


B) DATASET MANAGEMENT
═════════════════════════════════════════════════════════════

Recording_001.iq (30s, 1.2 GB)
  ├─ Importar a Dataset Manager
  ├─ Extraer metadatos
  ├─ Visualizar en labeler
  ├─ Etiquetar: "NORMAL"
  ├─ Versionar: recording_001_v1.iq
  └─ Asociar con Dataset "Training_Set_01"

Dataset_001
  ├─ Recording_001.iq (NORMAL)
  ├─ Recording_002.iq (INTERFERENCE)
  ├─ Recording_003.iq (NOISE)
  ├─ Recording_004.iq (NORMAL)
  └─ Metadata:
      - Created: 2026-08-18
      - Version: v1.0
      - Total samples: 1.2B
      - Classes: [NORMAL, INTERFERENCE, NOISE]
      - Split: 80% train / 20% test


C) FEATURE EXTRACTION
═════════════════════════════════════════════════════════════

Recording_001.iq (etiquetado como NORMAL)
  ↓
Segmentación:
  - Ventanas de N muestras
  - Overlap 50%
  - 1000 segmentos de 2 segundos c/u
  ↓
Para cada segmento:
  - FFT → espectro
  - Estadísticas: power, RMS, crest_factor
  - Spectral: entropy, flatness, kurtosis
  - IQ: amplitude, phase, correlation
  - Temporal: zero_crossing_rate, duty_cycle
  ↓
Output: DataFrame con 1000 filas, 40+ columnas

Etiqueta: NORMAL


D) ENTRENAMIENTO
═════════════════════════════════════════════════════════════

Dataset_001 (Dataset object)
  ├─ Validación: ✓ No data leakage detectado
  ├─ Preprocessing:
  │  ├─ Normalización (StandardScaler)
  │  ├─ Feature selection (top 20 features)
  │  └─ Balanceo de clases
  │
  ├─ Split (por recording, NO por muestras):
  │  ├─ Train: Recordings 1, 2, 3 → 20000 muestras
  │  └─ Test: Recording 4 → 5000 muestras
  │
  ├─ Entrenamiento de modelos:
  │  ├─ XGBoost:
  │  │  ├─ Parameters: depth=8, learning_rate=0.1
  │  │  ├─ Validation F1: 0.94
  │  │  └─ Test F1: 0.91
  │  │
  │  ├─ RandomForest:
  │  │  ├─ Parameters: n_trees=100
  │  │  ├─ Validation F1: 0.92
  │  │  └─ Test F1: 0.89
  │  │
  │  └─ IsolationForest (anomaly detection):
  │     ├─ Parameters: contamination=0.1
  │     └─ Test Precision: 0.88
  │
  └─ Registrar en Model Registry:
     ├─ Model ID: xgb_001_20260818_120545
     ├─ Dataset: Dataset_001_v1.0
     ├─ Features: [power, entropy, kurtosis, ...]
     ├─ Metrics: {F1: 0.91, Precision: 0.92, Recall: 0.90}
     └─ Status: READY_FOR_INFERENCE


E) INFERENCIA EN TIEMPO REAL
═════════════════════════════════════════════════════════════

Tiempo real, captura IQ continua:
  ↓
Cada 2 segundos:
  ├─ Extraer ventana de 2 segundos (80,000 muestras @ 40 MSps)
  ├─ Extraer features (40 dimensiones)
  ├─ Pasar a XGBoost (modelo en memoria)
  ├─ Obtener predicción:
  │  └─ {"class": "NORMAL", "confidence": 0.95}
  ├─ Actualizar UI:
  │  ├─ Spectrum graph
  │  ├─ Prediction badge: "NORMAL (95%)"
  │  └─ Confidence gauge
  └─ Guardar evento:
     └─ Event DB: timestamp, freq, class, confidence


F) OLLAMA INTEGRATION
═════════════════════════════════════════════════════════════

Usuario: "¿Hay interferencias?"
  ↓
Ollama LLM:
  1. Parse input → intent: "detect_interference"
  2. Llamar tool: get_recent_detections()
  3. Backend retorna:
     [{
       "timestamp": 1724073600,
       "frequency": 118245000,
       "power": -72.4,
       "classification": "INTERFERENCE",
       "confidence": 0.91
     }]
  4. Ollama interpreta y responde:
     "Sí, se detectó una interferencia hace 2 minutos
      en 118.2 MHz con confianza del 91%.
      La señal presenta características de jamming.
      Recomiendo monitorear esta frecuencia."
  ↓
Usuario lee respuesta
```

---

## 6. Arquitectura de Adquisición IQ/Espectro

### 6.1 Tipos de Adquisición

```
TIPO A: SWEEP (Espectro)
─────────────────────────
Parámetro      │ Valor Actual  │ Descripción
───────────────┼───────────────┼──────────────────────
Modo           │ Sweep         │ Captura espectro 2D
Frecuencia Cen │ 124.65 MHz    │ Configurable
Span           │ 5 MHz         │ Configurable
RBW            │ 10 kHz        │ Resolución
VBW            │ 10 kHz        │ Video BW
Ref Level      │ 0 dBm         │ Nivel referencia
Duración       │ 50 ms         │ Ciclo fijo
Output         │ Trace array   │ Valores de potencia
Almacenamiento │ Memoria corta │ 1-2 seg máx
Uso            │ Monitoreo RT  │ UI streaming


TIPO B: IQ RECORDING (Datos I/Q)
────────────────────────────────
Parámetro      │ Valor Nuevo   │ Descripción
───────────────┼───────────────┼──────────────────────
Modo           │ IQ            │ Captura componentes I/Q
Frecuencia Cen │ Variable      │ Configurable
Bandwidth      │ Variable      │ 1-40 MHz típico
Sample Rate    │ Variable      │ 40-125 MSps típico
Duración       │ Configurable  │ 1-3600 segundos
Tamaño Max     │ Configurable  │ GB (memoria/disco)
Output         │ IQ pairs      │ Complejos de 32 bits
Almacenamiento │ Disco SSD     │ Archivos .iq
Uso            │ Análisis ML   │ Datasets, feature ext.
Format         │ HDF5/NPZ      │ (a determinar)
Metadata       │ Completa      │ Timestamp, config, hash
```

### 6.2 Modelos de Datos Ampliados

```python
# ADQUISICIÓN BASE - Metadatos comunes
@dataclass
class AcquisitionMetadata:
    timestamp_utc: float              # Unix timestamp (UTC)
    device_id: str                    # "BB60C_SN123456"
    serial_number: int                # Serial del dispositivo
    device_type: str                  # "BB60C", "BB60D", etc.
    firmware_version: str             # "v3.2.1"
    api_version: str                  # "3.0.0"
    
    # Configuración RF en el momento de captura
    center_frequency_hz: float        # Frecuencia central
    span_hz: float                    # Span (sweep/IQ bandwidth)
    start_frequency_hz: float         # Freq inicio
    stop_frequency_hz: float          # Freq fin
    rbw_hz: float                     # Resolution BW
    vbw_hz: float                     # Video BW
    reference_level_dbm: float        # Nivel referencia
    attenuation_db: float             # Atenuación (si aplica)
    detector_type: str                # "AVERAGE", "PEAK", "MIN", etc.
    
    # Información de adquisición
    acquisition_mode: str             # "SWEEP" o "IQ"
    sample_rate_sps: Optional[float]  # Para IQ
    sample_count: Optional[int]       # Para IQ
    duration_seconds: Optional[float] # Duración
    
    # GPS (futuro)
    gps_latitude: Optional[float]     = None
    gps_longitude: Optional[float]    = None
    gps_altitude_m: Optional[float]   = None
    gps_timestamp: Optional[float]    = None
    
    # Metadatos adicionales
    location_name: Optional[str]      = None  # "Oficina", "Calle X"
    operator_name: Optional[str]      = None
    notes: Optional[str]              = None
    environment: Optional[str]        = None  # "Indoor", "Outdoor", etc.
    
    # Datos de calidad
    sample_loss_detected: bool        = False
    iq_imbalance_db: Optional[float]  = None
    dc_offset: Optional[float]        = None
    frequency_error_hz: Optional[float] = None
    
    # Control de versiones
    file_hash: Optional[str]          = None  # SHA256 del archivo
    file_format: Optional[str]        = None  # "HDF5", "NPZ", "WAV", etc.
    file_size_bytes: Optional[int]    = None
    compression: Optional[str]        = None  # "None", "GZIP", etc.


# SWEEP SNAPSHOT - Datos de espectro instantáneo
@dataclass
class SpectrumSnapshot:
    metadata: AcquisitionMetadata
    
    # Información de la traza
    trace: np.ndarray                 # Array de potencias (dBm)
    trace_length: int                 # Cantidad de puntos
    bin_size_hz: float                # Ancho de cada bin
    
    # Estadísticas de potencia
    peak_frequency_hz: float          # Freq del pico
    peak_power_dbm: float             # Potencia del pico
    noise_floor_dbm: float            # Piso de ruido
    occupied_bandwidth_hz: float      # BW ocupado
    
    # Trazas adicionales (si disponibles)
    max_hold: Optional[np.ndarray]    = None
    min_hold: Optional[np.ndarray]    = None
    average_trace: Optional[np.ndarray] = None


# IQ RECORDING - Datos de I/Q complejos
@dataclass
class IQRecording:
    metadata: AcquisitionMetadata
    
    # Datos IQ
    iq_data: np.ndarray               # Shape (N,) de complex64
    
    # Estadísticas IQ
    power_watts: float
    peak_to_average_ratio_db: float
    crest_factor: float
    
    # Detectores disponibles
    detector_min: Optional[np.ndarray] = None
    detector_max: Optional[np.ndarray] = None
    detector_avg: Optional[np.ndarray] = None
```

### 6.3 Servicios de Adquisición

```python
# AcquisitionService (nuevo)
class AcquisitionService:
    
    # Sweep
    def start_sweep(config: SweepConfig) → StreamID
    def stop_sweep(stream_id: StreamID) → None
    def get_current_sweep() → SpectrumSnapshot
    
    # IQ Recording
    def start_iq_recording(config: IQConfig) → RecordingID
    def stop_iq_recording(recording_id: RecordingID) → RecordingFile
    def get_iq_recording_status(recording_id: RecordingID) → Status
    def get_iq_recording_progress(recording_id: RecordingID) → ProgressInfo
    
    # Storage
    def save_recording(recording: IQRecording, path: str) → RecordingID
    def load_recording(recording_id: RecordingID) → IQRecording
    def list_recordings() → List[RecordingMetadata]
    def delete_recording(recording_id: RecordingID) → None
```

---

## 7. Arquitectura de Datasets

### 7.1 Dataset Workflow

```
┌─────────────────────────────────────────────────────┐
│ Recording Repository                                │
│ (Carpeta con archivos .iq)                          │
└────────────────┬────────────────────────────────────┘
                 │
                 ↓
     ┌─────────────────────────┐
     │ Dataset Import          │
     │ (Batch load + validate) │
     └────────────┬────────────┘
                  │
                  ↓
     ┌──────────────────────────────┐
     │ Data Quality Checks          │
     │ - Duplicates detection       │
     │ - Corruption detection       │
     │ - Sample loss check          │
     │ - Class balance              │
     └────────────┬─────────────────┘
                  │
                  ↓
     ┌──────────────────────────────┐
     │ Labeling Interface           │
     │ (Manual o semi-auto)         │
     │ - Spectrum viewer            │
     │ - Waterfall viewer           │
     │ - Class selector             │
     │ - Time segment selection     │
     └────────────┬─────────────────┘
                  │
                  ↓
     ┌──────────────────────────────┐
     │ Dataset Versioning           │
     │ dataset_v1.0                 │
     │ dataset_v1.1 (fixes)         │
     │ dataset_v2.0 (new classes)   │
     └────────────┬─────────────────┘
                  │
                  ↓
     ┌──────────────────────────────┐
     │ Split Strategy               │
     │ - By recording (preferred)   │
     │ - By session                 │
     │ - By scenario                │
     │ - Train/Val/Test ratios      │
     └────────────┬─────────────────┘
                  │
                  ↓
     ┌──────────────────────────────┐
     │ Feature Extraction Pipeline  │
     │ - Segmentation              │
     │ - Feature computation       │
     │ - Normalization             │
     │ - Feature selection         │
     └────────────┬─────────────────┘
                  │
                  ↓
     ┌──────────────────────────────┐
     │ Dataset Ready for Training   │
     │ (Encoded + validated)        │
     └──────────────────────────────┘


# DatasetManager (nuevo)
class DatasetManager:
    
    # Import
    def import_recordings(path: str, glob: str = "*.iq") → ImportResult
    
    # Validation
    def validate_dataset(dataset_id: str) → ValidationReport
    def detect_duplicates(dataset_id: str) → List[DuplicateGroup]
    def detect_corruption(dataset_id: str) → List[CorruptionReport]
    
    # Labeling
    def get_labeling_batch(dataset_id: str, batch_size: int) → RecordingBatch
    def label_recording(recording_id: str, label: str, segments: List[Segment]) → None
    def label_batch(labels: Dict[str, str]) → None
    
    # Versioning
    def create_version(dataset_id: str, version: str, notes: str) → DatasetVersion
    def list_versions(dataset_id: str) → List[DatasetVersion]
    def checkout_version(dataset_id: str, version: str) → None
    
    # Splitting
    def split_dataset(dataset_id: str, strategy: SplitStrategy, ratios: Dict) → SplitResult
    def get_split_info(dataset_id: str) → SplitInfo
    
    # Export
    def export_for_training(dataset_id: str, format: str = "parquet") → Path
    def export_metadata(dataset_id: str) → Dict
```

### 7.2 Dataset Schema

```python
@dataclass
class Dataset:
    id: str                          # "dataset_001"
    name: str                        # "RF Interference Detection v1"
    description: str
    created_at: datetime
    updated_at: datetime
    
    # Composición
    recordings: List[RecordingMetadata]  # Qué grabaciones contiene
    total_samples: int               # Total de IQ samples
    duration_seconds: float          # Duración total
    
    # Clases
    classes: Dict[str, int]          # {"NORMAL": 150, "INTERFERENCE": 50}
    class_descriptions: Dict[str, str]
    
    # Balanceo
    class_weights: Optional[Dict[str, float]]  # Para loss function
    is_balanced: bool
    
    # Metadatos de split
    train_recordings: List[str]
    val_recordings: List[str]
    test_recordings: List[str]
    
    # Features
    feature_names: List[str]         # Nombres de features
    feature_count: int
    feature_preprocessing: Dict      # StandardScaler params, etc.
    
    # Versioning
    version: str                     # "v1.0.0"
    parent_version: Optional[str]    # Para tracking de changes
    changelog: List[str]             # Qué cambió en cada versión
    
    # Calidad
    data_leakage_checked: bool
    duplicate_check_passed: bool
    corruption_check_passed: bool
    
    # Almacenamiento
    storage_path: Path
    storage_format: str              # "HDF5", "Parquet", etc.
```

---

## 8. Arquitectura de Entrenamiento ML

### 8.1 Pipeline de Entrenamiento

```
Dataset_001 (validado)
  │
  ├─ Split validation
  │  └─ ✓ No leakage
  │
  ├─ Preprocessing
  │  ├─ Normalización (StandardScaler)
  │  ├─ Feature selection
  │  ├─ Balanceo de clases
  │  └─ Encoding de categorías
  │
  ├─ Train Model 1: XGBoost
  │  ├─ Hyperparameters:
  │  │  - max_depth: [5, 8, 10]
  │  │  - learning_rate: [0.01, 0.1]
  │  │  - n_estimators: [100, 200]
  │  │
  │  ├─ Validation:
  │  │  - Cross-validation (5-fold)
  │  │  - Val metrics: F1=0.94, Precision=0.93
  │  │
  │  └─ Test:
  │     - Test metrics: F1=0.91, Precision=0.92
  │     - Confusion matrix
  │     - ROC curve
  │
  ├─ Train Model 2: RandomForest
  │  ├─ Hyperparameters
  │  ├─ Validation
  │  └─ Test
  │
  ├─ Train Model 3: IsolationForest
  │  ├─ Hyperparameters
  │  ├─ Validation
  │  └─ Test
  │
  └─ Model Registry
     ├─ Save best models
     ├─ Store metrics
     ├─ Store hyperparams
     └─ Generate comparison report


# TrainingService (nuevo)
class TrainingService:
    
    # Training
    def train_model(
        dataset_id: str,
        model_type: str,  # "xgboost", "random_forest", etc.
        hyperparams: Dict,
        validation_strategy: str = "cross_validation"
    ) → TrainingResult
    
    # Evaluation
    def evaluate_model(
        model_id: str,
        dataset_id: str,
        split: str = "test"
    ) → EvaluationMetrics
    
    def compare_models(
        model_ids: List[str],
        dataset_id: str
    ) → ComparisonReport
    
    # Hyperparameter tuning
    def tune_hyperparameters(
        dataset_id: str,
        model_type: str,
        param_grid: Dict,
        cv_folds: int = 5
    ) → TuningResult
```

### 8.2 Modelos Soportados

```python
# Interfaz base
class ModelTrainer(ABC):
    @abstractmethod
    def train(
        X_train: np.ndarray,
        y_train: np.ndarray,
        hyperparams: Dict
    ) → TrainedModel
    
    @abstractmethod
    def validate(
        X_val: np.ndarray,
        y_val: np.ndarray
    ) → ValidationMetrics


# Implementaciones concretas
class XGBoostTrainer(ModelTrainer):
    def train(...) → XGBModel
    def validate(...) → ValidationMetrics

class RandomForestTrainer(ModelTrainer):
    def train(...) → RFModel
    def validate(...) → ValidationMetrics

class IsolationForestTrainer(ModelTrainer):
    def train(...) → IFModel
    def validate(...) → ValidationMetrics

# Futuros (a agregar sin modificar código existente)
class KNNTrainer(ModelTrainer):
    pass

class MLPTrainer(ModelTrainer):
    pass

class CNNTrainer(ModelTrainer):
    pass


# Factory pattern para instanciar
class ModelFactory:
    @staticmethod
    def create_trainer(model_type: str) → ModelTrainer:
        trainers = {
            "xgboost": XGBoostTrainer,
            "random_forest": RandomForestTrainer,
            "isolation_forest": IsolationForestTrainer,
        }
        return trainers[model_type]()
```

### 8.3 Métricas

```python
@dataclass
class EvaluationMetrics:
    # Clasificación
    accuracy: float
    precision: float            # TP / (TP + FP)
    recall: float               # TP / (TP + FN)
    f1: float                   # 2 * (precision * recall) / (precision + recall)
    
    # Multiclass
    weighted_f1: float
    macro_f1: float
    
    # Ranking
    roc_auc: Optional[float]    # Area bajo la curva ROC
    pr_auc: Optional[float]     # Area bajo la curva Precision-Recall
    
    # Anomalía
    precision_anomaly: Optional[float]
    recall_anomaly: Optional[float]
    
    # Matriz de confusión
    confusion_matrix: np.ndarray
    class_report: Dict           # Precision/recall por clase
    
    # Curvas (serializable)
    roc_curve: Optional[List[Tuple[float, float]]]
    pr_curve: Optional[List[Tuple[float, float]]]


@dataclass
class ValidationMetrics:
    fold: int
    metrics: EvaluationMetrics
    training_time_seconds: float
    inference_time_ms: float


@dataclass
class TrainingResult:
    model_id: str
    model_type: str
    dataset_id: str
    training_date: datetime
    hyperparameters: Dict
    
    # Resultados
    train_metrics: EvaluationMetrics
    val_metrics: Optional[List[ValidationMetrics]]  # Si cross-val
    test_metrics: Optional[EvaluationMetrics]
    
    # Recursos
    training_time_seconds: float
    memory_used_mb: float
    
    # Modelo
    model_file_path: Path
    feature_names: List[str]
    feature_preprocessing_params: Dict
    
    # Calidad
    ready_for_inference: bool = True
    notes: Optional[str] = None
```

---

## 9. Arquitectura de Inferencia

### 9.1 Predicción en Tiempo Real

```
Real-time IQ stream (40 MSps)
  │
  ├─ Cada 2 segundos:
  │  ├─ Extraer ventana (80K muestras)
  │  ├─ [FEATURE EXTRACTION]
  │  │  └─ 40 features en 50ms
  │  ├─ [INFERENCE] (modelo en memoria)
  │  │  └─ Predicción en <10ms
  │  ├─ [RESULT AGGREGATION]
  │  │  └─ Ensemble si múltiples modelos
  │  └─ Update UI + save event
  │
  └─ Latencia total: ~100ms (acceptable para RT)


# PredictionService (nuevo)
class PredictionService:
    
    def __init__(self):
        self.models: Dict[str, LoadedModel] = {}
        self.feature_extractor = FeatureExtractor()
    
    def load_model(self, model_id: str) → None:
        """Cargar modelo en memoria"""
        model_registry.load_model(model_id)
        self.models[model_id] = loaded_model
    
    def predict(
        self,
        iq_window: np.ndarray,
        model_ids: List[str] = None
    ) → PredictionResult:
        """
        Predicción single window
        """
        features = self.feature_extractor.extract(iq_window)
        
        if model_ids is None:
            model_ids = [m for m in self.models.keys()]
        
        predictions = []
        for model_id in model_ids:
            pred = self.models[model_id].predict(features)
            predictions.append(pred)
        
        return self._aggregate_predictions(predictions)
    
    def predict_stream(
        self,
        iq_stream: IQStream,
        window_size: int,
        model_ids: List[str]
    ) → Generator[PredictionResult]:
        """
        Predicción streaming
        Yield prediction cada window_size samples
        """
        for window in iq_stream.windows(window_size):
            yield self.predict(window, model_ids)
    
    def predict_recording(
        self,
        recording_path: str,
        model_ids: List[str]
    ) → RecordingPredictions:
        """
        Predicción sobre archivo
        """
        recording = IQRecording.load(recording_path)
        results = []
        
        for window in recording.windows():
            results.append(self.predict(window, model_ids))
        
        return RecordingPredictions(recording.metadata, results)


@dataclass
class PredictionResult:
    timestamp: float
    
    # Predicción principal
    predicted_class: str
    confidence: float
    
    # Probabilidades por clase
    class_probabilities: Dict[str, float]
    
    # Ensemble info (si múltiples modelos)
    model_predictions: Dict[str, str]  # {"xgboost": "NORMAL", "rf": "NORMAL"}
    model_confidences: Dict[str, float]
    ensemble_method: str               # "majority_vote", "weighted_avg", etc.
    
    # Información de inferencia
    inference_time_ms: float
    features_used: int
    model_ids: List[str]
    
    # Contexto
    frequency_hz: Optional[float]      # Si se conoce
    power_dbm: Optional[float]         # Si se conoce
```

### 9.2 Model Registry

```python
class ModelRegistry:
    """
    Almacena modelos entrenados y metadata
    """
    
    def save_model(
        self,
        model: TrainedModel,
        result: TrainingResult
    ) → str:
        """
        Guardar modelo con metadata completa
        Retorna model_id
        """
        model_id = f"{result.model_type}_{timestamp}"
        
        # Guardar archivo .pkl/h5/joblib
        model_path = self.storage_path / f"{model_id}.pkl"
        joblib.dump(model, model_path)
        
        # Guardar metadata en DB
        self.db.insert_model_record({
            "id": model_id,
            "type": result.model_type,
            "dataset_id": result.dataset_id,
            "training_date": result.training_date,
            "hyperparameters": result.hyperparameters,
            "metrics": result.test_metrics.to_dict(),
            "features": result.feature_names,
            "preprocessing": result.feature_preprocessing_params,
            "status": "READY",
            "file_path": str(model_path),
        })
        
        return model_id
    
    def load_model(self, model_id: str) → TrainedModel:
        """Cargar modelo del disco"""
        record = self.db.get_model(model_id)
        model = joblib.load(record["file_path"])
        return model
    
    def get_model_info(self, model_id: str) → Dict:
        """Información completa del modelo"""
        return self.db.get_model(model_id)
    
    def list_models(
        self,
        model_type: str = None,
        dataset_id: str = None,
        status: str = "READY"
    ) → List[Dict]:
        """Listar modelos con filtros"""
        return self.db.query_models(model_type, dataset_id, status)
    
    def compare_models(
        self,
        model_ids: List[str]
    ) → ComparisonTable:
        """
        Comparar métricas de múltiples modelos
        Retorna tabla con columnas:
        - Model ID
        - Type
        - Dataset
        - Accuracy
        - Precision
        - Recall
        - F1
        - Training time
        """
        rows = []
        for model_id in model_ids:
            info = self.get_model_info(model_id)
            rows.append({
                "model_id": info["id"],
                "type": info["type"],
                "dataset": info["dataset_id"],
                "accuracy": info["metrics"]["accuracy"],
                "precision": info["metrics"]["precision"],
                "recall": info["metrics"]["recall"],
                "f1": info["metrics"]["f1"],
                "roc_auc": info["metrics"]["roc_auc"],
                "training_time": info["metrics"]["training_time_seconds"],
            })
        return ComparisonTable(rows)
```

---

## 10. Integración Ollama

### 10.1 Arquitectura

```
User Input (natural language)
  │
  ↓
┌─────────────────────────────┐
│ Ollama LLM                  │
│                             │
│ System prompt:              │
│ "You are an RF monitoring   │
│  assistant. Use the tools   │
│  available to help the      │
│  user."                     │
└────────┬────────────────────┘
         │
         ├─ Option A: Tool calling (preferred si soporta)
         │  └─ Ollama genera JSON con tool name + params
         │
         └─ Option B: Structured output
            └─ Ollama genera JSON según schema definido
                │
                ↓
         ┌────────────────────────────┐
         │ Backend (FastAPI)          │
         │                            │
         │ 1. Parsear response        │
         │ 2. Validar intent/params   │
         │ 3. Ejecutar tool           │
         │ 4. Retornar resultado      │
         └────────────────────────────┘
                │
                ↓
         Llamar RF/ML services
                │
                ↓
         Resultado estructurado
                │
                ↓
         Enviar de vuelta a Ollama
         "Aquí hay los datos..."
                │
                ↓
         Ollama interpreta y responde
         en lenguaje natural


# OllamaService (nuevo)
class OllamaService:
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.client = requests.Session()
        self.base_url = base_url
        self.model = "llama2"  # Configurable
        self.system_prompt = SYSTEM_PROMPT
    
    def set_model(self, model_name: str) → None:
        """Cambiar modelo (e.g., "mistral", "neural-chat")"""
        self.model = model_name
    
    def generate_intent(
        self,
        user_input: str,
        context: Optional[Dict] = None
    ) → IntentResponse:
        """
        Convertir lenguaje natural en intent + parámetros
        """
        prompt = f"""
        {self.system_prompt}
        
        Context: {context or {}}
        
        User: {user_input}
        
        Generate a JSON response with:
        - action: string (what to do)
        - parameters: object (what parameters)
        
        Example:
        {{"action": "start_monitoring", "parameters": {{"band": "AVIATION", "duration_seconds": 600}}}}
        """
        
        response = self.client.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            }
        )
        
        # Parse JSON from response
        intent = IntentResponse.parse(response.json()["response"])
        return intent
    
    def interpret_results(
        self,
        user_input: str,
        analysis_result: Dict
    ) → str:
        """
        Convertir resultados de análisis en
        explicación en lenguaje natural
        """
        prompt = f"""
        {self.system_prompt}
        
        User asked: {user_input}
        
        Analysis results:
        {json.dumps(analysis_result, indent=2)}
        
        Explain these results in natural language.
        Be concise and informative.
        """
        
        response = self.client.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            }
        )
        
        return response.json()["response"]
    
    def chat_with_context(
        self,
        user_input: str,
        conversation_history: List[Dict]
    ) → str:
        """
        Chat con historial de conversación
        """
        messages = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in conversation_history
        ])
        
        prompt = f"""
        {self.system_prompt}
        
        Conversation history:
        {messages}
        
        USER: {user_input}
        ASSISTANT:
        """
        
        response = self.client.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            }
        )
        
        return response.json()["response"]


@dataclass
class IntentResponse:
    action: str                  # "start_monitoring", "analyze", etc.
    parameters: Dict[str, Any]   # Parámetros específicos
    confidence: float            # 0.0-1.0 (parsed from Ollama)
    raw_response: str            # Respuesta original
    
    @classmethod
    def parse(cls, response: str) -> "IntentResponse":
        """Parse JSON from Ollama response"""
        # Extraer JSON del response (puede haber texto antes/después)
        try:
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return cls(
                    action=data.get("action", "unknown"),
                    parameters=data.get("parameters", {}),
                    confidence=data.get("confidence", 1.0),
                    raw_response=response,
                )
        except json.JSONDecodeError:
            pass
        
        # Fallback si no puede parsear
        return cls(
            action="unknown",
            parameters={},
            confidence=0.5,
            raw_response=response,
        )
```

### 10.2 Tools Disponibles para Ollama

```python
# CommandService con tools para Ollama
class CommandService:
    """
    Expone herramientas que Ollama puede llamar
    """
    
    # Herramientas de dispositivo
    @tool
    def get_device_status(self) → Dict:
        """Obtener estado del dispositivo"""
        return device_service.get_diagnostics()
    
    @tool
    def get_current_configuration(self) → Dict:
        """Obtener configuración RF actual"""
        return config_service.get_config()
    
    @tool
    def configure_frequency(self, center_hz: int, span_hz: int) → Dict:
        """Configurar frecuencia central y span"""
        return config_service.update_config({
            "center_frequency_hz": center_hz,
            "span_hz": span_hz,
        })
    
    @tool
    def configure_rbw(self, rbw_hz: int) → Dict:
        """Configurar RBW"""
        return config_service.update_config({"rbw_hz": rbw_hz})
    
    # Herramientas de captura
    @tool
    def start_sweep(self) → Dict:
        """Iniciar captura de espectro"""
        acquisition_service.start_sweep()
        return {"status": "sweep_started"}
    
    @tool
    def stop_sweep(self) → Dict:
        """Detener captura de espectro"""
        acquisition_service.stop_sweep()
        return {"status": "sweep_stopped"}
    
    @tool
    def start_iq_recording(self, duration_seconds: int) → Dict:
        """Iniciar grabación IQ"""
        rec_id = acquisition_service.start_iq_recording(duration_seconds)
        return {"recording_id": rec_id, "status": "recording"}
    
    @tool
    def stop_iq_recording(self, recording_id: str) → Dict:
        """Detener grabación IQ"""
        result = acquisition_service.stop_iq_recording(recording_id)
        return {"status": "stopped", "file": result.file_path}
    
    # Herramientas de análisis
    @tool
    def get_peak_list(self, top_n: int = 5) → List[Dict]:
        """Obtener lista de picos detectados"""
        snapshot = spectrum_service.get_current_spectrum()
        # Calcular picos
        peaks = analyze_peaks(snapshot.trace, top_n)
        return peaks
    
    @tool
    def get_recent_detections(self, limit: int = 10) → List[Dict]:
        """Obtener detecciones recientes de ML"""
        return event_service.get_recent_predictions(limit)
    
    @tool
    def analyze_segment(self, recording_id: str, start_s: float, end_s: float) → Dict:
        """Analizar un segmento específico"""
        recording = acquisition_service.load_recording(recording_id)
        segment = recording.get_segment(start_s, end_s)
        result = ml_service.predict(segment)
        return result.to_dict()
    
    # Herramientas de modelo
    @tool
    def get_model_list(self) → List[Dict]:
        """Listar modelos disponibles"""
        models = model_registry.list_models(status="READY")
        return [{"id": m["id"], "type": m["type"], "f1": m["metrics"]["f1"]} for m in models]
    
    @tool
    def get_model_status(self, model_id: str) → Dict:
        """Obtener información de un modelo"""
        return model_registry.get_model_info(model_id)
    
    @tool
    def run_model_prediction(self, model_id: str, recording_id: str) → Dict:
        """Ejecutar predicción con un modelo sobre un archivo"""
        recording = acquisition_service.load_recording(recording_id)
        result = prediction_service.predict_recording(recording.path, [model_id])
        return result.to_dict()
    
    # Herramientas de datos
    @tool
    def get_dataset_list(self) → List[Dict]:
        """Listar datasets disponibles"""
        return dataset_manager.list_datasets()
    
    @tool
    def get_recording_list(self) → List[Dict]:
        """Listar grabaciones disponibles"""
        return acquisition_service.list_recordings()
    
    @tool
    def export_data(self, recording_id: str, format: str = "csv") → Dict:
        """Exportar datos"""
        path = acquisition_service.export_recording(recording_id, format)
        return {"status": "exported", "path": str(path)}
```

### 10.3 Ejemplo de Flujo

```
USER:
"Analizá esta grabación y decime si hay interferencias"

OLLAMA:
{
  "action": "analyze_for_interference",
  "parameters": {
    "recording_id": "recording_001",
    "model_id": "xgboost_001"
  }
}

BACKEND:
1. Validar: recording_001 existe? ✓
2. Validar: modelo listo? ✓
3. Ejecutar: model.predict(recording_001)
4. Retornar: {
     "classification": "INTERFERENCE",
     "confidence": 0.91,
     "details": {...}
   }

OLLAMA (segunda llamada):
Interpret results:

Input:
- User preguntó: "¿Hay interferencias?"
- Analysis found: Classification=INTERFERENCE, confidence=91%
- Details: [power_levels, spectral_info]

Output:
"Sí, se detectó una interferencia con el 91% de confianza.
 La señal presenta características de jamming activo en la banda de 118-136 MHz.
 Recomiendo aplicar filtros adicionales o cambiar a frecuencia alternativa."

USER:
"Sí, mirá interferencias de tipo jamming"
```

---

## 11. Estructura de Carpetas Propuesta

```
rf-ia-app/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py (modificado: agregar routers nuevos)
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── health.py (sin cambios)
│   │   │   │   ├── devices.py (sin cambios)
│   │   │   │   ├── spectrum.py (sin cambios)
│   │   │   │   ├── ws_spectrum.py (sin cambios)
│   │   │   │   ├── config.py (sin cambios)
│   │   │   │   │
│   │   │   │   ├── recordings.py (NUEVO)
│   │   │   │   ├── datasets.py (NUEVO)
│   │   │   │   ├── models.py (NUEVO)
│   │   │   │   ├── training.py (NUEVO)
│   │   │   │   ├── inference.py (NUEVO)
│   │   │   │   ├── ai.py (NUEVO)
│   │   │   │   └── commands.py (NUEVO)
│   │   │   │
│   │   │   └── schemas/
│   │   │       ├── __init__.py
│   │   │       ├── spectrum.py (sin cambios)
│   │   │       ├── acquisition.py (NUEVO)
│   │   │       ├── datasets.py (NUEVO)
│   │   │       ├── training.py (NUEVO)
│   │   │       ├── inference.py (NUEVO)
│   │   │       └── ai.py (NUEVO)
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py (variables de config globales)
│   │   │   ├── settings.py (NUEVO, pydantic settings desde .env)
│   │   │   ├── logging.py (NUEVO, configuración de logging)
│   │   │   └── security.py (NUEVO, validación de commands)
│   │   │
│   │   ├── devices/
│   │   │   ├── __init__.py
│   │   │   └── bb60c/
│   │   │       ├── __init__.py
│   │   │       ├── adapter.py (sin cambios)
│   │   │       ├── exceptions.py (sin cambios)
│   │   │       ├── interfaces.py (sin cambios)
│   │   │       ├── models.py (sin cambios)
│   │   │       ├── diagnostics.py (sin cambios)
│   │   │       ├── sdk/
│   │   │       │   ├── __init__.py
│   │   │       │   └── bb_api.py (sin cambios)
│   │   │       └── iq_capture.py (NUEVO, grabación IQ)
│   │   │
│   │   ├── rf/
│   │   │   ├── __init__.py
│   │   │   ├── config.py (sin cambios)
│   │   │   ├── models.py (MODIFICADO, agregar nuevos modelos)
│   │   │   ├── state.py (sin cambios)
│   │   │   ├── spectrum_worker.py (sin cambios)
│   │   │   └── acquisition_worker.py (NUEVO, para IQ)
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── device_service.py (sin cambios)
│   │   │   ├── spectrum_service.py (sin cambios)
│   │   │   ├── config_service.py (sin cambios)
│   │   │   │
│   │   │   ├── acquisition_service.py (NUEVO)
│   │   │   ├── recording_service.py (NUEVO)
│   │   │   ├── storage_service.py (NUEVO)
│   │   │   └── event_service.py (NUEVO)
│   │   │
│   │   ├── ml/
│   │   │   ├── __init__.py
│   │   │   ├── feature/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── extractor.py (NUEVO)
│   │   │   │   ├── preprocessing.py (NUEVO)
│   │   │   │   └── features.py (NUEVO, definiciones de features)
│   │   │   │
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py (NUEVO, interfaz base)
│   │   │   │   ├── xgboost.py (NUEVO)
│   │   │   │   ├── random_forest.py (NUEVO)
│   │   │   │   ├── isolation_forest.py (NUEVO)
│   │   │   │   └── factory.py (NUEVO, ModelFactory)
│   │   │   │
│   │   │   ├── training/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── trainer.py (NUEVO)
│   │   │   │   ├── evaluator.py (NUEVO)
│   │   │   │   ├── validator.py (NUEVO, para evitar data leakage)
│   │   │   │   └── hyperparameter_tuning.py (NUEVO)
│   │   │   │
│   │   │   ├── inference/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── predictor.py (NUEVO)
│   │   │   │   ├── registry.py (NUEVO, ModelRegistry)
│   │   │   │   └── ensemble.py (NUEVO)
│   │   │   │
│   │   │   └── services/
│   │   │       ├── __init__.py
│   │   │       ├── training_service.py (NUEVO)
│   │   │       ├── prediction_service.py (NUEVO)
│   │   │       └── model_registry_service.py (NUEVO)
│   │   │
│   │   ├── datasets/
│   │   │   ├── __init__.py
│   │   │   ├── dataset.py (NUEVO, Dataset model)
│   │   │   ├── manager.py (NUEVO, DatasetManager)
│   │   │   ├── validators.py (NUEVO, validación de datos)
│   │   │   ├── splits.py (NUEVO, estrategias de split)
│   │   │   └── services/
│   │   │       ├── __init__.py
│   │   │       └── dataset_service.py (NUEVO)
│   │   │
│   │   ├── ai/
│   │   │   ├── __init__.py
│   │   │   ├── ollama_service.py (NUEVO)
│   │   │   ├── command_engine.py (NUEVO)
│   │   │   ├── intent_validator.py (NUEVO)
│   │   │   ├── tools.py (NUEVO, herramientas para Ollama)
│   │   │   └── prompts.py (NUEVO, system prompts)
│   │   │
│   │   └── storage/
│   │       ├── __init__.py
│   │       ├── database.py (NUEVO, SQLite operations)
│   │       ├── file_manager.py (NUEVO)
│   │       └── models/
│   │           ├── __init__.py
│   │           ├── recording.py (NUEVO, ORM)
│   │           ├── dataset.py (NUEVO, ORM)
│   │           ├── model.py (NUEVO, ORM)
│   │           └── event.py (NUEVO, ORM)
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py (sin cambios)
│   │   ├── test_adapter_hardware.py (sin cambios)
│   │   ├── test_connect_disconnect_stress.py (sin cambios)
│   │   ├── test_device_service.py (sin cambios)
│   │   │
│   │   ├── ml/ (NUEVO)
│   │   │   ├── __init__.py
│   │   │   ├── test_feature_extraction.py
│   │   │   ├── test_training.py
│   │   │   ├── test_inference.py
│   │   │   └── test_no_leakage.py
│   │   │
│   │   ├── datasets/ (NUEVO)
│   │   │   ├── __init__.py
│   │   │   ├── test_dataset_manager.py
│   │   │   └── test_data_validation.py
│   │   │
│   │   ├── ai/ (NUEVO)
│   │   │   ├── __init__.py
│   │   │   ├── test_ollama_service.py
│   │   │   └── test_command_engine.py
│   │   │
│   │   └── integration/ (NUEVO)
│   │       ├── __init__.py
│   │       └── test_e2e_pipeline.py
│   │
│   ├── data/ (NUEVO, almacenamiento local)
│   │   ├── recordings/          # Grabaciones IQ
│   │   ├── datasets/             # Datasets procesados
│   │   ├── models/               # Modelos entrenados
│   │   ├── models_registry.db    # SQLite con metadatos
│   │   └── events.db             # Eventos de detección
│   │
│   ├── .env (NUEVO, configuración)
│   ├── .env.example (NUEVO)
│   ├── requirements.txt (actualizado)
│   ├── pyproject.toml (sin cambios)
│   └── README_PHASE2.md (NUEVO)
│
├── frontend/
│   ├── src/
│   │   ├── main.ts (sin cambios)
│   │   ├── App.vue (MODIFICADO, agregar nuevos componentes)
│   │   │
│   │   ├── components/
│   │   │   ├── (todos los existentes sin cambios)
│   │   │   │
│   │   │   ├── acquisition/ (NUEVO)
│   │   │   │   ├── RecordingPanel.vue
│   │   │   │   ├── IQRecorder.vue
│   │   │   │   └── RecordingStatus.vue
│   │   │   │
│   │   │   ├── datasets/ (NUEVO)
│   │   │   │   ├── DatasetBrowser.vue
│   │   │   │   ├── DatasetLabeler.vue
│   │   │   │   └── DatasetViewer.vue
│   │   │   │
│   │   │   ├── ml/ (NUEVO)
│   │   │   │   ├── ModelDashboard.vue
│   │   │   │   ├── ModelComparison.vue
│   │   │   │   ├── PredictionPanel.vue
│   │   │   │   └── TrainingMonitor.vue
│   │   │   │
│   │   │   └── ai/ (NUEVO)
│   │   │       ├── AIChat.vue
│   │   │       ├── CommandHistory.vue
│   │   │       └── SystemLogs.vue
│   │   │
│   │   ├── composables/
│   │   │   ├── (todos los existentes sin cambios)
│   │   │   │
│   │   │   ├── useRecording.ts (NUEVO)
│   │   │   ├── useDataset.ts (NUEVO)
│   │   │   ├── useModel.ts (NUEVO)
│   │   │   ├── useTraining.ts (NUEVO)
│   │   │   └── useAI.ts (NUEVO)
│   │   │
│   │   ├── services/
│   │   │   ├── (todos los existentes sin cambios)
│   │   │   │
│   │   │   ├── acquisitionService.ts (NUEVO)
│   │   │   ├── datasetService.ts (NUEVO)
│   │   │   ├── modelService.ts (NUEVO)
│   │   │   ├── trainingService.ts (NUEVO)
│   │   │   └── aiService.ts (NUEVO)
│   │   │
│   │   └── types/ (NUEVO)
│   │       ├── acquisition.ts
│   │       ├── dataset.ts
│   │       ├── model.ts
│   │       └── ai.ts
│   │
│   └── (resto sin cambios)
│
├── ARCHITECTURE_PHASE2.md (ESTE DOCUMENTO)
├── README.md (actualizar con nueva estructura)
└── .gitignore (actualizado para /backend/data/)
```

---

## 12. Modelos de Datos Completos

### 12.1 Adquisición

```python
# backend/app/api/schemas/acquisition.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum


class AcquisitionMode(str, Enum):
    SWEEP = "sweep"
    IQ = "iq"


@dataclass
class AcquisitionMetadata:
    """Metadatos de cualquier adquisición"""
    timestamp_utc: float
    device_id: str
    serial_number: int
    device_type: str
    firmware_version: str
    api_version: str
    
    center_frequency_hz: float
    span_hz: float
    start_frequency_hz: float
    stop_frequency_hz: float
    rbw_hz: float
    vbw_hz: float
    reference_level_dbm: float
    attenuation_db: float
    detector_type: str
    
    acquisition_mode: AcquisitionMode
    sample_rate_sps: Optional[float] = None
    sample_count: Optional[int] = None
    duration_seconds: Optional[float] = None
    
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    gps_altitude_m: Optional[float] = None
    gps_timestamp: Optional[float] = None
    
    location_name: Optional[str] = None
    operator_name: Optional[str] = None
    notes: Optional[str] = None
    environment: Optional[str] = None
    
    sample_loss_detected: bool = False
    iq_imbalance_db: Optional[float] = None
    dc_offset: Optional[float] = None
    frequency_error_hz: Optional[float] = None
    
    file_hash: Optional[str] = None
    file_format: Optional[str] = None
    file_size_bytes: Optional[int] = None
    compression: Optional[str] = None


@dataclass
class SpectrumSnapshot:
    """Snapshot de espectro"""
    metadata: AcquisitionMetadata
    trace: List[float]              # dBm values
    trace_length: int
    bin_size_hz: float
    peak_frequency_hz: float
    peak_power_dbm: float
    noise_floor_dbm: float
    occupied_bandwidth_hz: float
    max_hold: Optional[List[float]] = None
    min_hold: Optional[List[float]] = None
    average_trace: Optional[List[float]] = None


@dataclass
class IQRecording:
    """Grabación de datos IQ complejos"""
    metadata: AcquisitionMetadata
    iq_data: bytes              # Serializado (complex64)
    sample_count: int
    power_watts: float
    peak_to_average_ratio_db: float
    crest_factor: float
    detector_min: Optional[List[float]] = None
    detector_max: Optional[List[float]] = None
    detector_avg: Optional[List[float]] = None
```

### 12.2 Datasets

```python
# backend/app/api/schemas/datasets.py

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum


class DatasetStatus(str, Enum):
    DRAFT = "draft"
    LABELED = "labeled"
    VALIDATED = "validated"
    READY = "ready"
    ARCHIVED = "archived"


class SplitStrategy(str, Enum):
    RANDOM = "random"               # Peligro de leakage
    BY_RECORDING = "by_recording"   # Recomendado
    BY_SESSION = "by_session"
    BY_SCENARIO = "by_scenario"


@dataclass
class DatasetMetadata:
    """Información de un Dataset"""
    id: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    
    # Contenido
    recording_ids: List[str]
    total_samples: int
    duration_seconds: float
    
    # Clases
    classes: Dict[str, int]          # {"NORMAL": 150, "INTERFERENCE": 50}
    class_descriptions: Dict[str, str]
    
    # Balanceo
    class_weights: Optional[Dict[str, float]] = None
    is_balanced: bool = False
    
    # Split
    train_recording_ids: List[str] = None
    val_recording_ids: List[str] = None
    test_recording_ids: List[str] = None
    split_strategy: Optional[SplitStrategy] = None
    
    # Features
    feature_names: List[str] = None
    feature_count: int = 0
    feature_preprocessing_params: Dict = None
    
    # Versionado
    version: str = "1.0.0"
    parent_version: Optional[str] = None
    changelog: List[str] = None
    
    # Validación
    data_leakage_checked: bool = False
    duplicate_check_passed: bool = False
    corruption_check_passed: bool = False
    
    # Almacenamiento
    storage_path: str = None
    storage_format: str = None  # "HDF5", "Parquet", "NPZ"
    
    # Estado
    status: DatasetStatus = DatasetStatus.DRAFT
```

### 12.3 Modelos ML

```python
# backend/app/api/schemas/training.py

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum


class ModelType(str, Enum):
    XGBOOST = "xgboost"
    RANDOM_FOREST = "random_forest"
    ISOLATION_FOREST = "isolation_forest"
    KNN = "knn"
    MLP = "mlp"
    CNN = "cnn"


class ModelStatus(str, Enum):
    TRAINING = "training"
    READY = "ready"
    ARCHIVED = "archived"
    FAILED = "failed"


@dataclass
class EvaluationMetrics:
    """Métricas de evaluación"""
    accuracy: float
    precision: float
    recall: float
    f1: float
    weighted_f1: Optional[float] = None
    macro_f1: Optional[float] = None
    roc_auc: Optional[float] = None
    pr_auc: Optional[float] = None
    precision_anomaly: Optional[float] = None
    recall_anomaly: Optional[float] = None
    confusion_matrix: List[List[int]] = None
    class_report: Dict = None
    training_time_seconds: Optional[float] = None
    inference_time_ms: Optional[float] = None


@dataclass
class ModelMetadata:
    """Información de un Modelo Entrenado"""
    id: str
    model_type: ModelType
    dataset_id: str
    training_date: datetime
    hyperparameters: Dict
    
    # Resultados
    train_metrics: EvaluationMetrics
    val_metrics: Optional[List[EvaluationMetrics]] = None
    test_metrics: Optional[EvaluationMetrics] = None
    
    # Recursos
    training_time_seconds: float = 0
    memory_used_mb: float = 0
    
    # Modelo
    model_file_path: str = None
    feature_names: List[str] = None
    feature_preprocessing_params: Dict = None
    
    # Estado
    status: ModelStatus = ModelStatus.READY
    ready_for_inference: bool = True
    notes: Optional[str] = None
    
    # Metadata adicional
    author: Optional[str] = None
    version: str = "1.0.0"
```

### 12.4 Inferencia

```python
# backend/app/api/schemas/inference.py

from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class PredictionResult:
    """Resultado de una predicción"""
    timestamp: float
    predicted_class: str
    confidence: float
    class_probabilities: Dict[str, float]
    
    # Ensemble info
    model_predictions: Dict[str, str] = None
    model_confidences: Dict[str, float] = None
    ensemble_method: str = None
    
    # Información de inferencia
    inference_time_ms: float = 0
    features_used: int = 0
    model_ids: List[str] = None
    
    # Contexto
    frequency_hz: Optional[float] = None
    power_dbm: Optional[float] = None


@dataclass
class RecordingPredictions:
    """Predicciones para una grabación completa"""
    recording_id: str
    recording_metadata: Dict
    predictions: List[PredictionResult]
    summary: Dict  # stats, majority_class, etc.
```

### 12.5 IA

```python
# backend/app/api/schemas/ai.py

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class IntentRequest:
    """Intención parseda por Ollama"""
    action: str                     # "start_monitoring", "analyze", etc.
    parameters: Dict[str, any]      # Parámetros específicos
    confidence: float               # 0.0-1.0
    raw_response: str               # Respuesta original de Ollama


@dataclass
class CommandValidationResult:
    """Resultado de validación de comando"""
    is_valid: bool
    errors: List[str] = None
    warnings: List[str] = None
    safety_checks_passed: bool = True
    permission_granted: bool = True


@dataclass
class AIResponse:
    """Respuesta final del sistema AI"""
    user_input: str
    parsed_intent: IntentRequest
    validation: CommandValidationResult
    execution_status: str           # "success", "error", "partial"
    result_data: Dict
    ai_interpretation: str          # Explicación en lenguaje natural
    conversation_id: str
    timestamp: datetime
```

---

## 13. Roadmap de Fases

```
FASE 1: Conexión BB60C ✅ COMPLETADA
└─ Sweep en tiempo real
└─ WebSocket streaming
└─ Configuración dinámica
└─ Diagn ósticsticos

FASE 2A: Arquitectura IQ/Espectro (PRÓXIMA)
├─ Modelos de datos expandidos
├─ Adquisición de espectro mejorada
├─ Captura IQ básica
└─ Almacenamiento en disco

FASE 2B: Grabador IQ
├─ Grabación de larga duración
├─ Detección de sample loss
├─ Metadata completa
└─ Múltiples formatos

FASE 2C: Metadata y Almacenamiento
├─ Database SQLite
├─ Indexación
├─ Búsqueda
└─ Versionado

FASE 2D: Dataset Manager
├─ Import de grabaciones
├─ Validación de datos
├─ Detección de duplicados
└─ División train/test

FASE 2E: Etiquetado
├─ Interfaz visual
├─ Etiquetado manual
├─ Segmentación temporal
└─ Validación de etiquetas

FASE 2F: Feature Engineering
├─ Extracción modular
├─ 40+ características
├─ Normalización
└─ Selección de features

FASE 2G: Training Pipeline
├─ XGBoost
├─ Random Forest
├─ Isolation Forest
├─ Evaluación
└─ Comparación de modelos

FASE 2H: Model Registry
├─ Almacenamiento
├─ Metadata
├─ Versionado
└─ Gestión de ciclo de vida

FASE 2I: Inferencia
├─ Predicción en tiempo real
├─ Predicción en archivo
├─ Ensemble
└─ Performance optimization

FASE 2J: Ollama Integration
├─ Conexión a Ollama
├─ Intent parsing
├─ Tool calling
└─ Respuestas interpretadas

FASE 2K: Command Engine
├─ Validación de intents
├─ Ejecución de comandos
├─ Orquestación RF+ML
└─ Manejo de errores

FASE 2L: IA Tiempo Real
├─ Predicción continua
├─ Visualización de confianza
├─ Alertas automáticas
└─ Interpretación en vivo

FASE 3: Frontend ML/AI
├─ Componentes nuevos
├─ Dashboard de modelos
├─ Chat con IA
└─ Visualización avanzada

FASE 4: Optimizaciones
├─ GPU acceleration
├─ Caché de features
├─ Compresión de datos
└─ Performance tuning

FASE 5: Escalabilidad
├─ Múltiples dispositivos
├─ Base de datos centralizada
├─ Servicios microservicios
└─ Distributed training

FASE 6: Productización
├─ Instalador
├─ Docker
├─ CI/CD
├─ Monitoreo
└─ Documentación completa
```

---

## 14. FASE 2A: Objetivos y Tareas

### 14.1 Objetivo General

**Diseñar e implementar la arquitectura de adquisición de datos IQ y espectro con almacenamiento persistente y metadatos completos.**

### 14.2 Requisitos

**Entrada:**
- Signal Hound BB60C conectado
- Backend FastAPI ejecutándose
- Frontend Vue funcionando

**Salida:**
- Grabación IQ de hasta 3600 segundos
- Almacenamiento en disco (/backend/data/recordings/)
- Base de datos SQLite con metadatos
- API endpoints para gestionar grabaciones
- Interfaz Vue para iniciar/detener grabaciones

### 14.3 Tareas Específicas

```
TAREA 1: Expandir modelos de datos
├─ Archivo: backend/app/api/schemas/acquisition.py (NUEVO)
├─ Cambios: backend/app/rf/models.py (EXTENDER)
├─ Objetos:
│  ├─ AcquisitionMetadata (completo)
│  ├─ SpectrumSnapshot (actualizar)
│  ├─ IQRecording (nuevo)
│  └─ Enums: AcquisitionMode
└─ Tests: tests/test_models_acquisition.py

TAREA 2: Crear AcquisitionService
├─ Archivo: backend/app/services/acquisition_service.py (NUEVO)
├─ Métodos:
│  ├─ start_sweep() → StreamID
│  ├─ stop_sweep() → None
│  ├─ get_current_sweep() → SpectrumSnapshot
│  ├─ start_iq_recording(config) → RecordingID
│  ├─ stop_iq_recording(recording_id) → RecordingFile
│  ├─ get_iq_recording_status(recording_id) → Status
│  ├─ save_recording(recording, path) → RecordingID
│  ├─ load_recording(recording_id) → IQRecording
│  ├─ list_recordings() → List[RecordingMetadata]
│  └─ delete_recording(recording_id) → None
└─ Tests: tests/test_acquisition_service.py

TAREA 3: Integrar IQ Capture en BB60C Adapter
├─ Archivo: backend/app/devices/bb60c/iq_capture.py (NUEVO)
├─ Clase: BB60CIQCapture
├─ Métodos:
│  ├─ start_iq_capture(center_hz, bandwidth, sample_rate, duration)
│  ├─ stop_iq_capture()
│  ├─ get_iq_data() → np.ndarray
│  └─ get_capture_status()
└─ Tests: tests/test_bb60c_iq_capture.py

TAREA 4: Crear StorageService
├─ Archivo: backend/app/services/storage_service.py (NUEVO)
├─ Métodos:
│  ├─ save_iq_recording(recording, filename) → Path
│  ├─ load_iq_recording(filepath) → IQRecording
│  ├─ save_sweep_snapshot(snapshot, filename) → Path
│  ├─ list_files(type: "iq" | "sweep") → List[Path]
│  ├─ delete_file(filepath) → None
│  ├─ compute_file_hash(filepath) → str
│  └─ get_storage_stats() → Dict
├─ Storage path: /backend/data/recordings/
├─ Formato: HDF5 (a validar en descripción)
└─ Tests: tests/test_storage_service.py

TAREA 5: Crear base de datos SQLite
├─ Archivo: backend/app/storage/database.py (NUEVO)
├─ Tablas:
│  ├─ recordings (id, filename, timestamp, device_id, metadata_json)
│  ├─ sweeps (id, timestamp, center_freq, peak_power, metadata_json)
│  ├─ metadata (id, acquisition_id, key, value)
│  └─ events (id, timestamp, event_type, data_json)
├─ Migrations: alembic (o SQL manual inicialmente)
└─ Tests: tests/test_database.py

TAREA 6: Crear RecordingRepository
├─ Archivo: backend/app/storage/repositories/recording_repository.py (NUEVO)
├─ Métodos:
│  ├─ create(recording: IQRecording) → RecordingID
│  ├─ get_by_id(id: str) → IQRecording
│  ├─ update(id: str, data: Dict) → None
│  ├─ delete(id: str) → None
│  ├─ list_all() → List[Recording]
│  ├─ find_by_timestamp_range(start, end) → List[Recording]
│  └─ find_by_label(label: str) → List[Recording]
└─ Tests: tests/test_recording_repository.py

TAREA 7: Crear API endpoints
├─ Archivo: backend/app/api/routers/recordings.py (NUEVO)
├─ Endpoints:
│  ├─ POST   /recordings/iq/start
│  ├─ POST   /recordings/iq/stop
│  ├─ GET    /recordings/iq/{recording_id}/status
│  ├─ GET    /recordings (lista)
│  ├─ GET    /recordings/{recording_id}
│  ├─ DELETE /recordings/{recording_id}
│  ├─ POST   /recordings/{recording_id}/export
│  └─ POST   /recordings/sweep/capture (uno-time snapshot)
└─ Tests: tests/test_api_recordings.py

TAREA 8: Crear eventos de registro
├─ Archivo: backend/app/services/event_service.py (NUEVO)
├─ Métodos:
│  ├─ log_recording_started(metadata) → EventID
│  ├─ log_recording_stopped(recording_id, metadata) → EventID
│  ├─ log_file_saved(recording_id, filepath) → EventID
│  └─ get_events(filter) → List[Event]
└─ Tests: tests/test_event_service.py

TAREA 9: Frontend - Panel de Grabación
├─ Archivo: frontend/src/components/acquisition/RecordingPanel.vue (NUEVO)
├─ Funcionalidades:
│  ├─ Botón START/STOP
│  ├─ Duración configurable
│  ├─ Center frequency
│  ├─ Bandwidth
│  ├─ Sample rate
│  ├─ Estado en tiempo real
│  ├─ Barra de progreso
│  └─ Tamaño estimado
└─ Usar composable: useRecording.ts

TAREA 10: Frontend - Composable useRecording
├─ Archivo: frontend/src/composables/useRecording.ts (NUEVO)
├─ Funciones:
│  ├─ startRecording(config)
│  ├─ stopRecording()
│  ├─ getRecordingStatus()
│  ├─ listRecordings()
│  └─ deleteRecording(id)
└─ Mantener estado reactivo

TAREA 11: Validar arquitectura de datos
├─ Verificar:
│  ├─ Completitud de AcquisitionMetadata
│  ├─ Serialización JSON/HDF5
│  ├─ Integridad de archivos
│  ├─ Hash y checksums
│  └─ Recuperabilidad de datos
└─ Documento: VALIDATION_PHASE2A.md

TAREA 12: Documentación y Testing
├─ Crear:
│  ├─ PHASE2A_IMPLEMENTATION.md
│  ├─ Unit tests (80%+ coverage)
│  ├─ Integration tests
│  └─ API docs (Swagger update)
└─ Validar con usuario
```

### 14.4 Decisiones Arquitectónicas a Hacer

```
1. FORMATO DE ALMACENAMIENTO IQ
   Opciones:
   A) NumPy .npy (simple, compatible)
   B) NumPy .npz (comprimido)
   C) HDF5 (hierarchical, ideal para datasets)
   D) WAV (estándar audio, portable)
   E) SigMF (estándar RF, metadatos completos)
   
   Recomendación: HDF5
   - Soporta metadatos embebidos
   - Compresión lossless
   - Lectura parcial (importante para archivos grandes)
   - Estándar en ML/científico
   - Herramientas disponibles
   
   Justificación:
   - Grabaciones de 30s @ 40 MSps ≈ 4.8 GB de IQ puro
   - HDF5 reduce a ~2.4 GB con compresión GZIP
   - Metadatos almacenados junto al archivo
   - Permite acceso random sin cargar todo

2. ESTRATEGIA DE SPLIT PARA EVITAR DATA LEAKAGE
   Regla: Dividir por RECORDING, no por muestras
   - Recording_001 → TRAIN
   - Recording_002 → TRAIN
   - Recording_003 → TRAIN
   - Recording_004 → TEST
   
   Justificación:
   - Evita correlación temporal
   - Evita duplicados implícitos
   - Reflect realidad: en prod, entrada = nueva grabación

3. CONFIGURACIÓN DE OLLAMA
   - ¿Local o remoto?
   - ¿Qué modelo usar por defecto?
   - ¿Timeout de llamadas?
   - ¿Caché de respuestas?
   → Decisión en FASE 2J

4. COMPRESIÓN DE DATOS
   - ¿GZIP (lento pero máximo)?
   - ¿LZ4 (rápido, menos compresión)?
   - ¿Sin compresión?
   → Propuesta: GZIP con opción de deshabilitar
```

### 14.5 Criterios de Aceptación

**La FASE 2A se considera COMPLETA cuando:**

```
✅ Modelos de datos
   - AcquisitionMetadata contiene todos los parámetros BB60C
   - SpectrumSnapshot y IQRecording heredan AcquisitionMetadata
   - Pydantic schemas validan correctamente
   - JSON serializable sin errores

✅ Adquisición IQ
   - start_iq_recording() inicia grabación real en BB60C
   - stop_iq_recording() detiene y retorna datos
   - Captura mínimo 10 segundos sin sample loss
   - Metadatos registrados correctamente

✅ Almacenamiento
   - Archivos guardados en /backend/data/recordings/
   - Formato HDF5 con compresión
   - Hash SHA256 computado y verificado
   - Recuperable y validable

✅ Base de datos
   - SQLite con tabla recordings poblada
   - Queries funcionan correctamente
   - Búsqueda por timestamp, device, label
   - Transacciones ACID

✅ API Endpoints
   - POST /recordings/iq/start devuelve recording_id
   - GET /recordings/{id}/status retorna estado actual
   - GET /recordings lista todas las grabaciones
   - DELETE /recordings/{id} elimina archivo + DB

✅ Frontend
   - RecordingPanel renderiza sin errores
   - Botón START inicia grabación
   - Barra de progreso actualiza en tiempo real
   - Botón STOP detiene y guarda

✅ Testing
   - Unit tests: 80%+ coverage
   - Integration tests: flujo completo funciona
   - API tests: todos los endpoints validados
   - Sin memory leaks en daemon threads

✅ Documentación
   - Código comentado (docstrings)
   - README_PHASE2A.md con instrucciones
   - API documented en Swagger/OpenAPI
   - Diagrama de flujo actualizado

✅ Sin Data Leakage
   - Validación de arquitectura correcta
   - Tests específicos para evitar correlaciones
   - Documento de justificación de split strategy

✅ Producc ión
   - .env con variables de configuración
   - Paths relativos (portable)
   - Error handling robusto
   - Logs estructurados
```

### 14.6 Preguntas de Validación

Antes de empezar FASE 2A, validar:

```
1. ¿Acuerdo con arquitectura de 9 capas?
2. ¿Acuerdo con separación ML vs LLM?
3. ¿HDF5 es el formato correcto para IQ?
4. ¿Qué parámetros adicionales debe capturar AcquisitionMetadata?
5. ¿Debo implementar todo o por módulos?
6. ¿Tests desde el principio o después?
7. ¿Frontend en FASE 2A o FASE 3?
8. ¿Necesitas cambios en la propuesta?
```

---

## Resumen Ejecutivo

Esta arquitectura propone una transformación de RF Monitor de una herramienta de monitoreo en tiempo real a una **plataforma integrada de análisis RF con IA**:

### Características Clave

1. **Separación Clara**: RF, ML y LLM completamente desacoplados
2. **Modular**: Agregar nuevos modelos sin quebrar existente
3. **Robusto**: Evitar data leakage desde el inicio
4. **Escalable**: Preparado para múltiples dispositivos y usuarios
5. **Documentado**: Cada decisión justificada

### Timeline

- **FASE 2A-2C**: Adquisición y almacenamiento (2-3 semanas)
- **FASE 2D-2F**: Datasets y features (3-4 semanas)
- **FASE 2G-2I**: ML pipeline y inferencia (4-5 semanas)
- **FASE 2J-2L**: Ollama e integración (2-3 semanas)
- **FASE 3+**: Frontend, optimizaciones, productización

### Próximo Paso

Validar esta propuesta. Si está de acuerdo, procederemos con **FASE 2A: Implementación de Adquisición IQ y Espectro**.

---

**Fin del Documento**

