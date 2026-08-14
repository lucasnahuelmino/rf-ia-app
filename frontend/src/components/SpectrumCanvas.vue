<template>

  <canvas
    ref="canvasRef"
    width="1100"
    height="600"
    @mousemove="onMouseMove"
    @click="onCanvasClick"
  />

</template>

<script setup lang="ts">

import {
  onMounted,
  ref,
  watch,
} from "vue"

import {
  markers,
} from "../composables/useMarkers"

const props = defineProps({

  snapshot: Object,

  showMaxHold: Boolean,

  showAverage: Boolean,

  maxHold: Array,

  averageTrace: Array,
})

const canvasRef =
  ref<HTMLCanvasElement | null>(null)

const cursorX =
  ref<number | null>(null)

const cursorY =
  ref<number | null>(null)

const DBM_TOP = 0
const DBM_BOTTOM = -130

function onMouseMove(
  event: MouseEvent,
) {

  const canvas =
    canvasRef.value

  if (!canvas)
    return

  const rect =
    canvas.getBoundingClientRect()

  cursorX.value =
    event.clientX - rect.left

  cursorY.value =
    event.clientY - rect.top
}

function onCanvasClick(
  event: MouseEvent,
) {

  const canvas =
    canvasRef.value

  if (!canvas)
    return

  const snapshot =
    props.snapshot as any

  const rect =
    canvas.getBoundingClientRect()

  const x =
    event.clientX - rect.left

  const ratio =
    x / canvas.width

  const frequencyHz =
    snapshot.start_frequency_hz
    +
    (
      ratio
      *
      (
        snapshot.stop_frequency_hz
        -
        snapshot.start_frequency_hz
      )
    )

  const selected =
    markers.value.find(
      marker =>
        marker.selected
    )

  if (!selected)
    return

  selected.frequencyHz =
    frequencyHz

  selected.powerDbm = 0

  draw()
}



function dbmToY(
  power: number,
  height: number,
) {

  return (
    height -
    (
      (
        power - DBM_BOTTOM
      )
      /
      (
        DBM_TOP - DBM_BOTTOM
      )
    )
    * height
  )
}

function yToDbm(
  y: number,
  height: number,
) {

  return (
    DBM_BOTTOM
    +
    (
      (height - y)
      / height
    )
    *
    (
      DBM_TOP - DBM_BOTTOM
    )
  )
}

function drawGrid(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
) {

  ctx.strokeStyle =
    "#2a2a2a"

  ctx.lineWidth = 1

  for (
    let i = 0;
    i <= 10;
    i++
  ) {

    const x =
      (i / 10) * width

    ctx.beginPath()

    ctx.moveTo(
      x,
      0,
    )

    ctx.lineTo(
      x,
      height,
    )

    ctx.stroke()
  }

  for (
    let i = 0;
    i <= 13;
    i++
  ) {

    const y =
      (i / 13) * height

    ctx.beginPath()

    ctx.moveTo(
      0,
      y,
    )

    ctx.lineTo(
      width,
      y,
    )

    ctx.stroke()
  }
}

function drawDbmScale(
  ctx: CanvasRenderingContext2D,
  height: number,
) {

  ctx.fillStyle =
    "#bbbbbb"

  ctx.font =
    "12px monospace"

  for (
    let i = 0;
    i <= 13;
    i++
  ) {

    const dbm =
      DBM_TOP - (i * 10)

    const y =
      (i / 13) * height

    ctx.fillText(
      `${dbm} dBm`,
      8,
      y + 12,
    )
  }
}

function drawFrequencyLabels(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
) {

  const snapshot =
    props.snapshot as any

  ctx.fillStyle =
    "#ffffff"

  ctx.font =
    "13px monospace"

  ctx.fillText(
    `START ${(snapshot.start_frequency_hz / 1e6).toFixed(3)} MHz`,
    10,
    height - 10,
  )

  ctx.fillText(
    `CENTER ${(snapshot.center_frequency_hz / 1e6).toFixed(3)} MHz`,
    width / 2 - 90,
    height - 10,
  )

  ctx.fillText(
    `STOP ${(snapshot.stop_frequency_hz / 1e6).toFixed(3)} MHz`,
    width - 200,
    height - 10,
  )
}

function drawTrace(
  ctx: CanvasRenderingContext2D,
  trace: number[],
  width: number,
  height: number,
) {

  if (!trace?.length)
    return

  ctx.beginPath()

  for (
    let i = 0;
    i < trace.length;
    i++
  ) {

    const x =
      (i / trace.length)
      * width

    const y =
      dbmToY(
        trace[i],
        height,
      )

    if (i === 0) {

      ctx.moveTo(
        x,
        y,
      )

    } else {

      ctx.lineTo(
        x,
        y,
      )
    }
  }

  ctx.stroke()
}

