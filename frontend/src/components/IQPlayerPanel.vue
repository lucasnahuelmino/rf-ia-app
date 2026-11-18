<template>

  <div class="panel">

    <h3>Reproductor I/Q</h3>

    <div class="row">
      <input v-model="filename" placeholder="archivo.iq" />
    </div>

    <div class="row">
      <button @click="openFile">Abrir</button>
      <button @click="play">Play</button>
      <button @click="pause">Pausa</button>
      <button @click="stop">Stop</button>
    </div>

    <div class="status">
      {{ status }}
    </div>

    <div v-if="metadata" class="meta">
      <pre>{{ JSON.stringify(metadata, null, 2) }}</pre>
    </div>

  </div>

</template>

<script setup lang="ts">

import { ref } from "vue"
import { API_BASE } from "../config"

const filename = ref("demo.iq")
const status = ref("Idle")
const metadata = ref<any>(null)

async function openFile() {
  const response = await fetch(
    `${API_BASE}/iq/play/open?filename=${encodeURIComponent(filename.value)}`,
    { method: "POST" }
  )
  const data = await response.json()
  metadata.value = data.metadata
  status.value = "Abierto"
}

async function play() {
  await fetch(`${API_BASE}/iq/play/start`, { method: "POST" })
  status.value = "Reproduciendo"
}

async function pause() {
  await fetch(`${API_BASE}/iq/play/pause`, { method: "POST" })
  status.value = "Pausado"
}

async function stop() {
  await fetch(`${API_BASE}/iq/play/stop`, { method: "POST" })
  status.value = "Detenido"
}

</script>

<style scoped>

.panel {
  background: white;
  border: 1px solid var(--sncte-border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 12px;
  margin-bottom: 12px;
}

.panel h3 {
  margin-top: 0;
  color: var(--sncte-blue-dark);
}

.row {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

input {
  flex: 1;
  height: 28px;
  padding: 0 8px;
  border: 1px solid var(--sncte-border);
  border-radius: 6px;
}

button {
  background: var(--sncte-blue);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 6px 12px;
  cursor: pointer;
}

.status {
  font-size: 12px;
  color: #374151;
  margin-bottom: 8px;
}

.meta pre {
  font-size: 10px;
  max-height: 160px;
  overflow: auto;
  background: #f6f9ff;
  padding: 8px;
  border-radius: 6px;
}

</style>