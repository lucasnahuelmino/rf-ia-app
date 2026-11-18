<template>
  <div class="panel">
    <h3>GPS</h3>
    <div class="row">
      <button @click="connectSimulated">Conectar simulado</button>
      <button @click="read">Leer posición</button>
      <button @click="disconnect">Desconectar</button>
    </div>
    <div class="status">{{ statusText }}</div>
    <div v-if="position" class="meta">
      Lat: {{ position.latitude }}<br />
      Lon: {{ position.longitude }}<br />
      Alt: {{ position.altitude }}<br />
      Sat: {{ position.satellites }}<br />
      Válido: {{ position.valid }}
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref } from "vue"
import { API_BASE } from "../config"
const statusText = ref("Desconectado")
const position = ref<any>(null)
async function connectSimulated() {
  const res = await fetch(`${API_BASE}/gps/connect/simulated`, { method: "POST" })
  const data = await res.json()
  statusText.value = data.connected ? (data.simulated ? "Simulado" : "Conectado") : "Desconectado"
}
async function read() {
  const res = await fetch(`${API_BASE}/gps/read`, { method: "POST" })
  const data = await res.json()
  position.value = data.position
}
async function disconnect() {
  await fetch(`${API_BASE}/gps/disconnect`, { method: "POST" })
  statusText.value = "Desconectado"
  position.value = null
}
</script>
<style scoped>
.panel { background: white; border: 1px solid var(--sncte-border); border-radius: var(--radius); box-shadow: var(--shadow); padding: 12px; margin-bottom: 12px; }
.panel h3 { margin-top: 0; color: var(--sncte-blue-dark); }
.row { display: flex; gap: 8px; margin-bottom: 8px; flex-wrap: wrap; }
button { background: var(--sncte-blue); color: white; border: none; border-radius: 6px; padding: 4px 8px; cursor: pointer; }
.status { font-size: 12px; color: #374151; margin-bottom: 8px; }
.meta { font-size: 12px; background: #f6f9ff; padding: 8px; border-radius: 6px; }
</style>