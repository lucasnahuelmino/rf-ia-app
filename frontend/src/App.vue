<template>

  <AppHeader />

  <div class="layout">

    <div class="left-panel">

      <SpectrumStatus
        v-if="snapshot"
        :snapshot="snapshot"
      />

      <SpectrumCanvas
        v-if="snapshot"
        :snapshot="snapshot"
        @moveCenter="moveCenterMarker"
      />

      <MarkerBar />

      <!-- Próximamente -->
      <!-- <WaterfallCanvas :snapshot="snapshot" /> -->

    </div>

    <div class="right-panel">

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
        />

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

import SpectrumControls
  from "./components/SpectrumControls.vue"

import SpectrumStatus
  from "./components/SpectrumStatus.vue"

import AnalyzerTools
  from "./components/AnalyzerTools.vue"

import MarkerBar
  from "./components/MarkerBar.vue"

import CollapsiblePanel
  from "./components/CollapsiblePanel.vue"

import {
  useSpectrum,
} from "./composables/useSpectrum"

import {
  markers,
} from "./composables/useMarkers"

import {
  updateSpectrumConfig,
} from "./services/configService"

const peakTracking =
  ref(false)

function togglePeakTracking(
  enabled: boolean,
) {

  peakTracking.value =
    enabled
}

async function resetView() {

  await updateSpectrumConfig({

    center_frequency_hz:
      122e6,

    span_hz:
      28e6,

    rbw_hz:
      10000,

    vbw_hz:
      10000,

    reference_level_dbm:
      0,
  })
}

const {
  spectrum,
  connect,
} = useSpectrum()

const snapshot = computed(
  () => spectrum.value
)

watch(
  snapshot,
  () => {

    if (
      peakTracking.value
    ) {

      peakSearch()
    }
  },
  {
    deep: true,
  },
)

function peakSearch() {

  if (!snapshot.value)
    return

  const trace =
    snapshot.value.trace

  if (!trace?.length)
    return

  let peakIndex = 0

  let peakValue =
    Number.NEGATIVE_INFINITY

  trace.forEach(
    (
      value: number,
      index: number,
    ) => {

      if (
        value > peakValue
      ) {

        peakValue = value

        peakIndex = index
      }
    }
  )

  const frequencyHz =
    snapshot.value.start_frequency_hz
    +
    (
      peakIndex
      *
      snapshot.value.bin_size_hz
    )

  const marker =
    markers.value.find(
      marker =>
        marker.id === "M1"
    )

  if (!marker)
    return

  marker.enabled = true

  marker.frequencyHz =
    frequencyHz

  marker.powerDbm =
    peakValue
}

async function centerOnMarker() {

  if (!snapshot.value)
    return

  const marker =
    markers.value.find(
      marker =>
        marker.id === "M1"
    )

  if (
    !marker ||
    !marker.frequencyHz
  ) {
    return
  }

  await updateSpectrumConfig({

    center_frequency_hz:
      marker.frequencyHz,

    span_hz:
      snapshot.value.span_hz,

    rbw_hz:
      snapshot.value.rbw_hz,

    vbw_hz:
      snapshot.value.vbw_hz,

    reference_level_dbm:
      snapshot.value.reference_level_dbm,
  })
}

async function moveCenterMarker(
  frequencyHz: number,
) {

  if (!snapshot.value)
    return

  await updateSpectrumConfig({

    center_frequency_hz:
      frequencyHz,

    span_hz:
      snapshot.value.span_hz,

    rbw_hz:
      snapshot.value.rbw_hz,

    vbw_hz:
      snapshot.value.vbw_hz,

    reference_level_dbm:
      snapshot.value.reference_level_dbm,
  })
}

onMounted(() => {

  connect()

})

</script>

<style>

body {

  margin: 0;

  background:
    var(--sncte-background);

  font-family:
    Arial,
    Helvetica,
    sans-serif;
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

</style>
