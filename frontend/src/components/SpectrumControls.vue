<template>

  <div class="controls">

    <h3>RF Configuration</h3>

    <div class="mode-selector">

      <label>

        <input
          v-model="mode"
          value="center"
          type="radio"
        />

        Center + Span

      </label>

      <label>

        <input
          v-model="mode"
          value="range"
          type="radio"
        />

        Start + Stop

      </label>

    </div>

    <div class="grid">

      <template v-if="mode === 'center'">

        <label>

          <span>Center (MHz)</span>

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

      </template>

      <template v-else>

        <label>

          <span>Start (MHz)</span>

          <input
            v-model.number="startMHz"
            type="number"
            step="0.001"
          />

        </label>

        <label>

          <span>Stop (MHz)</span>

          <input
            v-model.number="stopMHz"
            type="number"
            step="0.001"
          />

        </label>

      </template>

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

        <span>Reference (dBm)</span>

        <input
          v-model.number="config.reference_level_dbm"
          type="number"
        />

      </label>

    </div>

    <div class="presets">

      <button @click="presetAir">
        AIR
      </button>

      <button @click="presetVHF">
        VHF
      </button>

      <button @click="presetUHF">
        UHF
      </button>

      <button @click="preset433">
        433 MHz
      </button>

      <button @click="preset868">
        868 MHz
      </button>

      <button @click="presetWifi">
        WiFi
      </button>

    </div>

    <button
      class="apply"
      @click="applyConfig"
    >
      Apply
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

import {
  getSpectrumConfig,
  updateSpectrumConfig,
} from "../services/configService"

const mode =
  ref("center")

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
      (
        config.center_frequency_hz
        - config.span_hz / 2
      ) / 1e6
    ),

  set: (value: number) => {

    const stop =
      (
        config.center_frequency_hz
        + config.span_hz / 2
      )

    config.center_frequency_hz =
      (
        (
          value * 1e6
        )
        +
        stop
      ) / 2

    config.span_hz =
      stop
      -
      value * 1e6
  },
})

const stopMHz = computed({

  get: () =>
    (
      (
        config.center_frequency_hz
        + config.span_hz / 2
      ) / 1e6
    ),

  set: (value: number) => {

    const start =
      (
        config.center_frequency_hz
        - config.span_hz / 2
      )

    config.center_frequency_hz =
      (
        start
        +
        value * 1e6
      ) / 2

    config.span_hz =
      (
        value * 1e6
      )
      - start
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

function presetAir() {

  centerMHz.value = 127.5

  spanMHz.value = 19
}

function presetVHF() {

  centerMHz.value = 145

  spanMHz.value = 20
}

function presetUHF() {

  centerMHz.value = 435

  spanMHz.value = 40
}

function preset433() {

  centerMHz.value = 433.92

  spanMHz.value = 5
}

function preset868() {

  centerMHz.value = 868

  spanMHz.value = 10
}

function presetWifi() {

  centerMHz.value = 2440

  spanMHz.value = 100
}

onMounted(loadConfig)

</script>

<style scoped>

.controls {

  background: #181818;

  border: 1px solid #333;

  padding: 15px;

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

  background: #111;

  border: 1px solid #444;

  color: white;

  padding: 8px;
}

.presets {

  display: flex;

  gap: 10px;

  flex-wrap: wrap;

  margin-bottom: 15px;
}

button {

  padding: 8px 12px;

  cursor: pointer;
}

.apply {

  background: #00aa55;

  color: white;

  border: none;
}

</style>