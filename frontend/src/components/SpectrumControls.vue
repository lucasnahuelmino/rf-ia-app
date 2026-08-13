<template>

  <div class="controls">

    <h3>RF Configuration</h3>

    <div class="grid">

      <label>

        <span>Center Frequency (MHz)</span>

        <input
          v-model.number="centerMHz"
          type="number"
          step="0.001"
        />

      </label>

      <label>

        <span>Span (MHz)</span>

        <input
          v-model.number="spanMHz"
          type="number"
          step="0.001"
        />

      </label>

      <label>

        <span>RBW (kHz)</span>

        <input
          v-model.number="rbwKHz"
          type="number"
        />

      </label>

      <label>

        <span>VBW (kHz)</span>

        <input
          v-model.number="vbwKHz"
          type="number"
        />

      </label>

      <label>

        <span>Reference Level (dBm)</span>

        <input
          v-model.number="config.reference_level_dbm"
          type="number"
        />

      </label>

    </div>

    <button @click="applyConfig">
      Apply
    </button>

  </div>

</template>

<script setup lang="ts">

import {
  computed,
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

const centerMHz = computed({

  get: () =>
    config.center_frequency_hz / 1e6,

  set: (value: number) =>
    config.center_frequency_hz =
      value * 1e6,
})

const spanMHz = computed({

  get: () =>
    config.span_hz / 1e6,

  set: (value: number) =>
    config.span_hz =
      value * 1e6,
})

const rbwKHz = computed({

  get: () =>
    config.rbw_hz / 1e3,

  set: (value: number) =>
    config.rbw_hz =
      value * 1e3,
})

const vbwKHz = computed({

  get: () =>
    config.vbw_hz / 1e3,

  set: (value: number) =>
    config.vbw_hz =
      value * 1e3,
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
}

onMounted(
  loadConfig
)

</script>

<style scoped>

.controls {

  background: #181818;

  border: 1px solid #333;

  padding: 15px;

  margin-bottom: 15px;
}

h3 {

  margin-top: 0;

  color: #00ff55;
}

.grid {

  display: grid;

  grid-template-columns:
    repeat(
      auto-fit,
      minmax(220px, 1fr)
    );

  gap: 12px;

  margin-bottom: 12px;
}

label {

  display: flex;

  flex-direction: column;

  gap: 6px;
}

span {

  color: #ccc;

  font-size: 13px;
}

input {

  padding: 8px;

  background: #111;

  border: 1px solid #444;

  color: white;
}

button {
  width: 120px;
  padding: 10px;
  border: none;
  background: #00aa55;
  color: white;
  cursor: pointer;
}

button:hover {
  background: #00cc66;
}

</style>