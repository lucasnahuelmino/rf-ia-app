<template>

  <div class="controls">

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

    <div class="grid">

      <label>
        <span>Inicio (MHz)</span>
        <input v-model.number="startMHz" type="number" step="0.001" />
      </label>

      <label>
        <span>Fin (MHz)</span>
        <input v-model.number="stopMHz" type="number" step="0.001" />
      </label>

      <label>
        <span>Centro (MHz)</span>
        <input :value="centerMHz.toFixed(3)" readonly />
      </label>

      <label>
        <span>Span (MHz)</span>
        <input :value="spanMHz.toFixed(3)" readonly />
      </label>

      <label>
        <span>RBW (kHz)</span>
        <input v-model.number="rbwKHz" type="number" />
      </label>

      <label>
        <span>VBW (kHz)</span>
        <input v-model.number="vbwKHz" type="number" />
      </label>

      <label>
        <span>Ref (dBm)</span>
        <input v-model.number="config.reference_level_dbm" type="number" />
      </label>

      <label>
        <span>Sweep time (ms, 0=auto)</span>
        <input v-model.number="sweepTimeMs" type="number" step="0.1" />
      </label>

      <label class="checkbox">
        <input v-model="config.auto_attenuation" type="checkbox" />
        <span>Auto Atten</span>
      </label>

      <label>
        <span>Atten (0-3)</span>
        <input
          v-model.number="config.attenuation"
          type="number"
          min="0"
          max="3"
          :disabled="config.auto_attenuation"
        />
      </label>

      <label class="checkbox">
        <input v-model="config.auto_gain" type="checkbox" />
        <span>Auto Gain</span>
      </label>

      <label>
        <span>Gain (0-3)</span>
        <input
          v-model.number="config.gain"
          type="number"
          min="0"
          max="3"
          :disabled="config.auto_gain"
        />
      </label>

      <label>
        <span>Detector</span>
        <select v-model.number="config.detector">
          <option :value="0">Min/Max</option>
          <option :value="1">Average</option>
        </select>
      </label>

      <label>
        <span>RBW shape</span>
        <select v-model.number="config.rbw_shape">
          <option :value="0">Nuttall</option>
          <option :value="1">Flat-top</option>
          <option :value="2">CISPR</option>
        </select>
      </label>

      <label class="checkbox">
        <input v-model="spurReject" type="checkbox" />
        <span>Spur reject</span>
      </label>

    </div>

    <div class="actions">
      <button class="apply" @click="applyConfig">
        Aplicar
      </button>
    </div>

  </div>

</template>

<script setup lang="ts">

import {
  computed,
  onMounted,
  reactive,
} from "vue"

import SpectrumPresetSelector
  from "./SpectrumPresetSelector.vue"

import {
  getSpectrumConfig,
  updateSpectrumConfig,
} from "../services/configService"

const config = reactive({

  center_frequency_hz: 0,

  span_hz: 0,

  start_frequency_hz: 0,

  stop_frequency_hz: 0,

  rbw_hz: 10000,

  vbw_hz: 10000,

  sweep_time_s: 0,

  reference_level_dbm: 0,

  attenuation: 0,

  gain: 0,

  auto_attenuation: true,

  auto_gain: true,

  detector: 1,

  rbw_shape: 0,

  spur_reject: 0,
})

const spurReject = computed({
  get: () => config.spur_reject === 1,
  set: (value: boolean) => {
    config.spur_reject = value ? 1 : 0
  },
})

const sweepTimeMs = computed({
  get: () => (config.sweep_time_s || 0) * 1000,
  set: (value: number) => {
    config.sweep_time_s = (value || 0) / 1000
  },
})

const centerMHz = computed({
  get: () => config.center_frequency_hz / 1e6,
  set: (value: number) =>
    config.center_frequency_hz = value * 1e6,
})

const spanMHz = computed({
  get: () => config.span_hz / 1e6,
  set: (value: number) =>
    config.span_hz = value * 1e6,
})

