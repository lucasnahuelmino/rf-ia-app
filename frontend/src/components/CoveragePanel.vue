<template>
  <div class="panel">
    <h3>Cobertura</h3>
    <div class="row">
      <select v-model="model">
        <option value="free_space">Espacio libre</option>
        <option value="okumura_hata">Okumura-Hata</option>
        <option value="cost231_hata">COST-231 Hata</option>
      </select>
      <button @click="predict">Predecir</button>
    </div>
    <div v-if="result" class="meta">
      <pre>{{ JSON.stringify(result, null, 2) }}</pre>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref } from "vue"
import { API_BASE } from "../config"
const model = ref("free_space")
const result = ref<any>(null)
async function predict() {
  const params = {
    frequency_hz: 100000000,
    distance_km: 1,
    tx_power_dbm: 30,
    tx_gain_dbi: 6,
    rx_gain_dbi: 0,
    losses_db: 0,
    tx_height_m: 30,
    rx_height_m: 1.5,
  }
  const res = await fetch(`${API_BASE}/coverage/predict`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ model: model.value, params }) })
  result.value = await res.json()
}
</script>
<style scoped>
.panel { background: white; border: 1px solid var(--sncte-border); border-radius: var(--radius); box-shadow: var(--shadow); padding: 12px; margin-bottom: 12px; }
.panel h3 { margin-top: 0; color: var(--sncte-blue-dark); }
.row { display: flex; gap: 8px; margin-bottom: 8px; }
select, button { height: 28px; border: 1px solid var(--sncte-border); border-radius: 6px; }
button { background: var(--sncte-blue); color: white; border: none; padding: 0 12px; cursor: pointer; }
.meta pre { font-size: 10px; max-height: 200px; overflow: auto; background: #f6f9ff; padding: 8px; border-radius: 6px; }
</style>