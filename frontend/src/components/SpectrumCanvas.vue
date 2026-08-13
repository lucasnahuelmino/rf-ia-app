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

const props = defineProps<{
  snapshot: any
}>()

const canvasRef =
  ref<HTMLCanvasElement | null>(null)

function drawGrid(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
) {

  ctx.strokeStyle = "#333"
  ctx.lineWidth = 1

  for (let i = 0; i <= 10; i++) {

    const y =
      (i / 10) * height

    ctx.beginPath()
    ctx.moveTo(0, y)
    ctx.lineTo(width, y)
    ctx.stroke()
  }

  for (let i = 0; i <= 10; i++) {

    const x =
      (i / 10) * width

    ctx.beginPath()
    ctx.moveTo(x, 0)
    ctx.lineTo(x, height)
    ctx.stroke()
  }
}

function drawLabels(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
) {

  const snapshot =
    props.snapshot

  ctx.fillStyle = "#ffffff"

  ctx.font = "14px Arial"

  const startMHz =
    snapshot.start_frequency_hz / 1e6

  const stopMHz =
    snapshot.stop_frequency_hz / 1e6

  const centerMHz =
    snapshot.center_frequency_hz / 1e6

  ctx.fillText(
    `START ${startMHz.toFixed(3)} MHz`,
    10,
    height - 10,
  )

  ctx.fillText(
    `CENTER ${centerMHz.toFixed(3)} MHz`,
    width / 2 - 70,
    height - 10,
  )

  ctx.fillText(
    `STOP ${stopMHz.toFixed(3)} MHz`,
    width - 170,
    height - 10,
  )

  for (let i = 0; i <= 12; i++) {

    const dbm =
      -10 * i

    const y =
      (i / 12) * height

    ctx.fillText(
      `${dbm} dBm`,
      5,
      y + 10,
    )
  }
}

function drawSpectrum(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
) {

  const trace =
    props.snapshot.trace

  if (!trace) return

  const len =
    trace.length

  let peakPower =
    Number.NEGATIVE_INFINITY

  let peakIndex = 0

  trace.forEach(
    (
      value: number,
      index: number,
    ) => {

      if (
        value > peakPower
      ) {
        peakPower = value
        peakIndex = index
      }
    }
  )

  ctx.strokeStyle =
    "#00ff55"

  ctx.lineWidth = 2

  ctx.beginPath()

  for (
    let i = 0;
    i < len;
    i++
  ) {

    const x =
      (i / len) * width

    const power =
      trace[i]

    const y =
      height -
      (
        (power + 130)
        / 130
      ) *
      height

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

  const peakX =
    (peakIndex / len)
    * width

  const peakY =
    height -
    (
      (peakPower + 130)
      / 130
    ) *
    height

  ctx.fillStyle =
    "#ffcc00"

  ctx.beginPath()

  ctx.arc(
    peakX,
    peakY,
    5,
    0,
    Math.PI * 2,
  )

  ctx.fill()

  const peakFrequencyHz =
    props.snapshot.start_frequency_hz
    +
    peakIndex
    *
    props.snapshot.bin_size_hz

  ctx.fillStyle =
    "#ffcc00"

  ctx.fillText(
    `Peak: ${(peakFrequencyHz / 1e6).toFixed(3)} MHz | ${peakPower.toFixed(2)} dBm`,
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

  drawLabels(
    ctx,
    width,
    height,
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

onMounted(draw)

</script>