<template>
  <div class="panel">
    <h3>Editor de cadenas RF</h3>
    <div class="row">
      <select v-model="chainId">
        <option v-for="c in chains" :key="c.id" :value="c.id">{{ c.name }}</option>
      </select>
      <button @click="loadChain">Cargar</button>
    </div>
    <div class="row">
      <input v-model="newNodeType" placeholder="tipo (antenna, splitter, cable, amp, filter, receiver)" />
      <input v-model="newNodeName" placeholder="nombre" />
      <button @click="addNode">Agregar nodo</button>
      <button @click="save">Guardar topología</button>
    </div>
    <svg :width="600" :height="300" class="svg">
      <line v-for="(e, i) in edges" :key="i" :x1="nodePos(e.from).x" :y1="nodePos(e.from).y" :x2="nodePos(e.to).x" :y2="nodePos(e.to).y" stroke="#60a5fa" stroke-width="2" />
      <g v-for="(n, i) in nodes" :key="i">
        <rect :x="nodePos(n.id).x - 40" :y="nodePos(n.id).y - 20" width="80" height="40" rx="6" fill="#1f2937" stroke="#60a5fa" />
        <text :x="nodePos(n.id).x" :y="nodePos(n.id).y + 4" text-anchor="middle" fill="white" font-size="10">{{ n.name }}</text>
      </g>
    </svg>
    <div class="row">
      <select v-model="edgeFrom"><option v-for="n in nodes" :key="n.id" :value="n.id">{{ n.name }}</option></select>
      <span>→</span>
      <select v-model="edgeTo"><option v-for="n in nodes" :key="n.id" :value="n.id">{{ n.name }}</option></select>
      <button @click="addEdge">Conectar</button>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from "vue"
import { API_BASE } from "../config"
const chains = ref<any[]>([])
const chainId = ref<number | null>(null)
const nodes = ref<any[]>([])
const edges = ref<any[]>([])
const newNodeType = ref("antenna")
const newNodeName = ref("")
const edgeFrom = ref("")
const edgeTo = ref("")
function nodePos(id: string) {
  const idx = nodes.value.findIndex(n => n.id === id)
  const cols = 4
  const x = 80 + (idx % cols) * 140
  const y = 60 + Math.floor(idx / cols) * 90
  return { x, y }
}
async function loadChains() {
  const res = await fetch(`${API_BASE}/antennas`)
  chains.value = (await res.json()).items
}
async function loadChain() {
  if (!chainId.value) return
  const chain = chains.value.find(c => c.id === chainId.value)
  const topo = chain?.topology || {}
  nodes.value = topo.nodes || []
  edges.value = topo.edges || []
}
function addNode() {
  const id = `n${Date.now()}`
  nodes.value.push({ id, type: newNodeType.value, name: newNodeName.value || newNodeType.value })
  newNodeName.value = ""
}
function addEdge() {
  if (!edgeFrom.value || !edgeTo.value || edgeFrom.value === edgeTo.value) return
  edges.value.push({ from: edgeFrom.value, to: edgeTo.value })
}
async function save() {
  if (!chainId.value) return
  await fetch(`${API_BASE}/antennas/${chainId.value}/topology`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ nodes, edges }) })
}
onMounted(loadChains)
</script>
<style scoped>
.panel { background: white; border: 1px solid var(--sncte-border); border-radius: var(--radius); box-shadow: var(--shadow); padding: 12px; margin-bottom: 12px; }
.panel h3 { margin-top: 0; color: var(--sncte-blue-dark); }
.row { display: flex; gap: 8px; margin-bottom: 8px; flex-wrap: wrap; align-items: center; }
input, select { height: 28px; padding: 0 8px; border: 1px solid var(--sncte-border); border-radius: 6px; }
button { background: var(--sncte-blue); color: white; border: none; border-radius: 6px; padding: 4px 8px; cursor: pointer; }
.svg { background: #101010; border-radius: 6px; margin: 8px 0; }
</style>