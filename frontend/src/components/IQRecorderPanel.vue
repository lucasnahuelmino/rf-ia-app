<template>

  <div class="panel">

    <h3>Grabación I/Q</h3>

    <div class="row">
      <button @click="startDemo">
        Grabar demo
      </button>
      <button @click="stop">
        Detener
      </button>
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

const status = ref("Idle")
const metadata = ref<any>(null)

async function startDemo() {
  status.value = "Grabando..."
  const response = await fetch(
    `${API_BASE}/iq/record/demo?seconds=1&sample_rate=1000000`,
    { method: "POST" }
  )
  const data = await response.json()
  metadata.value = data.metadata
  status.value = "Completado"
}

async function stop() {
  const response = await fetch(
    `${API_BASE}/iq/record/stop`,
    { method: "POST" }
  )
  const data = await response.json()
  status.value = "Detenido"
  metadata.value = data.metadata ?? metadata.value
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