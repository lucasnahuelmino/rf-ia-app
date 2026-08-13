<template>

  <canvas
    ref="canvasRef"
    width="1400"
    height="700"
  />

</template>

<script setup lang="ts">

import {
  onMounted,
  ref,
  watch,
} from "vue"

const props = defineProps({

  snapshot: Object,

  showMaxHold: Boolean,

  showAverage: Boolean,

  maxHold: Array,

  averageTrace: Array,
})

const canvasRef =
  ref<HTMLCanvasElement | null>(null)

const DBM_TOP = 0
const DBM_BOTTOM = -130

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
    *
    height
  )
}

function drawGrid(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
) {

  ctx.strokeStyle = "#2a2a2a"

  ctx.lineWidth = 1

  for (let i = 0; i <= 10; i++) {

    const x =
      (i / 10) * width

    ctx.beginPath()

    ctx.moveTo(x, 0)

    ctx.lineTo(x, height)

    ctx.stroke()
  }

  for (let i = 0; i <= 13; i++) {

    const y =
      (i / 13) * height

    ctx.beginPath()

    ctx.moveTo(0, y)

    ctx.lineTo(width, y)

    ctx.stroke()
  }
}

function drawDbmScale(
  ctx: CanvasRenderingContext2D,
  height: number,
) {

  ctx.fillStyle = "#bbbbbb"

  ctx.font = "12px monospace"

  for (let i = 0; i <= 13; i++) {

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

  const startMHz =
    snapshot.start_frequency_hz / 1e6

  const stopMHz =
    snapshot.stop_frequency_hz / 1e6

  const centerMHz =
    snapshot.center_frequency_hz / 1e6

  ctx.fillStyle = "#ffffff"

  ctx.font = "13px monospace"

  ctx.fillText(
    `START ${startMHz.toFixed(3)} MHz`,
    10,
    height - 10,
  )

  ctx.fillText(
    `CENTER ${centerMHz.toFixed(3)} MHz`,
    width / 2 - 80,
    height - 10,
  )

  ctx.fillText(
    `STOP ${stopMHz.toFixed(3)} MHz`,
    width - 190,
    height - 10,
  )
}

function drawTrace(
  ctx: CanvasRenderingContext2D,
  trace: number[],
  width: number,
  height: number,
) {

  const len =
    trace.length

  if (!len)
    return

  ctx.beginPath()

  for (
    let i = 0;
    i < len;
    i++
  ) {

    const x =
      (i / len)
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

  ctx.font = "13px monospace"

  ctx.fillStyle = "#00ff55"

  ctx.fillText(
    "LIVE",
    width - 130,
    20,
  )

  ctx.fillStyle = "#ff8800"

  ctx.fillText(
    "MAX HOLD",
    width - 130,
    40,
  )

  ctx.fillStyle = "#00aaff"

  ctx.fillText(
    "AVERAGE",
    width - 130,
    60,
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

      if (
        value > peakValue
      ) {

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
      "#00aaff"

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
      "#ff8800"

    ctx.lineWidth = 1

    drawTrace(
      ctx,
      props.maxHold as number[],
      width,
      height,
    )
  }

  ctx.strokeStyle =
    "#00ff55"

  ctx.lineWidth = 2

  drawTrace(
    ctx,
    trace,
    width,
    height,
  )

  const peakX =
    (peakIndex / trace.length)
    * width

  const peakY =
    dbmToY(
      peakValue,
      height,
    )

  ctx.fillStyle =
    "#ffcc00"

  ctx.fillRect(
    peakX - 3,
    peakY - 18,
    6,
    18,
  )

  ctx.beginPath()

  ctx.moveTo(
    peakX,
    peakY - 22,
  )

  ctx.lineTo(
    peakX - 8,
    peakY - 35,
  )

  ctx.lineTo(
    peakX + 8,
    peakY - 35,
  )

  ctx.closePath()

  ctx.fill()

  const peakFrequencyHz =
    snapshot.start_frequency_hz
    +
    (
      peakIndex
      *
      snapshot.bin_size_hz
    )

  ctx.fillStyle =
    "#ffcc00"

  ctx.font =
    "14px monospace"

  ctx.fillText(
    `PEAK ${(peakFrequencyHz / 1e6).toFixed(3)} MHz | ${peakValue.toFixed(2)} dBm`,
    20,
    25,
  )
}

function draw() {

  const canvas =
    canvasRef.value

  if (!canvas)
    return

  if (!props.snapshot)
    return

  const ctx =
    canvas.getContext("2d")

  if (!ctx)
    return

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
}

watch(
  () => props.snapshot,
  draw,
  {
    deep: true,
  },
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