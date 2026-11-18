<template>

  <div class="panel">

    <h3>Audio</h3>

    <div class="row">
      <button @click="recordDemo">
        Grabar demo WAV
      </button>
      <button @click="stop">
        Detener
      </button>
    </div>

    <div class="status">
      {{ status }}
    </div>

  </div>

</template>

<script setup lang="ts">

import { ref } from "vue"
import { API_BASE } from "../config"

const status = ref("Idle")

async function recordDemo() {
  status.value = "Grabando..."
  const response = await fetch(
    `${API_BASE}/audio/demo`,
    { method: "POST" }
  )
  const data = await response.json()
  status.value = `Completado: ${data.path}`
}

async function stop() {
  await fetch(`${API_BASE}/audio/record/stop`, { method: "POST" })
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
}

</style>