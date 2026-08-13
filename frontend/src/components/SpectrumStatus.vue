<template>

  <div class="status-panel">

    <div class="card">
      <span class="label">DEVICE</span>
      <span class="value">
        CONNECTED
      </span>
    </div>

    <div class="card">
      <span class="label">CENTER</span>
      <span class="value">
        {{ centerMHz }}
      </span>
    </div>

    <div class="card">
      <span class="label">SPAN</span>
      <span class="value">
        {{ spanMHz }}
      </span>
    </div>

    <div class="card">
      <span class="label">PEAK</span>
      <span class="value">
        {{ peakMHz }}
      </span>
    </div>

    <div class="card">
      <span class="label">LEVEL</span>
      <span class="value">
        {{ peakLevel }}
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

</script>

<style scoped>

.status-panel {

  display: flex;

  gap: 12px;

  margin-bottom: 15px;

  flex-wrap: wrap;
}

.card {

  min-width: 160px;

  padding: 10px;

  border: 1px solid #333;

  background: #181818;
}

.label {

  display: block;

  color: #888;

  font-size: 12px;
}

.value {

  display: block;

  color: #00ff55;

  font-size: 18px;

  font-weight: bold;
}

</style>