<template>
  <div class="panel">
    <h3>Receptores</h3>
    <button @click="discover">Detectar</button>
    <ul>
      <li v-for="d in devices" :key="d.serial_number">
        {{ d.alias || d.serial_number }} - {{ d.state }}
        <button @click="connect(d.serial_number)">Conectar</button>
        <button @click="disconnect(d.serial_number)">Desconectar</button>
      </li>
    </ul>
  </div>
</template>
<script setup lang="ts">
import { ref } from "vue"
import { API_BASE } from "../config"
const devices = ref<any[]>([])
async function discover() {
  const res = await fetch(`${API_BASE}/devices/multi/discover`, { method: "POST" })
  await res.json()
  await load()
}
async function load() {
  const res = await fetch(`${API_BASE}/devices/multi`)
  const data = await res.json()
  devices.value = data.items
}
async function connect(sn: number) {
  await fetch(`${API_BASE}/devices/multi/${sn}/connect`, { method: "POST" })
  await load()
}
async function disconnect(sn: number) {
  await fetch(`${API_BASE}/devices/multi/${sn}/disconnect`, { method: "POST" })
  await load()
}
</script>
<style scoped>
.panel { background: white; border: 1px solid var(--sncte-border); border-radius: var(--radius); box-shadow: var(--shadow); padding: 12px; margin-bottom: 12px; }
.panel h3 { margin-top: 0; color: var(--sncte-blue-dark); }
button { background: var(--sncte-blue); color: white; border: none; border-radius: 6px; padding: 4px 8px; cursor: pointer; margin-left: 4px; }
ul { list-style: none; padding: 0; }
li { padding: 4px 0; border-bottom: 1px solid #eef2f7; }
</style>