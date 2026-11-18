<template>

  <div class="waterfall-container">

    <div class="controls">
      <button @click="paused = !paused">
        {{ paused ? "Reanudar" : "Pausar" }}
      </button>
      <button @click="clear">Limpiar</button>
      <label>
        Rango (dB)
        <input v-model.number="range" type="number" />
      </label>
    </div>

    <canvas ref="canvasRef"></canvas>

  </div>

</template>

<script setup lang="ts">

import { onMounted, onBeforeUnmount, ref, watch } from "vue"

const props = defineProps<{ snapshot: any }>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
const paused = ref(false)
const range = ref(80)

const history = ref<number[][]>([])
const maxRows = 200

let raf = 0

function pushRow() {
  if (paused.value) return
  if (!props.snapshot?.trace?.length) return

  const trace = props.snapshot.trace as number[]
  history.value.unshift([...trace])

  if (history.value.length > maxRows) {
    history.value.pop()
  }
}

function colorFor(value: number, min: number, max: number) {
  const norm = Math.min(1, Math.max(0, (value - min) / (max - min)))
  const r = Math.floor(255 * norm)
  const g = Math.floor(128 * norm)
  const b = Math.floor(255 * (1 - norm))
  return `rgb(${r},${g},${b})`
}

function draw() {
  const canvas = canvasRef.value
  if (!canvas) return

  const ctx = canvas.getContext("2d")
  if (!ctx) return

  const width = canvas.width
  const height = canvas.height

  ctx.fillStyle = "#000"
  ctx.fillRect(0, 0, width, height)

  if (!history.value.length) return

  const cols = history.value[0].length
  const cellWidth = width / cols
  const cellHeight = height / maxRows

  const min = -range.value
  const max = 0

  history.value.forEach((row, rowIndex) => {
    row.forEach((value, colIndex) => {
      ctx.fillStyle = colorFor(value, min, max)
      ctx.fillRect(
        colIndex * cellWidth,
        rowIndex * cellHeight,
        Math.ceil(cellWidth),
        Math.ceil(cellHeight),
      )
    })
  })
}

function clear() {
  history.value = []
  draw()
}

function loop() {
  pushRow()
  draw()
  raf = requestAnimationFrame(loop)
}

watch(() => props.snapshot, () => {}, { deep: true })

onMounted(() => {
  const canvas = canvasRef.value
  if (canvas) {
    canvas.width = 800
    canvas.height = 300
  }
  loop()
})

onBeforeUnmount(() => {
  cancelAnimationFrame(raf)
})

</script>

<style scoped>

.waterfall-container {
  background: #101010;
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  padding: 8px;
  margin-bottom: 12px;
}

.controls {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
  color: #e5e7eb;
  font-size: 12px;
}

.controls button {
  background: #1f2937;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
}

.controls input {
  width: 60px;
}

canvas {
  width: 100%;
  height: 300px;
  display: block;
}

</style>