function drawLegend(
  ctx: CanvasRenderingContext2D,
  width: number,
) {

  ctx.font =
    "13px monospace"

  ctx.fillStyle =
    "#60a5fa"

  ctx.fillText(
    "LIVE",
    width - 140,
    20,
  )

  ctx.fillStyle =
    "#f59e0b"

  ctx.fillText(
    "MAX HOLD",
    width - 140,
    40,
  )

  ctx.fillStyle =
    "#06b6d4"

  ctx.fillText(
    "AVERAGE",
    width - 140,
    60,
  )
}

function drawCursor(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
) {

  if (
    cursorX.value === null
  ) {
    return
  }

  ctx.strokeStyle = "#666"

  ctx.beginPath()

  ctx.moveTo(
    cursorX.value,
    0,
  )

  ctx.lineTo(
    cursorX.value,
    height,
  )

  ctx.stroke()
}

function drawMarkers(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
) {

  const snapshot =
    props.snapshot as any

  const trace =
    snapshot.trace

  if (!trace)
    return

  markers.value.forEach(
    marker => {

      if (
        !marker.frequencyHz
      ) {
        return
      }

      const ratio =
        (
          marker.frequencyHz
          -
          snapshot.start_frequency_hz
        )
        /
        (
          snapshot.stop_frequency_hz
          -
          snapshot.start_frequency_hz
        )

      const binIndex =
        Math.min(
          trace.length - 1,
          Math.max(
            0,
            Math.round(
              ratio * trace.length
            )
          )
        )

      marker.powerDbm =
        trace[binIndex]

      const x =
        ratio * width

      ctx.strokeStyle =
        marker.id === "CENTRO"
          ? "#22c55e"
          : "#fbbf24"

      ctx.lineWidth = 1

      ctx.beginPath()

      ctx.moveTo(
        x,
        0,
      )

      ctx.lineTo(
        x,
        height,
      )

      ctx.stroke()

      ctx.fillStyle =
        marker.id === "CENTRO"
          ? "#22c55e"
          : "#fbbf24"

      ctx.font =
        "12px monospace"

      ctx.fillText(
        marker.id,
        x + 4,
        40,
      )
    }
  )
}
function drawSpectrum(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
) {

  const snapshot =
    props.snapshot as any

  const trace =
    snapshot.trace

  if (!trace)
    return

  let peakIndex = 0

  let peakValue =
    Number.NEGATIVE_INFINITY

  trace.forEach(
    (
      value: number,
      index: number,
    ) => {

      if (value > peakValue) {

        peakValue = value

        peakIndex = index
      }
    }
  )

  if (
    props.showAverage &&
    props.averageTrace
  ) {

    ctx.strokeStyle =
      "#06b6d4"

    ctx.lineWidth = 1

    drawTrace(
      ctx,
      props.averageTrace as number[],
      width,
      height,
    )
  }

  if (
    props.showMaxHold &&
    props.maxHold
  ) {

    ctx.strokeStyle =
      "#f59e0b"

    ctx.lineWidth = 1

    drawTrace(
      ctx,
      props.maxHold as number[],
      width,
      height,
    )
  }

  ctx.strokeStyle =
    "#60a5fa"

  ctx.lineWidth = 2

  drawTrace(
    ctx,
    trace,
    width,
    height,
  )

  const peakFrequencyHz =
    snapshot.start_frequency_hz
    +
    (
      peakIndex
      *
      snapshot.bin_size_hz
    )

  const peakX =
    (
      peakIndex / trace.length
    )
    * width

  const peakY =
    dbmToY(
      peakValue,
      height,
    )

  ctx.fillStyle =
    "#fbbf24"

  ctx.fillRect(
    peakX - 3,
    peakY - 22,
    6,
    22,
  )

  ctx.font =
    "13px monospace"

  ctx.fillText(
    `PEAK ${(peakFrequencyHz / 1e6).toFixed(3)} MHz | ${peakValue.toFixed(2)} dBm`,
    20,
    25,
  )
}

function draw() {

  const canvas =
    canvasRef.value

  if (!canvas) return

  if (!props.snapshot) return

  const ctx =
    canvas.getContext("2d")

  if (!ctx) return

  const width =
    canvas.width

  const height =
    canvas.height

  ctx.clearRect(
    0,
    0,
    width,
    height,
  )

  ctx.fillStyle =
    "#101010"

  ctx.fillRect(
    0,
    0,
    width,
    height,
  )

  drawGrid(
    ctx,
    width,
    height,
  )

  drawDbmScale(
    ctx,
    height,
  )

  drawFrequencyLabels(
    ctx,
    width,
    height,
  )

  drawLegend(
    ctx,
    width,
  )

  drawSpectrum(
    ctx,
    width,
    height,
  )

  drawMarkers(
    ctx,
    width,
    height,
  )

  drawCursor(
    ctx,
    width,
    height,
  )
}

watch(
  () => props.snapshot,
  draw,
  { deep: true },
)

watch(
  () => [
    props.showAverage,
    props.showMaxHold,
  ],
  draw,
)

onMounted(draw)

</script>