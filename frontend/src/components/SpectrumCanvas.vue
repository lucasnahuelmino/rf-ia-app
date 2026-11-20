<template>

  <div
    ref="containerRef"
    class="canvas-container"
  >

    <canvas
      ref="canvasRef"
      @mousemove="onMouseMove"
      @mousedown="onMouseDown"
      @mouseup="onMouseUp"
      @mouseleave="onMouseLeave"
      @click="onCanvasClick"
      @wheel.prevent="onZoom"
    />

    <div
      v-if="cursorInfo"
      class="cursor-readout"
    >
      {{ cursorInfo }}
    </div>

  </div>

</template>

<script setup lang="ts">

import {
  onMounted,
  onBeforeUnmount,
  ref,
  watch,
} from "vue"

import {
  markers,
} from "../composables/useMarkers"

const props = defineProps({
  snapshot: Object,
  showMaxHold: Boolean,
  showMinHold: Boolean,
  showAverage: Boolean,
  maxHold: Array,
  minHold: Array,
  averageTrace: Array,
})

const emit = defineEmits([
  "moveCenter",
  "zoom",
  "pan",
])

const containerRef =
  ref<HTMLDivElement | null>(null)

const canvasRef =
  ref<HTMLCanvasElement | null>(null)

const cursorX =
  ref<number | null>(null)

const cursorY =
  ref<number | null>(null)

const cursorInfo =
  ref<string | null>(null)

const isPanning =
  ref(false)

const panStartX =
  ref(0)

const panStartCenter =
  ref(0)

const DBM_TOP = 0
const DBM_BOTTOM = -130

let resizeObserver: ResizeObserver | null = null

function resizeCanvas() {
  const canvas = canvasRef.value
  const container = containerRef.value

  if (!canvas || !container) return

  const rect = container.getBoundingClientRect()

  const width = Math.max(320, Math.floor(rect.width))
  const height = Math.max(240, Math.floor(rect.height || 600))

  if (canvas.width !== width) canvas.width = width
  if (canvas.height !== height) canvas.height = height

  draw()
}

function onMouseMove(event: MouseEvent) {
  const canvas = canvasRef.value
  if (!canvas) return

  const rect = canvas.getBoundingClientRect()

  cursorX.value = event.clientX - rect.left
  cursorY.value = event.clientY - rect.top

  updateCursorInfo()

  if (isPanning.value) {
    const deltaPx = cursorX.value - panStartX.value
    const snapshot = props.snapshot as any
    if (!snapshot) return

    const spanHz =
      snapshot.stop_frequency_hz - snapshot.start_frequency_hz

    const deltaHz = -(deltaPx / canvas.width) * spanHz

    emit("pan", panStartCenter.value + deltaHz)
  }

  draw()
}

function onMouseDown(event: MouseEvent) {
  const snapshot = props.snapshot as any
  if (!snapshot) return

  isPanning.value = true
  panStartX.value = event.offsetX
  panStartCenter.value = snapshot.center_frequency_hz
}

function onMouseUp() {
  isPanning.value = false
}

function onMouseLeave() {
  cursorX.value = null
  cursorY.value = null
  cursorInfo.value = null
  isPanning.value = false
  draw()
}

function onZoom(event: WheelEvent) {
  emit("zoom", event.deltaY)
}

function onCanvasClick(event: MouseEvent) {
  const canvas = canvasRef.value
  if (!canvas) return

  const snapshot = props.snapshot as any
  if (!snapshot) return

  const rect = canvas.getBoundingClientRect()

  const x = event.clientX - rect.left

  const ratio = x / canvas.width

  const frequencyHz =
    snapshot.start_frequency_hz +
    ratio *
      (snapshot.stop_frequency_hz - snapshot.start_frequency_hz)

  const selected = markers.value.find(
    (marker) => marker.selected
  )

  if (!selected) return

  selected.enabled = true
  selected.frequencyHz = frequencyHz

  const trace = snapshot.trace as number[] | undefined
  if (trace?.length) {
    const binIndex = Math.min(
      trace.length - 1,
      Math.max(0, Math.round(ratio * (trace.length - 1)))
    )
    selected.powerDbm = trace[binIndex]
  }

  if (selected.id === "CENTRO") {
    emit("moveCenter", frequencyHz)
  }

  draw()
}

