<template>

  <AppHeader />

  <nav class="main-nav">
    <button
      v-for="sec in sections"
      :key="sec.id"
      class="nav-button"
      :class="{ active: activeSection === sec.id }"
      @click="activeSection = sec.id"
    >
      {{ sec.label }}
    </button>
  </nav>

  <ReceiverStrip @select="onReceiverSelect" />

  <div class="layout">

    <div class="main-area">

      <template v-if="activeSection === 'analyzer'">
      <div class="toolbar">
        <AnalyzerTools
          @peakSearch="peakSearch"
          @centerMarker="centerOnMarker"
          @resetView="resetView"
          @togglePeakTracking="togglePeakTracking"
          @markerToPeak="markerToPeak"
          @nextPeak="nextPeak"
          @previousPeak="previousPeak"
          @toggleMaxHold="onToggleMaxHold"
          @toggleMinHold="onToggleMinHold"
          @toggleAverage="onToggleAverage"
          @clearAccumulators="clearAccumulators"
        />
        <button class="tool-toggle" @click="showConfig = !showConfig">
          {{ showConfig ? "Ocultar config" : "Config RF" }}
        </button>
      </div>

      <div v-if="showConfig" class="config-drawer">
        <DevicePanel />
        <SpectrumControls />
      </div>

      <div class="viz-area">
        <MarkerBar />
        <SpectrumStatus v-if="snapshot" :snapshot="snapshot" />
        <SpectrumCanvas
          v-if="snapshot"
          :snapshot="snapshot"
          :show-max-hold="showMaxHold"
          :show-min-hold="showMinHold"
          :show-average="showAverage"
          :max-hold="maxHold ?? undefined"
          :min-hold="minHold ?? undefined"
          :average-trace="averageTrace ?? undefined"
          @moveCenter="moveCenterMarker"
          @zoom="zoomSpectrum"
          @pan="panSpectrum"
        />
        <div v-else class="empty-canvas">Esperando adquisici�n...</div>
        <WaterfallCanvas v-if="snapshot" :snapshot="snapshot" />
      </div>

      <MarkerTable />

      </template>

      <template v-if="activeSection === 'connections'">
        <MultiDevicePanel />
        <AntennaEditor />
        <RFChainEditor />
        <GPSPanel />
      </template>

      <template v-if="activeSection === 'missions'">
        <MissionPanel />
        <CampaignPanel />
      </template>

      <template v-if="activeSection === 'processing'">
        <WorkspacePanel />
        <IQRecorderPanel />
        <IQPlayerPanel />
        <DemodulatorPanel />
        <AudioPanel />
        <AudioLivePanel />
      </template>

      <template v-if="activeSection === 'analysis'">
        <MeasurementsPanel v-if="snapshot" :snapshot="snapshot" />
        <AdvancedHeatmapPanel />
        <SpatialAnalysisPanel />
        <CoveragePanel />
        <OccupationAuditorPanel />
        <GeoMapView />
        <OllamaPanel />
        <MLPanel />
      </template>

      <template v-if="activeSection === 'config'">
        <DevicePanel />
        <SpectrumControls />
        <OllamaPanel />
        <MLPanel />
      </template>

      <template v-if="activeSection === 'files'">
        <RecordingsLibrary />
        <ExportPanel />
      </template>

    </div>

  </div>

</template>

<script setup lang="ts">

import {
  computed,
  onMounted,
  ref,
  watch,
} from "vue"



























































import AppHeader
  from "./components/AppHeader.vue"

import ReceiverStrip
  from "./components/ReceiverStrip.vue"

import SpectrumCanvas
  from "./components/SpectrumCanvas.vue"

import WaterfallCanvas
  from "./components/WaterfallCanvas.vue"

import SpectrumControls
  from "./components/SpectrumControls.vue"

import SpectrumStatus
  from "./components/SpectrumStatus.vue"

import AnalyzerTools
  from "./components/AnalyzerTools.vue"

import MarkerBar
  from "./components/MarkerBar.vue"

import MarkerTable
  from "./components/MarkerTable.vue"

import MeasurementsPanel
  from "./components/MeasurementsPanel.vue"

import DevicePanel
  from "./components/DevicePanel.vue"

