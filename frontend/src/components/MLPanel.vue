<template>

  <div class="panel">

    <h3>Machine Learning</h3>

    <div class="row">
      <button @click="extractFeatures">
        Extraer features
      </button>
    </div>

    <div v-if="features" class="response">
      <pre>{{ JSON.stringify(features, null, 2) }}</pre>
    </div>

  </div>

</template>

<script setup lang="ts">

import { ref } from "vue"
import { API_BASE } from "../config"

const features = ref<any>(null)

async function extractFeatures() {
  const trace = Array.from({ length: 100 }, (_, i) => Math.sin(i / 10))
  const res = await fetch(`${API_BASE}/ml/features/spectrum`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ trace }),
  })
  features.value = await res.json()
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
  margin-bottom: 8px;
}

button {
  background: var(--sncte-blue);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 6px 12px;
  cursor: pointer;
}

.response pre {
  font-size: 10px;
  max-height: 160px;
  overflow: auto;
  background: #f6f9ff;
  padding: 8px;
  border-radius: 6px;
}

</style>