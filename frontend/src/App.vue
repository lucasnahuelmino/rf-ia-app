<template>

  <AppHeader />

  <div class="layout">

    <div class="left-panel">

      <SpectrumStatus
        v-if="snapshot"
        :snapshot="snapshot"
      />

      <div class="connection-bar">
        Estado WS:
        <span :class="connectionClass">
          {{ connectionStatus }}
        </span>
      </div>

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

      <MarkerBar />

      <WaterfallCanvas
        v-if="snapshot"
        :snapshot="snapshot"
      />

      <MarkerTable />

      <MeasurementsPanel
        v-if="snapshot"
        :snapshot="snapshot"
      />

    </div>

    <div class="right-panel">

      <GradientButtonGroup>
        <GradientButton
          v-for="tab in tabs"
          :key="tab.id"
          :active="activeTab === tab.id"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </GradientButton>
      </GradientButtonGroup>

      <div class="tab-content">

        <template v-if="activeTab === 'controls'">
          <DevicePanel />
          <SpectrumControls />
        </template>

        <template v-if="activeTab === 'analysis'">
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
        </template>

        <template v-if="activeTab === 'iq'">
          <IQRecorderPanel />
          <IQPlayerPanel />
          <DemodulatorPanel />
          <AudioPanel />
        </template>

        <template v-if="activeTab === 'data'">
          <RecordingsLibrary />
          <ExportPanel />
          <AdvancedHeatmapPanel />
        </template>

        <template v-if="activeTab === 'system'">
          <MultiDevicePanel />
          <MissionPanel />
          <AntennaEditor />
          <RFChainEditor />
          <OccupationAuditorPanel />
          <GPSPanel />
          <GeoMapView />
          <SpatialAnalysisPanel />
          <CoveragePanel />
          <CampaignPanel />
          <OllamaPanel />
          <MLPanel />
        </template>

      </div>

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

import IQRecorderPanel
  from "./components/IQRecorderPanel.vue"

import IQPlayerPanel
  from "./components/IQPlayerPanel.vue"

import DemodulatorPanel
  from "./components/DemodulatorPanel.vue"

import AudioPanel
  from "./components/AudioPanel.vue"

import RecordingsLibrary
  from "./components/RecordingsLibrary.vue"

import ExportPanel
  from "./components/ExportPanel.vue"

import OllamaPanel
  from "./components/OllamaPanel.vue"

import MLPanel
  from "./components/MLPanel.vue"

import GradientButtonGroup
  from "./components/ui/GradientButtonGroup.vue"

import GradientButton
  from "./components/ui/GradientButton.vue"

import MultiDevicePanel
  from "./components/MultiDevicePanel.vue"

import MissionPanel
  from "./components/MissionPanel.vue"

import GPSPanel
  from "./components/GPSPanel.vue"

import GeoMapView
  from "./components/GeoMapView.vue"

import SpatialAnalysisPanel
  from "./components/SpatialAnalysisPanel.vue"

import CampaignPanel
  from "./components/CampaignPanel.vue"

import CoveragePanel
  from "./components/CoveragePanel.vue"

import AntennaEditor
  from "./components/AntennaEditor.vue"

import RFChainEditor
  from "./components/RFChainEditor.vue"

import OccupationAuditorPanel
  from "./components/OccupationAuditorPanel.vue"

import AdvancedHeatmapPanel
  from "./components/AdvancedHeatmapPanel.vue"

import DevicePanel
  from "./components/DevicePanel.vue"



import {
  useSpectrum,
} from "./composables/useSpectrum"

import {
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
  markers,
  moveMarkerToPeak,
  peakSearch: markerPeakSearch,
  nextPeak: markerNextPeak,
  previousPeak: markerPreviousPeak,
  centerOnMarker: markerCenterOnMarker,
} = useMarkers()

const {
  spectrum,
  connectionStatus,
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

const connectionClass = computed(() => {
  switch (connectionStatus.value) {
    case "connected":
      return "status-connected"
    case "connecting":
      return "status-connecting"
    default:
      return "status-disconnected"
  }
})

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

const activeTab = ref("controls")

const tabs = [
  { id: "controls", label: "Controles" },
  { id: "analysis", label: "Análisis" },
  { id: "iq", label: "IQ/Audio" },
  { id: "data", label: "Datos" },
  { id: "system", label: "Sistema" },
]

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

.layout {
  padding: 4px;
  display: flex;
  gap: 4px;
  align-items: stretch;
  height: calc(100vh - 56px);
  overflow: hidden;
}

.left-panel {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow: hidden;
}

.right-panel {
  width: 340px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  overflow: hidden;
}

.tab-content {
  flex: 1;
  overflow: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tab-bar {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  background: white;
  border: 1px solid var(--sncte-border);
  border-radius: var(--radius);
  padding: 6px;
  box-shadow: var(--shadow);
}

.tab-button {
  flex: 1;
  min-width: 70px;
  height: 28px;
  border: none;
  border-radius: 6px;
  background: #f6f9ff;
  color: var(--sncte-blue-dark);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
}

.tab-button.active {
  background: var(--sncte-blue);
  color: white;
}

.tab-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.connection-bar {
  margin-bottom: 8px;
  font-size: 12px;
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