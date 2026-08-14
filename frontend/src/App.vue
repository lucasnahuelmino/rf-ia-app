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

      <CollapsiblePanel
        title="Estado del Instrumento"
        :default-open="false"
      >
        <DevicePanel />
      </CollapsiblePanel>

      <SpectrumControls />

      <CollapsiblePanel
        title="Herramientas del Analizador"
        :defaultOpen="true"
      >
        <AnalyzerTools />
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

  import DevicePanel
  from "./components/DevicePanel.vue"

  import CollapsiblePanel
  from "./components/CollapsiblePanel.vue"

const {
  spectrum,
  connect,
} = useSpectrum()

const snapshot = computed(
  () => spectrum.value
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

.layout {
  padding: 20px;
  display: flex;
  gap: 20px;
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