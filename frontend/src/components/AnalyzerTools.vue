<template>

  <div class="tools-container">

    <div class="row">

      <button
        v-for="marker in markers"
        :key="marker.id"
        class="tool-button"
        :class="{ active: marker.selected }"
        @click="selectMarker(markers.findIndex(m => m.id === marker.id))"
      >
        {{ marker.id }}
      </button>

    </div>

    <div class="row">

      <button
        class="tool-button"
        :class="{ active: showPeakMarker }"
        @click="togglePeak"
      >
        PEAK
      </button>

      <button
        class="tool-button"
        :class="{ active: showDelta }"
        @click="showDelta = !showDelta"
      >
        DELTA
      </button>

      <button
        class="action-button"
        @click="emit('markerToPeak')"
      >
        M->PEAK
      </button>

      <button
        class="action-button"
        @click="emit('nextPeak')"
      >
        NEXT
      </button>

      <button
        class="action-button"
        @click="emit('previousPeak')"
      >
        PREV
      </button>

    </div>

    <div class="row">

      <button
        class="tool-button"
        :class="{ active: showMaxHold }"
        @click="toggleMaxHold"
      >
        MAX
      </button>

      <input
        v-model.number="maxHoldSeconds"
        class="small-input"
        type="number"
      />

      <button
        class="tool-button"
        :class="{ active: showMinHold }"
        @click="toggleMinHold"
      >
        MIN
      </button>

      <input
        v-model.number="minHoldSeconds"
        class="small-input"
        type="number"
      />

      <button
        class="tool-button"
        :class="{ active: showAverage }"
        @click="toggleAverage"
      >
        AVG
      </button>

      <input
        v-model.number="averageSweeps"
        class="small-input"
        type="number"
      />

      <button
        class="action-button"
        @click="emit('clearAccumulators')"
      >
        CLEAR ACC
      </button>

    </div>

    <div class="row">

      <button
        class="action-button"
        @click="emit('centerMarker')"
      >
        CENTRAR M1
      </button>

      <button
        class="action-button"
        @click="emit('clear')"
      >
        LIMPIAR
      </button>

      <button
        class="action-button"
        @click="emit('resetView')"
      >
        RESET
      </button>

      <button
        class="action-button"
        @click="emit('peakSearch')"
      >
        PEAK SEARCH
      </button>

    </div>

  </div>

</template>

<script setup lang="ts">

import { ref } from "vue"

import { useMarkers } from "../composables/useMarkers"

const emit = defineEmits([
  "peakSearch",
  "centerMarker",
  "clear",
  "resetView",
  "togglePeakTracking",
  "markerToPeak",
  "nextPeak",
  "previousPeak",
  "toggleMaxHold",
  "toggleMinHold",
  "toggleAverage",
  "clearAccumulators",
])

const { markers, selectMarker } = useMarkers()

const showPeakMarker = ref(false)
const showDelta = ref(false)
const showMaxHold = ref(false)
const showMinHold = ref(false)
const showAverage = ref(false)

const maxHoldSeconds = ref(60)
const minHoldSeconds = ref(60)
const averageSweeps = ref(20)

function togglePeak() {
  showPeakMarker.value = !showPeakMarker.value
  emit("togglePeakTracking", showPeakMarker.value)

  if (showPeakMarker.value) {
    emit("peakSearch")
  }
}

function toggleMaxHold() {
  showMaxHold.value = !showMaxHold.value
  emit("toggleMaxHold", showMaxHold.value)
}

function toggleMinHold() {
  showMinHold.value = !showMinHold.value
  emit("toggleMinHold", showMinHold.value)
}

function toggleAverage() {
  showAverage.value = !showAverage.value
  emit("toggleAverage", showAverage.value)
}

</script>

<style scoped>

.tools-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  align-items: center;
}

.tool-button {
  min-width: 40px;
  height: 24px;
  padding: 0 6px;
  border-radius: 4px;
  border: 1px solid var(--border);
  background: var(--bg-panel-2);
  color: var(--text);
  font-size: 10px;
  font-weight: 600;
  cursor: pointer;
}

.tool-button.active {
  background: var(--sncte-blue);
  color: white;
}

.small-input {
  width: 48px;
  height: 28px;
  text-align: center;
  font-size: 12px;
}

.action-button {
  height: 30px;
  padding: 0 12px;
  background: var(--sncte-blue);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.action-button:hover {
  opacity: 0.9;
}

</style>