<template>

  <div class="panel">

    <h3>Biblioteca de grabaciones</h3>

    <button @click="load">
      Actualizar
    </button>

    <table>
      <thead>
        <tr>
          <th>Archivo</th>
          <th>Tamaño</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.name">
          <td>{{ item.name }}</td>
          <td>{{ item.size }}</td>
          <td>
            <button @click="remove(item.name)">
              Eliminar
            </button>
          </td>
        </tr>
      </tbody>
    </table>

  </div>

</template>

<script setup lang="ts">

import { onMounted, ref } from "vue"
import { API_BASE } from "../config"

const items = ref<any[]>([])

async function load() {
  const response = await fetch(`${API_BASE}/recordings`)
  const data = await response.json()
  items.value = data.items
}

async function remove(name: string) {
  await fetch(`${API_BASE}/recordings/${encodeURIComponent(name)}`, {
    method: "DELETE",
  })
  await load()
}

onMounted(load)

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

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  margin-top: 8px;
}

th, td {
  padding: 6px;
  border-bottom: 1px solid #eef2f7;
  text-align: left;
}

button {
  background: var(--sncte-blue);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 4px 8px;
  cursor: pointer;
}

</style>