function updateCursorInfo() {
  const canvas = canvasRef.value
  const snapshot = props.snapshot as any

  if (
    !canvas ||
    !snapshot ||
    cursorX.value === null ||
    cursorY.value === null
  ) {
    cursorInfo.value = null
    return
  }

  const spanHz =
    snapshot.stop_frequency_hz - snapshot.start_frequency_hz

  const frequencyHz =
    snapshot.start_frequency_hz +
    (cursorX.value / canvas.width) * spanHz

  const powerDbm = yToDbm(cursorY.value, canvas.height)

  cursorInfo.value = `${(frequencyHz / 1e6).toFixed(4)} MHz | ${powerDbm.toFixed(2)} dBm`
}

function dbmToY(power: number, height: number) {
  return (
    height -
    ((power - DBM_BOTTOM) / (DBM_TOP - DBM_BOTTOM)) * height
  )
}

function yToDbm(y: number, height: number) {
  return (
    DBM_BOTTOM +
    ((height - y) / height) * (DBM_TOP - DBM_BOTTOM)
  )
}

function drawGrid(ctx: CanvasRenderingContext2D, width: number, height: number) {
  ctx.strokeStyle = "#2a2a2a"
  ctx.lineWidth = 1

  for (let i = 0; i <= 10; i++) {
    const x = (i / 10) * width
    ctx.beginPath()
    ctx.moveTo(x, 0)
    ctx.lineTo(x, height)
    ctx.stroke()
  }

  for (let i = 0; i <= 10; i++) {
    const y = (i / 10) * height
    ctx.beginPath()
    ctx.moveTo(0, y)
    ctx.lineTo(width, y)
    ctx.stroke()
  }
}

function drawDbmScale(ctx: CanvasRenderingContext2D, height: number) {
  ctx.fillStyle = "#bbbbbb"
  ctx.font = "12px monospace"

  for (let i = 0; i <= 10; i++) {
    const dbm = DBM_TOP - i * 10
    const y = (i / 10) * height
    ctx.fillText(`${dbm} dBm`, 8, y + 12)
  }
}

function drawFrequencyLabels(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  snapshot: any,
) {
  ctx.fillStyle = "#ffffff"
  ctx.font = "12px monospace"

  ctx.fillText(
    `START ${(snapshot.start_frequency_hz / 1e6).toFixed(3)} MHz`,
    10,
    height - 8,
  )

  ctx.fillText(
    `CENTER ${(snapshot.center_frequency_hz / 1e6).toFixed(3)} MHz`,
    width / 2 - 80,
    height - 8,
  )

  ctx.fillText(
    `STOP ${(snapshot.stop_frequency_hz / 1e6).toFixed(3)} MHz`,
    width - 180,
    height - 8,
  )
}

