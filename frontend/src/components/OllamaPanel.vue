<template>

  <div class="panel">

    <h3>Asistente IA (Ollama)</h3>

    <div class="row">
      <button @click="checkStatus">Estado</button>
      <span>{{ statusText }}</span>
    </div>

    <div class="row">
      <select v-model="model">
        <option v-for="m in models" :key="m">{{ m }}</option>
      </select>
    </div>

    <textarea v-model="prompt" rows="3" placeholder="Preguntá sobre el espectro..."></textarea>

    <button @click="generate">Enviar</button>

    <div v-if="response" class="response">
      {{ response }}
    </div>

  </div>

</template>

<script setup lang="ts">

import { ref } from "vue"
import { API_BASE } from "../config"

const statusText = ref("Desconocido")
const models = ref<string[]>([])
const model = ref("")
const prompt = ref("")
const response = ref("")

async function checkStatus() {
  const res = await fetch(`${API_BASE}/ollama/status`)
  const data = await res.json()
  if (data.available) {
    statusText.value = "Disponible"
    models.value = data.models || []
    if (!model.value && models.value.length) model.value = models.value[0]
  } else {
    statusText.value = "No disponible"
    models.value = []
  }
}

async function generate() {
  if (!model.value) return
  const res = await fetch(`${API_BASE}/ollama/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model: model.value, prompt: prompt.value }),
  })
  const data = await res.json()
  response.value = data.response || data.error || "Sin respuesta"
}

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

.row {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

textarea {
  width: 100%;
  margin-bottom: 8px;
  border: 1px solid var(--sncte-border);
  border-radius: 6px;
  padding: 6px;
}

button {
  background: var(--sncte-blue);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 6px 12px;
  cursor: pointer;
}

.response {
  margin-top: 8px;
  font-size: 12px;
  background: #f6f9ff;
  padding: 8px;
  border-radius: 6px;
  white-space: pre-wrap;
}

</style>