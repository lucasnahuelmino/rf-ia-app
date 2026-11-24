<template>
  <div class="panel">
    <h3>Audio en vivo</h3>
    <div class="row">
      <button @click="start">Iniciar</button>
      <button @click="stop">Detener</button>
      <input type="range" min="0" max="1" step="0.01" v-model.number="volume" @change="setVol" />
      <button @click="mute = !mute; setMute()">Mute</button>
    </div>
    <div class="status">{{ status }}</div>
  </div>
</template>
<script setup lang="ts">
import { ref } from "vue"
import { API_BASE } from "../config"
const status = ref("Detenido")
const volume = ref(1)
const mute = ref(false)
async function start() {
  await fetch(`${API_BASE}/audio/live/start`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ mode: "FM", frequency: 100e6 }) })
  status.value = "Reproduciendo"
}
async function stop() {
  await fetch(`${API_BASE}/audio/live/stop`, { method: "POST" })
  status.value = "Detenido"
}
async function setVol() {
  await fetch(`${API_BASE}/audio/live/volume?volume=${volume.value}`, { method: "POST" })
}
async function setMute() {
  await fetch(`${API_BASE}/audio/live/mute?muted=${mute.value}`, { method: "POST" })
}
</script>
<style scoped>
.panel { background: var(--bg-panel); border: 1px solid var(--border); border-radius: var(--radius); padding: 8px; margin-bottom: 8px; }
.panel h3 { margin: 0 0 6px 0; color: var(--accent); font-size: 12px; }
.row { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }
button { padding: 4px 8px; border: 1px solid var(--border-2); border-radius: 4px; background: var(--bg-panel-2); color: var(--text); cursor: pointer; font-size: 11px; }
.status { font-size: 11px; color: var(--text-muted); margin-top: 4px; }
</style>