function drawTrace(
  ctx: CanvasRenderingContext2D,
  trace: number[],
  width: number,
  height: number,
  color: string,
  lineWidth: number,
) {
  if (!trace?.length) return

  ctx.strokeStyle = color
  ctx.lineWidth = lineWidth
  ctx.beginPath()

  for (let i = 0; i < trace.length; i++) {
    const x = (i / Math.max(1, trace.length - 1)) * width
    const y = dbmToY(trace[i], height)

    if (i === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  }

  ctx.stroke()
}

function drawLegend(ctx: CanvasRenderingContext2D, width: number) {
  ctx.font = "12px monospace"

  const entries = [
    { label: "LIVE", color: "#60a5fa" },
    { label: "MAX HOLD", color: "#f59e0b" },
    { label: "MIN HOLD", color: "#f87171" },
    { label: "AVERAGE", color: "#06b6d4" },
  ]

  entries.forEach((entry, index) => {
    ctx.fillStyle = entry.color
    ctx.fillText(entry.label, width - 120, 18 + index * 16)
  })
}

function drawMarkers(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  snapshot: any,
) {
  const trace = snapshot.trace as number[] | undefined
  if (!trace?.length) return

  markers.value.forEach((marker) => {
    if (!marker.frequencyHz) return

    const ratio =
      (marker.frequencyHz - snapshot.start_frequency_hz) /
      (snapshot.stop_frequency_hz - snapshot.start_frequency_hz)

    const x = ratio * width

    const color =
      marker.id === "CENTRO" ? "#22c55e" : "#fbbf24"

    ctx.strokeStyle = color
    ctx.lineWidth = 1
    ctx.beginPath()
    ctx.moveTo(x, 0)
    ctx.lineTo(x, height)
    ctx.stroke()

    ctx.fillStyle = color
    ctx.font = "12px monospace"
    ctx.fillText(marker.id, x + 4, 36)
  })
}

function drawCursor(ctx: CanvasRenderingContext2D, width: number, height: number) {
  if (cursorX.value === null || cursorY.value === null) return

  ctx.strokeStyle = "#888"
  ctx.lineWidth = 1

  ctx.beginPath()
  ctx.moveTo(cursorX.value, 0)
  ctx.lineTo(cursorX.value, height)
  ctx.stroke()

  ctx.beginPath()
  ctx.moveTo(0, cursorY.value)
  ctx.lineTo(width, cursorY.value)
  ctx.stroke()
}

function drawSpectrum(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
) {
  const snapshot = props.snapshot as any
  if (!snapshot?.trace?.length) return

  const trace = snapshot.trace as number[]

  if (props.showAverage && props.averageTrace) {
    drawTrace(
      ctx,
      props.averageTrace as number[],
      width,
      height,
      "#06b6d4",
      1,
    )
  }

  if (props.showMaxHold && props.maxHold) {
    drawTrace(
      ctx,
      props.maxHold as number[],
      width,
      height,
      "#f59e0b",
      1,
    )
  }

  if (props.showMinHold && props.minHold) {
    drawTrace(
      ctx,
      props.minHold as number[],
      width,
      height,
      "#f87171",
      1,
    )
  }

  drawTrace(ctx, trace, width, height, "#60a5fa", 2)

  // peak indicator
  let peakIndex = 0
  let peakValue = Number.NEGATIVE_INFINITY

  trace.forEach((value, index) => {
    if (value > peakValue) {
      peakValue = value
      peakIndex = index
    }
  })

  const peakX = (peakIndex / Math.max(1, trace.length - 1)) * width
  const peakY = dbmToY(peakValue, height)

  ctx.fillStyle = "#fbbf24"
  ctx.fillRect(peakX - 3, peakY - 20, 6, 20)

  ctx.fillStyle = "#fbbf24"
  ctx.font = "13px monospace"

  const peakFrequencyHz =
    snapshot.start_frequency_hz + peakIndex * snapshot.bin_size_hz

  ctx.fillText(
    `PEAK ${(peakFrequencyHz / 1e6).toFixed(4)} MHz | ${peakValue.toFixed(2)} dBm`,
    16,
    20,
  )
}

function draw() {
  const canvas = canvasRef.value
  if (!canvas) return

  if (!props.snapshot) return

  const ctx = canvas.getContext("2d")
  if (!ctx) return

  resizeCanvasGuard()

  const width = canvas.width
  const height = canvas.height

  ctx.clearRect(0, 0, width, height)

  ctx.fillStyle = "#101010"
  ctx.fillRect(0, 0, width, height)

  const snapshot = props.snapshot as any

  drawGrid(ctx, width, height)
  drawDbmScale(ctx, height)
  drawFrequencyLabels(ctx, width, height, snapshot)
  drawLegend(ctx, width)
  drawSpectrum(ctx, width, height)
  drawMarkers(ctx, width, height, snapshot)
  drawCursor(ctx, width, height)
}

function resizeCanvasGuard() {
  const canvas = canvasRef.value
  const container = containerRef.value
  if (!canvas || !container) return

  const rect = container.getBoundingClientRect()
  const width = Math.max(320, Math.floor(rect.width))
  const height = Math.max(240, Math.floor(rect.height || 600))

  if (canvas.width !== width) canvas.width = width
  if (canvas.height !== height) canvas.height = height
}

watch(() => props.snapshot, draw, { deep: true })
watch(
  () => [
    props.showAverage,
    props.showMaxHold,
    props.showMinHold,
    props.maxHold,
    props.minHold,
    props.averageTrace,
  ],
  draw,
  { deep: true },
)

onMounted(() => {
  resizeCanvas()

  resizeObserver = new ResizeObserver(() => {
    resizeCanvas()
  })

  if (containerRef.value) {
    resizeObserver.observe(containerRef.value)
  }
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
})

</script>

<style scoped>

.canvas-container {
  position: relative;
  width: 100%;
  height: 300px;
  background: #101010;
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  overflow: hidden;
}

canvas {
  display: block;
  width: 100%;
  height: 100%;
  cursor: crosshair;
}

.cursor-readout {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.7);
  color: #e5e7eb;
  font-family: monospace;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  pointer-events: none;
}

</style>