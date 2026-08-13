<template>

  <div class="controls">

    <h3>Configuración RF</h3>

    <SpectrumPresetSelector
      @presetLoaded="onPresetLoaded"
    />

    <div class="favoritos">

      <button @click="loadFavorite(88,108)">
        FM
      </button>

      <button @click="loadFavorite(108,136)">
        AÉREO
      </button>

      <button @click="loadFavorite(703,803)">
        LTE700
      </button>

      <button @click="loadFavorite(3300,3600)">
        5G
      </button>

      <button @click="loadFavorite(431,436)">
        ISM 433
      </button>

    </div>

    <div class="mode-selector">

      <label>
        <input
          v-model="mode"
          value="center"
          type="radio"
        />
        Centro + Span
      </label>

      <label>
        <input
          v-model="mode"
          value="range"
          type="radio"
        />
        Inicio + Fin
      </label>

    </div>

    <div class="grid">

      <label>
        <span>Frecuencia Inicial (MHz)</span>

        <input
          v-model.number="startMHz"
          type="number"
          step="0.001"
        />
      </label>

      <label>
        <span>Frecuencia Final (MHz)</span>

        <input
          v-model.number="stopMHz"
          type="number"
          step="0.001"
        />
      </label>

      <label>
        <span>Frecuencia Central (MHz)</span>

        <input
          :value="centerMHz.toFixed(3)"
          readonly
        />
      </label>

      <label>
        <span>Span (MHz)</span>

        <input
          :value="spanMHz.toFixed(3)"
          readonly
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
        <span>Referencia (dBm)</span>

        <input
          v-model.number="config.reference_level_dbm"
          type="number"
        />
      </label>

    </div>

    <button
      class="apply"
      @click="applyConfig"
    >
      Aplicar Configuración
    </button>

  </div>

</template>

<script setup lang="ts">

import {
  computed,
  onMounted,
  reactive,
  ref,
} from "vue"

import SpectrumPresetSelector
  from "./SpectrumPresetSelector.vue"

import {
  getSpectrumConfig,
  updateSpectrumConfig,
} from "../services/configService"

const mode =
  ref("range")

const config = reactive({

  center_frequency_hz: 0,

  span_hz: 0,

  rbw_hz: 10000,

  vbw_hz: 10000,

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

const startMHz = computed({

  get: () =>
    (
      config.center_frequency_hz
      -
      config.span_hz / 2
    ) / 1e6,

  set: (value: number) => {

    const stopFreq =
      config.center_frequency_hz
      +
      config.span_hz / 2

    config.center_frequency_hz =
      (
        value * 1e6
        +
        stopFreq
      ) / 2

    config.span_hz =
      stopFreq
      -
      (
        value * 1e6
      )
  },
})

const stopMHz = computed({

  get: () =>
    (
      config.center_frequency_hz
      +
      config.span_hz / 2
    ) / 1e6,

  set: (value: number) => {

    const startFreq =
      config.center_frequency_hz
      -
      config.span_hz / 2

    config.center_frequency_hz =
      (
        startFreq
        +
        (
          value * 1e6
        )
      ) / 2

    config.span_hz =
      (
        value * 1e6
      )
      -
      startFreq
  },
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

async function loadFavorite(
  startMHzValue: number,
  stopMHzValue: number,
) {

  startMHz.value =
    startMHzValue

  stopMHz.value =
    stopMHzValue

  await applyConfig()
}

async function onPresetLoaded(
  preset: any,
) {

  startMHz.value =
    preset.inicioMHz

  stopMHz.value =
    preset.finMHz

  await applyConfig()
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

.favoritos {

  display: flex;

  gap: 8px;

  flex-wrap: wrap;

  margin-bottom: 15px;
}

.mode-selector {

  display: flex;

  gap: 20px;

  margin-bottom: 15px;
}

.grid {

  display: grid;

  grid-template-columns:
    repeat(
      auto-fit,
      minmax(220px,1fr)
    );

  gap: 12px;

  margin-bottom: 15px;
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

  background: #111;

  border: 1px solid #444;

  color: white;

  padding: 8px;
}

button {

  padding: 8px 12px;

  cursor: pointer;
}

.apply {

  background: #00aa55;

  color: white;

  border: none;

  font-weight: bold;
}

.apply:hover {

  background: #00cc66;
}

</style>