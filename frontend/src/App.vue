<template>

  <div class="container">

    <h1>
      RF Monitor
    </h1>

    <p>
      BB60C Real Time Spectrum
    </p>

    <SpectrumCanvas
      v-if="trace"
      :trace="trace"
    />

    <SpectrumControls />

    <SpectrumCanvas
      v-if="trace"
      :trace="trace"
    />

  </div>

</template>

<script setup lang="ts">

import {
  computed,
  onMounted,
} from "vue"

import SpectrumCanvas
from "./components/SpectrumCanvas.vue"

import {
  useSpectrum
} from "./composables/useSpectrum"

import SpectrumControls
from "./components/SpectrumControls.vue"

const {
  spectrum,
  connect,
} = useSpectrum()

const trace = computed(
  () => spectrum.value?.trace ?? []
)

onMounted(() => {

  connect()
})

</script>