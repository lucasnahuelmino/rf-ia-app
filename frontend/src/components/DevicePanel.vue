<template>

  <div class="panel">

    <h3>
      Estado del Instrumento
    </h3>

    <div class="grid">

      <div class="card">
        <span class="label">Equipo</span>
        <span class="value">BB60C</span>
      </div>

      <div class="card">
        <span class="label">Estado</span>
        <span class="value" :class="stateClass">
          {{ state }}
        </span>
      </div>

      <div class="card">
        <span class="label">Firmware</span>
        <span class="value">{{ firmware ?? "--" }}</span>
      </div>

      <div class="card">
        <span class="label">Serie</span>
        <span class="value">{{ serial ?? "--" }}</span>
      </div>

      <div class="card">
        <span class="label">Temperatura</span>
        <span class="value">
          {{ temperature !== null ? temperature.toFixed(1) : "--" }} °C
        </span>
      </div>

      <div class="card">
        <span class="label">Voltaje USB</span>
        <span class="value">
          {{ voltage !== null ? voltage.toFixed(2) : "--" }} V
        </span>
      </div>

      <div class="card">
        <span class="label">Corriente USB</span>
        <span class="value">
          {{ current !== null ? current : "--" }} mA
        </span>
      </div>

      <div class="card">
        <span class="label">API</span>
        <span class="value">{{ apiVersion ?? "--" }}</span>
      </div>

    </div>

  </div>

</template>

<script setup lang="ts">

import { onMounted, onBeforeUnmount, ref } from "vue"

import { API_BASE } from "../config"

const firmware = ref<number | null>(null)
const serial = ref<number | null>(null)
const temperature = ref<number | null>(null)
const voltage = ref<number | null>(null)
const current = ref<number | null>(null)
const apiVersion = ref<string | null>(null)
const state = ref<string>("DESCONOCIDO")

const stateClass = ref("")

let timer: number | null = null

async function fetchDiagnostics() {
  try {
    const response = await fetch(
      `${API_BASE}/devices/bb60c/diagnostics`
    )

    if (!response.ok) return

    const data = await response.json()

    firmware.value = data.firmware_version
    serial.value = data.serial_number
    temperature.value = data.temperature
    voltage.value = data.usb_voltage
    current.value = data.usb_current
    apiVersion.value = data.api_version
    state.value = data.state ?? "CONECTADO"
    stateClass.value = "success"
  } catch (error) {
    state.value = "ERROR"
    stateClass.value = "error"
  }
}

onMounted(() => {
  fetchDiagnostics()
  timer = window.setInterval(fetchDiagnostics, 3000)
})

onBeforeUnmount(() => {
  if (timer !== null) clearInterval(timer)
})

</script>

<style scoped>

.panel {
  background: white;
  border-radius: var(--radius);
  border: 1px solid var(--sncte-border);
  box-shadow: var(--shadow);
  padding: 16px;
  margin-bottom: 15px;
}

.panel h3 {
  margin-top: 0;
  color: var(--sncte-blue-dark);
}

.grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(120px, 1fr));
  gap: 8px;
}

.card {
  padding: 8px;
  border-radius: 8px;
  background: #f6f9ff;
}

.label {
  display: block;
  color: #5a6a85;
  font-size: 12px;
  margin-bottom: 6px;
  text-transform: uppercase;
}

.value {
  color: var(--sncte-blue-dark);
  font-size: 20px;
  font-weight: 600;
}

.success {
  color: #198754;
}

.error {
  color: #dc2626;
}

</style>