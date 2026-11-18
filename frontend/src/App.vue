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

      <DevicePanel />

      <SpectrumControls />

      <CollapsiblePanel
        title="Herramientas del Analizador"
        :defaultOpen="true"
      >

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

      </CollapsiblePanel>

      <CollapsiblePanel title="Grabación I/Q" :defaultOpen="false">
        <IQRecorderPanel />
        <IQPlayerPanel />
      </CollapsiblePanel>

      <CollapsiblePanel title="Demodulación y Audio" :defaultOpen="false">
        <DemodulatorPanel />
        <AudioPanel />
      </CollapsiblePanel>

      <CollapsiblePanel title="Biblioteca" :defaultOpen="false">
        <RecordingsLibrary />
      </CollapsiblePanel>

      <CollapsiblePanel title="Exportaciones" :defaultOpen="false">
        <ExportPanel />
      </CollapsiblePanel>

      <CollapsiblePanel title="Asistente IA" :defaultOpen="false">
        <OllamaPanel />
      </CollapsiblePanel>

      <CollapsiblePanel title="Machine Learning" :defaultOpen="false">
        <MLPanel />
      </CollapsiblePanel>

      <CollapsiblePanel title="Receptores" :defaultOpen="false">
        <MultiDevicePanel />
      </CollapsiblePanel>

      <CollapsiblePanel title="Misiones" :defaultOpen="false">
        <MissionPanel />
      </CollapsiblePanel>

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

import MultiDevicePanel
  from "./components/MultiDevicePanel.vue"

import MissionPanel
  from "./components/MissionPanel.vue"

import DevicePanel
  from "./components/DevicePanel.vue"

import CollapsiblePanel
  from "./components/CollapsiblePanel.vue"

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

onMounted(() => {
  connect()
})

</script>

<style>

body {
  margin: 0;
  background: var(--sncte-background);
  font-family: Arial, Helvetica, sans-serif;
}

.layout {
  padding: 10px;
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.left-panel {
  flex: 1;
  min-width: 0;
}

.right-panel {
  width: 320px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  position: sticky;
  top: 20px;
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