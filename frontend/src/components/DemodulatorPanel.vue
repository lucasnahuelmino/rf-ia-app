<template>

  <div class="panel">

    <h3>Demodulador</h3>

    <div class="row">
      <label>
        Modo
        <select v-model="mode">
          <option v-for="m in modes" :key="m">{{ m }}</option>
        </select>
      </label>

      <button @click="runSynthetic">
        Demod sintética
      </button>
    </div>

    <div class="status">
      {{ status }}
    </div>

    <div v-if="result" class="meta">
      <pre>{{ JSON.stringify(result, null, 2) }}</pre>
    </div>

  </div>

</template>

<script setup lang="ts">

import { ref } from "vue"
import { API_BASE } from "../config"

const modes = ["AM", "FM", "WFM", "NFM", "USB", "LSB", "CW"]
const mode = ref("WFM")
const status = ref("Idle")
const result = ref<any>(null)

async function runSynthetic() {
  status.value = "Procesando..."
  const response = await fetch(
    `${API_BASE}/demod/synthetic`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        mode: mode.value,
        sample_rate: 1000000,
        audio_rate: 48000,
        duration_seconds: 0.5,
      }),
    }
  )
  const data = await response.json()
  result.value = data
  status.value = "Completado"
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
  align-items: center;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

select {
  height: 28px;
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