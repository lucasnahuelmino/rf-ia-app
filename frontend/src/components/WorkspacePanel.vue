<template>
  <div class="panel">
    <h3>Workspace</h3>
    <div class="tabs">
      <button v-for="t in tabs" :key="t.id" @click="active = t.id" :class="{ active: active === t.id }">{{ t.name }}</button>
      <button @click="addTab">+ Nueva vista</button>
    </div>
    <div class="content">
      Vista activa: {{ active }}
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref } from "vue"
const tabs = ref([{ id: 1, name: "Vista 1" }])
const active = ref(1)
let nextId = 2
function addTab() { tabs.value.push({ id: nextId, name: `Vista ${nextId}` }); active.value = nextId; nextId++ }
</script>
<style scoped>
.panel { background: var(--bg-panel); border: 1px solid var(--border); border-radius: var(--radius); padding: 8px; }
.panel h3 { margin: 0 0 6px 0; color: var(--accent); font-size: 12px; }
.tabs { display: flex; gap: 4px; margin-bottom: 8px; flex-wrap: wrap; }
.tabs button { padding: 4px 8px; border: 1px solid var(--border-2); border-radius: 4px; background: var(--bg-panel-2); color: var(--text); cursor: pointer; font-size: 11px; }
.tabs button.active { background: linear-gradient(135deg, #0ea5e9, #2563eb); color: white; border: none; }
.content { color: var(--text-muted); font-size: 11px; }
</style>