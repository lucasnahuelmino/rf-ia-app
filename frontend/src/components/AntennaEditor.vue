<template>
  <div class="panel">
    <h3>Antenas y cadenas RF</h3>
    <div class="row">
      <input v-model="name" placeholder="Nombre cadena" />
      <input v-model="componentsText" placeholder="componentes separados por coma" />
      <button @click="create">Crear</button>
    </div>
    <ul>
      <li v-for="c in chains" :key="c.id">
        {{ c.name }} ({{ (c.components || []).join(" -> ") }})
        <button @click="remove(c.id)">Eliminar</button>
      </li>
    </ul>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from "vue"
import { API_BASE } from "../config"
const name = ref("")
const componentsText = ref("")
const chains = ref<any[]>([])
async function load() {
  const res = await fetch(`${API_BASE}/antennas`)
  chains.value = (await res.json()).items
}
async function create() {
  const components = componentsText.value.split(",").map(s => s.trim()).filter(Boolean)
  await fetch(`${API_BASE}/antennas`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name: name.value, components }) })
  name.value = ""
  componentsText.value = ""
  await load()
}
async function remove(id: number) {
  await fetch(`${API_BASE}/antennas/${id}`, { method: "DELETE" })
  await load()
}
onMounted(load)
</script>
<style scoped>
.panel { background: white; border: 1px solid var(--sncte-border); border-radius: var(--radius); box-shadow: var(--shadow); padding: 12px; margin-bottom: 12px; }
.panel h3 { margin-top: 0; color: var(--sncte-blue-dark); }
.row { display: flex; gap: 8px; margin-bottom: 8px; flex-wrap: wrap; }
input { flex: 1; height: 28px; padding: 0 8px; border: 1px solid var(--sncte-border); border-radius: 6px; }
button { background: var(--sncte-blue); color: white; border: none; border-radius: 6px; padding: 4px 8px; cursor: pointer; }
ul { list-style: none; padding: 0; }
li { padding: 4px 0; border-bottom: 1px solid #eef2f7; display: flex; justify-content: space-between; align-items: center; }
</style>