<template>
  <div class="panel">
    <h3>Misiones</h3>
    <div class="row">
      <input v-model="name" placeholder="Nombre misión" />
      <button @click="create">Crear</button>
    </div>
    <ul>
      <li v-for="m in missions" :key="m.id">
        {{ m.name }} - {{ m.status }}
        <button @click="execute(m.id)">Ejecutar</button>
        <button @click="pause(m.id)">Pausar</button>
      </li>
    </ul>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from "vue"
import { API_BASE } from "../config"
const name = ref("")
const missions = ref<any[]>([])
async function load() {
  const res = await fetch(`${API_BASE}/missions`)
  missions.value = (await res.json()).items
}
async function create() {
  await fetch(`${API_BASE}/missions`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name: name.value }) })
  name.value = ""
  await load()
}
async function execute(id: number) {
  await fetch(`${API_BASE}/missions/${id}/execute`, { method: "POST" })
  await load()
}
async function pause(id: number) {
  await fetch(`${API_BASE}/missions/${id}/pause`, { method: "POST" })
  await load()
}
onMounted(load)
</script>
<style scoped>
.panel { background: white; border: 1px solid var(--sncte-border); border-radius: var(--radius); box-shadow: var(--shadow); padding: 12px; margin-bottom: 12px; }
.panel h3 { margin-top: 0; color: var(--sncte-blue-dark); }
.row { display: flex; gap: 8px; margin-bottom: 8px; }
input { flex: 1; height: 28px; padding: 0 8px; border: 1px solid var(--sncte-border); border-radius: 6px; }
button { background: var(--sncte-blue); color: white; border: none; border-radius: 6px; padding: 4px 8px; cursor: pointer; }
ul { list-style: none; padding: 0; }
li { padding: 4px 0; border-bottom: 1px solid #eef2f7; }
</style>