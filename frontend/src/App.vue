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
      />

      <CollapsiblePanel
        title="Tabla de Markers"
        :defaultOpen="false"
      >
        <MarkerTable />
      </CollapsiblePanel>

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
        />
      </CollapsiblePanel>

    </div>

</div>

</template>

<script setup lang="ts">

import {
  computed,
  onMounted,
} from "vue"

import SpectrumCanvas
  from "./components/SpectrumCanvas.vue"

import SpectrumControls
  from "./components/SpectrumControls.vue"

import SpectrumStatus
  from "./components/SpectrumStatus.vue"

import {
  useSpectrum,
} from "./composables/useSpectrum"

import AppHeader
from "./components/AppHeader.vue"

import MarkerTable
  from "./components/MarkerTable.vue"

  import AnalyzerTools
  from "./components/AnalyzerTools.vue"

import {
  markers,
} from "./composables/useMarkers"

  import CollapsiblePanel
  from "./components/CollapsiblePanel.vue"

const {
  spectrum,
  connect,
} = useSpectrum()

const snapshot = computed(
  () => spectrum.value
)

function peakSearch() {

  if (!snapshot.value)
    return

  const trace =
    snapshot.value.trace

  let peakIndex = 0

  let peakValue =
    Number.NEGATIVE_INFINITY

  trace.forEach(
    (
      value: number,
      index: number,
    ) => {

      if (value > peakValue) {

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

  markers.value[0].enabled = true

  markers.value[0].selected = true

  markers.value[0].frequencyHz =
    frequencyHz

  markers.value[0].powerDbm =
    peakValue
}

async function centerOnMarker() {

  const marker =
    markers.value[0]

  if (!marker.frequencyHz)
    return

  await fetch(
    "http://127.0.0.1:8000/spectrum/config",
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify({
        center_frequency_hz:
          marker.frequencyHz,

        span_hz:
          snapshot.value.span_hz,

        rbw_hz: 10000,

        vbw_hz: 10000,

        reference_level_dbm: 0,
      }),
    }
  )
}

onMounted(() => {
  connect()
})

</script>

<style>

body {
  margin: 0;
  background: var(--sncte-background);

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