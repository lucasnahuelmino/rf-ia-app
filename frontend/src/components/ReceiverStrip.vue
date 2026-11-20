<template>
  <div class="receiver-strip">
    <div v-if="devices.length === 0" class="empty">
      Sin receptores detectados
      <button @click="discover">Detectar</button>
    </div>
    <div v-for="d in devices" :key="d.serial_number" class="mini" :class="stateClass(d.state)" @click="select(d)">
      <div class="led" :class="stateClass(d.state)"></div>
      <div class="alias">{{ d.alias || d.serial_number }}</div>
      <div class="serial">S/N {{ d.serial_number }}</div>
      <div class="fw">FW {{ d.firmware_version || '--' }}</div>
      <div class="status">{{ d.state }}</div>
    </div>
    <button class="detect" @click="discover">Detectar</button>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from "vue"
import { API_BASE } from "../config"
const devices = ref<any[]>([])
const emit = defineEmits(["select"])
async function discover() {
  await fetch(`${API_BASE}/devices/multi/discover`, { method: "POST" })
  await load()
}
async function load() {
  const res = await fetch(`${API_BASE}/devices/multi`)
  devices.value = (await res.json()).items || []
}
function select(d: any) { emit("select", d) }
function stateClass(state: string) {
  const s = (state || "").toLowerCase()
  if (s.includes("connect") || s.includes("acquir")) return "ok"
  if (s.includes("error")) return "error"
  if (s.includes("busy") || s.includes("ocup")) return "busy"
  return "idle"
}
onMounted(load)
</script>
<style scoped>
.receiver-strip {
  display: flex;
  gap: 6px;
  align-items: stretch;
  padding: 4px 6px;
  background: #0f172a;
  border-radius: 6px;
  overflow-x: auto;
  height: 56px;
}
.empty {
  color: #94a3b8;
  font-size: 11px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.mini {
  min-width: 120px;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 4px;
  padding: 4px 6px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 1px;
}
.mini.ok { border-color: #22c55e; }
.mini.error { border-color: #ef4444; }
.mini.busy { border-color: #f59e0b; }
.led {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #64748b;
  position: absolute;
}
.mini { position: relative; }
.led.ok { background: #22c55e; box-shadow: 0 0 6px #22c55e; }
.led.error { background: #ef4444; box-shadow: 0 0 6px #ef4444; }
.led.busy { background: #f59e0b; box-shadow: 0 0 6px #f59e0b; }
.alias { color: #e2e8f0; font-size: 11px; font-weight: 700; }
.serial { color: #94a3b8; font-size: 9px; }
.fw { color: #94a3b8; font-size: 9px; }
.status { color: #cbd5e1; font-size: 9px; text-transform: uppercase; }
.detect {
  min-width: 70px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 10px;
}
</style>