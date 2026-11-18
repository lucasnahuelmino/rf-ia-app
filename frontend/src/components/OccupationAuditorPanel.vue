<template>
  <div class="panel">
    <h3>Auditor de ocupación</h3>
    <div class="row">
      <input v-model.number="startFreq" placeholder="Frecuencia inicial" />
      <input v-model.number="channelWidth" placeholder="Ancho canal" />
      <button @click="runAudit">Auditar</button>
    </div>
    <div v-if="results.length" class="results">
      <table>
        <thead><tr><th>Canal</th><th>Ocupación</th><th>Max</th><th>Ruido</th></tr></thead>
        <tbody>
          <tr v-for="(r, i) in results" :key="i">
            <td>{{ r.nominal_frequency_hz }}</td>
            <td>{{ (r.activity_ratio * 100).toFixed(1) }}%</td>
            <td>{{ r.max_power_dbm?.toFixed(2) }}</td>
            <td>{{ r.noise_floor_dbm?.toFixed(2) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref } from "vue"
import { API_BASE } from "../config"
const startFreq = ref(88000000)
const channelWidth = ref(200000)
const results = ref<any[]>([])
async function runAudit() {
  const channels = Array.from({ length: 5 }, (_, i) => ({ frequency: startFreq.value + i * channelWidth.value }))
  const res = await fetch(`${API_BASE}/occupation/audit`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ channels }) })
  const data = await res.json()
  results.value = data.items || []
}
</script>
<style scoped>
.panel { background: white; border: 1px solid var(--sncte-border); border-radius: var(--radius); box-shadow: var(--shadow); padding: 12px; margin-bottom: 12px; }
.panel h3 { margin-top: 0; color: var(--sncte-blue-dark); }
.row { display: flex; gap: 8px; margin-bottom: 8px; flex-wrap: wrap; }
input { flex: 1; height: 28px; padding: 0 8px; border: 1px solid var(--sncte-border); border-radius: 6px; }
button { background: var(--sncte-blue); color: white; border: none; border-radius: 6px; padding: 4px 8px; cursor: pointer; }
table { width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 8px; }
th, td { padding: 6px; border-bottom: 1px solid #eef2f7; text-align: left; }
</style>