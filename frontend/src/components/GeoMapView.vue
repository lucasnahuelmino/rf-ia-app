<template>
  <div class="panel">
    <h3>Mapa georreferenciado</h3>
    <button @click="load">Actualizar</button>
    <canvas ref="canvasRef" width="400" height="300"></canvas>
    <div class="count">{{ points.length }} puntos</div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from "vue"
import { API_BASE } from "../config"
const canvasRef = ref<HTMLCanvasElement | null>(null)
const points = ref<any[]>([])
async function load() {
  const res = await fetch(`${API_BASE}/geo/list?limit=500`)
  const data = await res.json()
  points.value = data.items || []
  draw()
}
function draw() {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext("2d")
  if (!ctx) return
  ctx.fillStyle = "#101010"
  ctx.fillRect(0, 0, canvas.width, canvas.height)
  if (!points.value.length) return
  const lats = points.value.map((p) => p.latitude)
  const lons = points.value.map((p) => p.longitude)
  const minLat = Math.min(...lats)
  const maxLat = Math.max(...lats)
  const minLon = Math.min(...lons)
  const maxLon = Math.max(...lons)
  points.value.forEach((p) => {
    const x = ((p.longitude - minLon) / (maxLon - minLon || 1)) * (canvas.width - 20) + 10
    const y = canvas.height - (((p.latitude - minLat) / (maxLat - minLat || 1)) * (canvas.height - 20) + 10)
    ctx.fillStyle = "#60a5fa"
    ctx.beginPath()
    ctx.arc(x, y, 3, 0, Math.PI * 2)
    ctx.fill()
  })
}
onMounted(load)
</script>
<style scoped>
.panel { background: white; border: 1px solid var(--sncte-border); border-radius: var(--radius); box-shadow: var(--shadow); padding: 12px; margin-bottom: 12px; }
.panel h3 { margin-top: 0; color: var(--sncte-blue-dark); }
button { background: var(--sncte-blue); color: white; border: none; border-radius: 6px; padding: 4px 8px; cursor: pointer; margin-bottom: 8px; }
canvas { width: 100%; height: 300px; border: 1px solid #2a2a2a; border-radius: 6px; }
.count { font-size: 12px; color: #374151; margin-top: 4px; }
</style>