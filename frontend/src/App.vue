<template>

  <div class="container">

    <h1>
      RF Monitor
    </h1>

    <p>
      BB60C Real Time Spectrum
    </p>

    <SpectrumControls />
    
    <SpectrumStatus
      v-if="snapshot"
      :snapshot="snapshot"
    />
    <SpectrumCanvas
      v-if="snapshot"
      :snapshot="snapshot"
    />

  </div>

</template>

<script setup lang="ts">

import { computed, onMounted, } from "vue"
import SpectrumCanvas from "./components/SpectrumCanvas.vue"
import SpectrumControls from "./components/SpectrumControls.vue"
import { useSpectrum } from "./composables/useSpectrum"
import SpectrumStatus from "./components/SpectrumStatus.vue"

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