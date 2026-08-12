<template>
  <canvas
    ref="canvasRef"
    width="1200"
    height="600"
  />
</template>

<script setup lang="ts">

import {
  onMounted,
  ref,
  watch,
} from "vue"

const props = defineProps<{
  trace: number[]
}>()

const canvasRef =
  ref<HTMLCanvasElement | null>(null)

function draw() {

  const canvas = canvasRef.value

  if (!canvas) return

  const ctx =
    canvas.getContext("2d")

  if (!ctx) return

  ctx.clearRect(
    0,
    0,
    canvas.width,
    canvas.height
  )

  ctx.fillStyle = "#111"

  ctx.fillRect(
    0,
    0,
    canvas.width,
    canvas.height
  )

  ctx.strokeStyle = "#00ff66"

  ctx.beginPath()

  const len =
    props.trace.length

  for (let i = 0; i < len; i++) {

    const x =
      (i / len) *
      canvas.width

    const power =
      props.trace[i]

    const y =
      canvas.height -
      ((power + 130) / 130)
      * canvas.height

    if (i === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  }

  ctx.stroke()
}

watch(
  () => props.trace,
  draw,
)

onMounted(draw)

</script>