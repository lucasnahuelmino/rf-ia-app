<template>
  <div class="panel">
    <h3>Heatmap avanzado</h3>
    <div class="row">
      <select v-model="metric">
        <option value="level_dbm">Potencia</option>
        <option value="noise_floor_dbm">Ruido</option>
      </select>
      <input v-model.number="gridSize" placeholder="Grid" />
      <button @click="run">Calcular</button>
    </div>
    <div v-if="result" class="meta">
      Celdas: {{ result.cells?.length }} | Min: {{ result.min }} | Max: {{ result.max }}
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref } from "vue"
import { API_BASE } from "../config"
const metric = ref("level_dbm")
const gridSize = ref(12)
const result = ref<any>(null)
async function run() {
  const res = await fetch(`${API_BASE}/spatial/heatmap`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ metric: metric.value, grid_size: gridSize.value }) })
  result.value = await res.json()
}
</script>
<style scoped>
.panel { background: white; border: 1px solid var(--sncte-border); border-radius: var(--radius); box-shadow: var(--shadow); padding: 12px; margin-bottom: 12px; }
.panel h3 { margin-top: 0; color: var(--sncte-blue-dark); }
.row { display: flex; gap: 8px; margin-bottom: 8px; flex-wrap: wrap; }
select, input, button { height: 28px; border: 1px solid var(--sncte-border); border-radius: 6px; }
button { background: var(--sncte-blue); color: white; border: none; padding: 0 12px; cursor: pointer; }
.meta { font-size: 12px; color: #374151; }
</style>