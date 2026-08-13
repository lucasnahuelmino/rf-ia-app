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

    <SpectrumTools
      v-model:showMaxHold="showMaxHold"
      v-model:showAverage="showAverage"
      @clear="clear"
    />

    <SpectrumCanvas
      v-if="snapshot"
      :snapshot="snapshot"
      :show-max-hold="showMaxHold"
      :show-average="showAverage"
      :max-hold="maxHoldTrace"
      :average-trace="averageTrace"
    />

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

import SpectrumTools
  from "./components/SpectrumTools.vue"

import {
  useSpectrum,
} from "./composables/useSpectrum"

import {
  useSpectrumTools,
} from "./composables/useSpectrumTools"

const {
  spectrum,
  connect,
} = useSpectrum()

const snapshot = computed(
  () => spectrum.value
)

const {
  maxHoldTrace,
  averageTrace,
  update,
  clear,
} = useSpectrumTools()

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