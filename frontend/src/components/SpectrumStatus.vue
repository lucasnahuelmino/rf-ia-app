<template>

  <div class="status-bar">

    <div class="item">

      <span class="label">
        Equipo
      </span>

      <span class="value">
        BB60C
      </span>

    </div>

    <div class="item">

      <span class="label">
        Frecuencia Central
      </span>

      <span class="value">
        {{ centerMHz }}
      </span>

    </div>

    <div class="item">

      <span class="label">
        Nivel
      </span>

      <span class="value">
        {{ centerLevel }}
      </span>

    </div>

    <div class="item">

      <span class="label">
        Peak
      </span>

      <span class="value">
        {{ peakMHz }}
      </span>

    </div>

    <div class="item">

      <span class="label">
        Nivel Peak
      </span>

      <span class="value">
        {{ peakLevel }}
      </span>

    </div>

    <div class="item">

      <span class="label">
        Span
      </span>

      <span class="value">
        {{ spanMHz }}
      </span>

    </div>

    <div class="item">

      <span class="label">
        Fuente
      </span>

      <span class="value">
        {{ source }}
      </span>

    </div>

  </div>

</template>

<script setup lang="ts">

import { computed } from "vue"

const props = defineProps<{
  snapshot: any
}>()

const centerMHz = computed(() => {

  if (!props.snapshot)
    return "--"

  return (
    props.snapshot.center_frequency_hz
    / 1e6
  ).toFixed(3) + " MHz"
})

const spanMHz = computed(() => {

  if (!props.snapshot)
    return "--"

  return (
    props.snapshot.span_hz
    / 1e6
  ).toFixed(3) + " MHz"
})

const source = computed(() => {

  if (!props.snapshot)
    return "--"

  return props.snapshot.source ?? "HARDWARE"
})

const peakInfo = computed(() => {

  if (
    !props.snapshot ||
    !props.snapshot.trace
  ) {
    return null
  }

  const trace =
    props.snapshot.trace

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

  const frequencyHz =
    props.snapshot.start_frequency_hz
    +
    peakIndex
    *
    props.snapshot.bin_size_hz

  return {
    frequencyHz,
    level: peakValue,
  }
})

const peakMHz = computed(() => {

  if (!peakInfo.value)
    return "--"

  return (
    peakInfo.value.frequencyHz
    / 1e6
  ).toFixed(3) + " MHz"
})

const peakLevel = computed(() => {

  if (!peakInfo.value)
    return "--"

  return (
    peakInfo.value.level
  ).toFixed(2) + " dBm"
})

const centerLevel = computed(() => {

  if (
    !props.snapshot ||
    !props.snapshot.trace
  ) {
    return "--"
  }

  const trace =
    props.snapshot.trace

  const centerFreq =
    props.snapshot.center_frequency_hz

  const ratio =
    (
      centerFreq
      -
      props.snapshot.start_frequency_hz
    )
    /
    (
      props.snapshot.stop_frequency_hz
      -
      props.snapshot.start_frequency_hz
    )

  const bin =
    Math.min(
      trace.length - 1,
      Math.max(
        0,
        Math.round(
          ratio * trace.length
        )
      )
    )

  return (
    trace[bin]
  ).toFixed(2) + " dBm"
})

</script>

<style scoped>

.status-bar {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  background: white;
  border: 1px solid var(--sncte-border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 8px;
  margin-bottom: 10px;
}

.item {
  background: #f6f9ff;
  border: 1px solid var(--sncte-border);
  border-radius: 8px;
  padding: 6px 10px;
  min-width: 120px;
}

.label {
  font-size: 10px;
  text-transform: uppercase;
  color: #6a7b98;
  display: block;
}

.value {
  font-size: 13px;
  font-weight: 700;
  color: var(--sncte-blue-dark);
}

</style>