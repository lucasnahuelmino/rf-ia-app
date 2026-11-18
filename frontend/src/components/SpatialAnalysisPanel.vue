<template>
  <div class="panel">
    <h3>Análisis espacial</h3>
    <div class="row">
      <input v-model.number="frequency" placeholder="Frecuencia Hz" />
      <button @click="runFM">Analizar FM</button>
      <button @click="runHeatmap">Heatmap</button>
      <button @click="exportGeo">Exportar GeoJSON</button>
    </div>
    <div v-if="result" class="meta">
      <pre>{{ JSON.stringify(result, null, 2) }}</pre>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref } from "vue"
import { API_BASE } from "../config"
const frequency = ref(100000000)
const result = ref<any>(null)
async function runFM() {
  const res = await fetch(`${API_BASE}/spatial/fm-analysis`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ nominal_frequency_hz: frequency.value }) })
  result.value = await res.json()
}
async function runHeatmap() {
  const res = await fetch(`${API_BASE}/spatial/heatmap`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ metric: "level_dbm", grid_size: 10 }) })
  result.value = await res.json()
}
async function exportGeo() {
  const res = await fetch(`${API_BASE}/spatial/export-geojson`, { method: "POST" })
  result.value = await res.json()
}
</script>
<style scoped>
.panel { background: white; border: 1px solid var(--sncte-border); border-radius: var(--radius); box-shadow: var(--shadow); padding: 12px; margin-bottom: 12px; }
.panel h3 { margin-top: 0; color: var(--sncte-blue-dark); }
.row { display: flex; gap: 8px; margin-bottom: 8px; flex-wrap: wrap; }
input { flex: 1; height: 28px; padding: 0 8px; border: 1px solid var(--sncte-border); border-radius: 6px; }
button { background: var(--sncte-blue); color: white; border: none; border-radius: 6px; padding: 4px 8px; cursor: pointer; }
.meta pre { font-size: 10px; max-height: 200px; overflow: auto; background: #f6f9ff; padding: 8px; border-radius: 6px; }
</style>