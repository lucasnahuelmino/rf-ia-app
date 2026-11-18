<template>

  <div class="panel">

    <h3>Exportaciones</h3>

    <div class="row">
      <select v-model="format">
        <option value="csv">CSV</option>
        <option value="xlsx">XLSX</option>
        <option value="pdf">PDF</option>
      </select>
      <button @click="runExport">Exportar</button>
    </div>

    <div v-if="result" class="status">
      {{ result.path }}
    </div>

  </div>

</template>

<script setup lang="ts">

import { ref } from "vue"
import { API_BASE } from "../config"

const format = ref("csv")
const result = ref<any>(null)

async function runExport() {
  const rows = [{ frequency_mhz: 100, level_dbm: -50 }]
  const res = await fetch(`${API_BASE}/exports`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      format: format.value,
      filename: "export",
      rows,
    }),
  })
  result.value = await res.json()
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

select, button {
  height: 28px;
  border: 1px solid var(--sncte-border);
  border-radius: 6px;
}

button {
  background: var(--sncte-blue);
  color: white;
  border: none;
  padding: 0 12px;
  cursor: pointer;
}

.status {
  font-size: 12px;
  color: #374151;
  word-break: break-all;
}

</style>