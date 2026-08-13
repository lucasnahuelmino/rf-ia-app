<template>

  <div class="controls">

    <h3>Spectrum Controls</h3>

    <label>
      Center Frequency (Hz)

      <input
        v-model.number="config.center_frequency_hz"
        type="number"
      />
    </label>

    <label>
      Span (Hz)

      <input
        v-model.number="config.span_hz"
        type="number"
      />
    </label>

    <label>
      RBW (Hz)

      <input
        v-model.number="config.rbw_hz"
        type="number"
      />
    </label>

    <label>
      VBW (Hz)

      <input
        v-model.number="config.vbw_hz"
        type="number"
      />
    </label>

    <label>
      Reference Level (dBm)

      <input
        v-model.number="config.reference_level_dbm"
        type="number"
      />
    </label>

    <button @click="applyConfig">
      Apply
    </button>

  </div>

</template>

<script setup lang="ts">

import {
  onMounted,
  reactive,
} from "vue"

import {
  getSpectrumConfig,
  updateSpectrumConfig,
} from "../services/configService"

const config = reactive({
  center_frequency_hz: 0,
  span_hz: 0,
  rbw_hz: 0,
  vbw_hz: 0,
  reference_level_dbm: 0,
})

async function loadConfig() {

  const data =
    await getSpectrumConfig()

  Object.assign(
    config,
    data,
  )
}

async function applyConfig() {

  await updateSpectrumConfig(
    config
  )

  alert(
    "Configuration updated"
  )
}

onMounted(loadConfig)

</script>

<style scoped>

.controls {
  display: flex;
  flex-direction: column;

  gap: 10px;

  margin-bottom: 20px;

  padding: 12px;

  border: 1px solid #333;
}

input {
  width: 100%;
}

button {
  width: 120px;
}

</style>