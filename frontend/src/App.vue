<template>

  <AppHeader />

  <div class="container">

    <CollapsiblePanel
      title="Estado del Instrumento"
    >

      <DevicePanel />

    </CollapsiblePanel>

    <SpectrumControls />

    <SpectrumStatus
      v-if="snapshot"
      :snapshot="snapshot"
    />

    <CollapsiblePanel
      title="Herramientas del Analizador"
      :defaultOpen="true"
    >

      <AnalyzerTools />

    </CollapsiblePanel>

    <SpectrumCanvas
      v-if="snapshot"
      :snapshot="snapshot"
      :show-max-hold="showMaxHold"
      :show-average="showAverage"
      :max-hold="maxHoldTrace"
      :average-trace="averageTrace"
    />

    <CollapsiblePanel
      title="Tabla de Markers"
    >

      <MarkerTable />

    </CollapsiblePanel>

  </div>

</template>

<script setup lang="ts">

import {
  computed,
  onMounted,
  watch,
  ref,
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

  import CollapsiblePanel
  from "./components/CollapsiblePanel.vue"

const {
  spectrum,
  connect,
} = useSpectrum()

const snapshot = computed(
  () => spectrum.value
)

const showMaxHold =
  ref(false)

const showAverage =
  ref(false)

watch(
  spectrum,
  (value) => {
    if (
      value?.trace
    ) {
      update(
        value.trace
      )
    }
  },
  {
    deep: true,
  },
)

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

.container {
  padding: 20px;
}

</style>