import IQRecorderPanel
  from "./components/IQRecorderPanel.vue"

import IQPlayerPanel
  from "./components/IQPlayerPanel.vue"

import DemodulatorPanel
  from "./components/DemodulatorPanel.vue"

import AudioPanel
  from "./components/AudioPanel.vue"

import AudioLivePanel
  from "./components/AudioLivePanel.vue"

import RecordingsLibrary
  from "./components/RecordingsLibrary.vue"

import ExportPanel
  from "./components/ExportPanel.vue"

import OllamaPanel
  from "./components/OllamaPanel.vue"

import MLPanel
  from "./components/MLPanel.vue"

import MultiDevicePanel
  from "./components/MultiDevicePanel.vue"

import MissionPanel
  from "./components/MissionPanel.vue"

import AntennaEditor
  from "./components/AntennaEditor.vue"

import RFChainEditor
  from "./components/RFChainEditor.vue"

import OccupationAuditorPanel
  from "./components/OccupationAuditorPanel.vue"

import GPSPanel
  from "./components/GPSPanel.vue"

import GeoMapView
  from "./components/GeoMapView.vue"

import SpatialAnalysisPanel
  from "./components/SpatialAnalysisPanel.vue"

import CoveragePanel
  from "./components/CoveragePanel.vue"

import CampaignPanel
  from "./components/CampaignPanel.vue"

import AdvancedHeatmapPanel
  from "./components/AdvancedHeatmapPanel.vue"

import WorkspacePanel
  from "./components/WorkspacePanel.vue"

import {
  useSpectrum,
} from "./composables/useSpectrum"

import {
  markers,
  useMarkers,
} from "./composables/useMarkers"

import {
  useTraceAnalysis,
} from "./composables/useTraceAnalysis"

import {
  updateSpectrumConfig,
} from "./services/configService"

const peakTracking =
  ref(false)

const showMaxHold =
  ref(false)

const showMinHold =
  ref(false)

const showAverage =
  ref(false)

const {
  moveMarkerToPeak,
  peakSearch: markerPeakSearch,
  nextPeak: markerNextPeak,
  previousPeak: markerPreviousPeak,
  centerOnMarker: markerCenterOnMarker,
} = useMarkers()

const {
  spectrum,
  connect,
} = useSpectrum()

const traceAnalysis =
  useTraceAnalysis(spectrum)

const maxHold = computed(
  () => traceAnalysis.maxHold.value
)

const minHold = computed(
  () => traceAnalysis.minHold.value
)

const averageTrace = computed(
  () => traceAnalysis.average.value
)

const snapshot = computed(
  () => spectrum.value
)

const activeSection = ref("analyzer")
const showConfig = ref(false)

const sections = [
  { id: "analyzer", label: "Analizador" },
  { id: "connections", label: "Conexiones" },
  { id: "missions", label: "Misiones" },
  { id: "processing", label: "Procesamiento" },
  { id: "analysis", label: "Análisis" },
  { id: "config", label: "Configuración" },
  { id: "files", label: "Archivo" },
]





watch(
  snapshot,
  () => {
    if (peakTracking.value) {
      peakSearch()
    }
  },
  { deep: true },
)

function togglePeakTracking(enabled: boolean) {
  peakTracking.value = enabled
}

async function resetView() {
  await updateSpectrumConfig({
    center_frequency_hz: 122e6,
    span_hz: 28e6,
    rbw_hz: 10000,
    vbw_hz: 10000,
    reference_level_dbm: 0,
  })
}

function peakSearch() {
  if (!snapshot.value) return
  markerPeakSearch(snapshot.value, "M1")
}

function markerToPeak() {
  if (!snapshot.value) return
  const selected = markers.value.find(
    (m) => m.selected
  )
  if (!selected) return
  moveMarkerToPeak(selected.id, snapshot.value)
}

function nextPeak() {
  if (!snapshot.value) return
  const selected = markers.value.find(
    (m) => m.selected
  )
  if (!selected) return
  markerNextPeak(snapshot.value, selected.id)
}

function previousPeak() {
  if (!snapshot.value) return
  const selected = markers.value.find(
    (m) => m.selected
  )
  if (!selected) return
  markerPreviousPeak(snapshot.value, selected.id)
}