const startMHz = computed({
  get: () =>
    (config.center_frequency_hz - config.span_hz / 2) / 1e6,
  set: (value: number) => {
    const stopFreq = config.center_frequency_hz + config.span_hz / 2
    config.center_frequency_hz = (value * 1e6 + stopFreq) / 2
    config.span_hz = stopFreq - value * 1e6
  },
})

const stopMHz = computed({
  get: () =>
    (config.center_frequency_hz + config.span_hz / 2) / 1e6,
  set: (value: number) => {
    const startFreq = config.center_frequency_hz - config.span_hz / 2
    config.center_frequency_hz = (startFreq + value * 1e6) / 2
    config.span_hz = value * 1e6 - startFreq
  },
})

const rbwKHz = computed({
  get: () => config.rbw_hz / 1e3,
  set: (value: number) =>
    config.rbw_hz = value * 1e3,
})

const vbwKHz = computed({
  get: () => config.vbw_hz / 1e3,
  set: (value: number) =>
    config.vbw_hz = value * 1e3,
})

async function loadConfig() {
  const data = await getSpectrumConfig()
  Object.assign(config, data)
}

async function applyConfig() {
  await updateSpectrumConfig(config)
}

async function loadFavorite(startMHzValue: number, stopMHzValue: number) {
  startMHz.value = startMHzValue
  stopMHz.value = stopMHzValue
  await applyConfig()
}

async function onPresetLoaded(preset: any) {
  startMHz.value = preset.inicioMHz
  stopMHz.value = preset.finMHz
  await applyConfig()
}

onMounted(loadConfig)

</script>

<style scoped>

.controls {
  background: white;
  border: 1px solid var(--sncte-border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 20px;
  margin-bottom: 20px;
}

.controls h3 {
  margin-top: 0;
  margin-bottom: 16px;
  color: var(--sncte-blue-dark);
  font-size: 20px;
  font-weight: 700;
}

.favoritos {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  padding-bottom: 12px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--sncte-border);
}

.actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}

.favoritos button {
  background: #edf3ff;
  color: var(--sncte-blue-dark);
  border: 1px solid var(--sncte-border);
  border-radius: 20px;
  padding: 3px 8px;
  font-weight: 600;
  font-size: 11px;
  transition: all .2s ease;
}

.favoritos button:hover {
  background: var(--sncte-blue);
  color: white;
}

.mode-selector {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
  padding: 12px;
  background: #f8fbff;
  border: 1px solid var(--sncte-border);
  border-radius: 10px;
}

.mode-selector label {
  flex-direction: row;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: var(--sncte-blue-dark);
  font-weight: 500;
}

.grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

label {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

label.checkbox {
  flex-direction: row;
  align-items: center;
  gap: 8px;
}

span {
  color: var(--sncte-blue-dark);
  font-size: 11px;
  font-weight: 600;
}

input,
select {
  height: 28px;
  padding: 0 8px;
  background: white;
  color: var(--sncte-text);
  border: 1px solid var(--sncte-border);
  border-radius: 8px;
  font-size: 12px;
  transition: all .2s ease;
}

input:focus,
select:focus {
  outline: none;
  border-color: var(--sncte-blue);
  box-shadow: 0 0 0 3px rgba(0, 60, 158, 0.15);
}

input[readonly] {
  background: #f6f8fc;
  color: var(--sncte-blue-dark);
  font-weight: 600;
}

button {
  cursor: pointer;
  border: none;
  transition: all .2s ease;
}

.apply {
  background: var(--sncte-blue);
  color: white;
  border-radius: 10px;
  padding: 12px 18px;
  width: 100%;
  height: 32px;
  font-size: 13px;
  font-weight: 600;
}

.apply:hover {
  background: var(--sncte-blue-light);
  transform: translateY(-1px);
}

.apply:active {
  transform: translateY(0px);
}

</style>