async function centerOnMarker() {
  if (!snapshot.value) return

  const marker = markers.value.find(
    (m) => m.id === "M1"
  )

  if (!marker || !marker.frequencyHz) return

  const payload = markerCenterOnMarker(
    "M1",
    snapshot.value
  )

  if (!payload) return

  await updateSpectrumConfig(payload)
}

async function zoomSpectrum(deltaY: number) {
  if (!snapshot.value) return

  const factor = deltaY > 0 ? 1.2 : 0.8

  await updateSpectrumConfig({
    center_frequency_hz: snapshot.value.center_frequency_hz,
    span_hz: snapshot.value.span_hz * factor,
    rbw_hz: snapshot.value.rbw_hz,
    vbw_hz: snapshot.value.vbw_hz,
    reference_level_dbm: snapshot.value.reference_level_dbm,
  })
}

async function panSpectrum(centerFrequencyHz: number) {
  if (!snapshot.value) return

  await updateSpectrumConfig({
    center_frequency_hz: centerFrequencyHz,
    span_hz: snapshot.value.span_hz,
    rbw_hz: snapshot.value.rbw_hz,
    vbw_hz: snapshot.value.vbw_hz,
    reference_level_dbm: snapshot.value.reference_level_dbm,
  })
}

async function moveCenterMarker(frequencyHz: number) {
  if (!snapshot.value) return

  await updateSpectrumConfig({
    center_frequency_hz: frequencyHz,
    span_hz: snapshot.value.span_hz,
    rbw_hz: snapshot.value.rbw_hz,
    vbw_hz: snapshot.value.vbw_hz,
    reference_level_dbm: snapshot.value.reference_level_dbm,
  })
}

function onToggleMaxHold(value: boolean) {
  showMaxHold.value = value
}

function onToggleMinHold(value: boolean) {
  showMinHold.value = value
}

function onToggleAverage(value: boolean) {
  showAverage.value = value
}

function clearAccumulators() {
  traceAnalysis.reset()
}

function onReceiverSelect() {}

onMounted(() => {
  connect()
})

</script>

<style>

html, body, #app {
  height: 100%;
  margin: 0;
  overflow: hidden;
}

body {
  background: var(--sncte-background);
  font-family: Arial, Helvetica, sans-serif;
}

.main-nav {
  display: flex;
  gap: 4px;
  padding: 4px 8px;
  background: var(--bg-panel);
  border-bottom: 1px solid var(--border);
  height: 36px;
  align-items: center;
}

.nav-button {
  padding: 4px 12px;
  border: 1px solid var(--border-2);
  border-radius: 4px;
  background: var(--bg-panel-2);
  color: var(--text);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
}

.nav-button:hover {
  border-color: var(--accent);
  color: var(--text-h);
}

.nav-button.active {
  background: linear-gradient(135deg, #0ea5e9, #2563eb);
  color: white;
  border: none;
}

.layout {
  padding: 4px;
  display: flex;
  gap: 4px;
  align-items: stretch;
  height: calc(100vh - 136px);
  overflow: hidden;
}

.main-area {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow: hidden;
}

.viz-area {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow: hidden;
}

.config-drawer {
  display: flex;
  gap: 8px;
  padding: 6px;
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  max-height: 180px;
  overflow: auto;
}

.empty-canvas {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #020617;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text-muted);
  font-size: 13px;
}

.tab-bar {
  display: flex;
  gap: 4px;
  padding: 4px;
  background: white;
  border: 1px solid var(--sncte-border);
  border-radius: 6px;
}

.tab-button {
  flex: 1;
  height: 26px;
  border: none;
  border-radius: 4px;
  background: #f6f9ff;
  color: var(--sncte-blue-dark);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
}

.tab-button.active {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  color: white;
}

.tab-content {
  flex: 1;
  overflow: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-mini {
  font-size: 11px;
  color: #374151;
}

.connection-bar {
  margin-bottom: 4px;
  font-size: 11px;
  color: #374151;
}

.status-connected {
  color: #16a34a;
  font-weight: 700;
}

.status-connecting {
  color: #d97706;
  font-weight: 700;
}

.status-disconnected {
  color: #dc2626;
  font-weight: 700;
}

</style>