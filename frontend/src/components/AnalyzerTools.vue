<template>

  <div class="tools-container">

    <div class="row">

      <button
        v-for="marker in markers"
        :key="marker.id"
        class="tool-button"
        :class="{
          active: marker.selected
        }"
        @click="
          selectMarker(
            markers.findIndex(
              m => m.id === marker.id
            )
          )
        "
      >
        {{ marker.id }}
      </button>

    </div>

    <div class="row">

      <button
        class="tool-button"
        :class="{
          active: showPeakMarker
        }"
        @click="togglePeak"
      >
        PEAK
      </button>

      <button
        class="tool-button"
        :class="{
          active: showDelta
        }"
        @click="
          showDelta =
          !showDelta
        "
      >
        DELTA
      </button>

    </div>

    <div class="row">

      <button
        class="tool-button"
        :class="{
          active: showMaxHold
        }"
        @click="
          showMaxHold =
          !showMaxHold
        "
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
        :class="{
          active: showMinHold
        }"
        @click="
          showMinHold =
          !showMinHold
        "
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
        :class="{
          active: showAverage
        }"
        @click="
          showAverage =
          !showAverage
        "
      >
        AVG
      </button>

      <input
        v-model.number="averageSweeps"
        class="small-input"
        type="number"
      />

    </div>

    <div class="row">

      <button
        class="action-button"
        @click="
          emit(
            'centerMarker'
          )
        "
      >
        CENTRAR M1
      </button>

      <button
        class="action-button"
        @click="
          emit(
            'clear'
          )
        "
      >
        LIMPIAR
      </button>

      <button
        class="action-button"
        @click="
          emit(
            'resetView'
          )
        "
      >
        RESET
      </button>

    </div>

  </div>

</template>

<script setup lang="ts">

import {
  ref,
} from "vue"

import {
  useMarkers,
} from "../composables/useMarkers"

const emit =
  defineEmits([
    "peakSearch",
    "centerMarker",
    "clear",
    "resetView",
    "togglePeakTracking",
  ])

const {
  markers,
  selectMarker,
} = useMarkers()

const showPeakMarker =
  ref(false)

const showDelta =
  ref(false)

const showMaxHold =
  ref(false)

const showMinHold =
  ref(false)

const showAverage =
  ref(false)

const maxHoldSeconds =
  ref(60)

const minHoldSeconds =
  ref(60)

const averageSweeps =
  ref(20)

function togglePeak() {

  showPeakMarker.value =
    !showPeakMarker.value

  emit(
    "togglePeakTracking",
    showPeakMarker.value
  )

  if (
    showPeakMarker.value
  ) {

    emit(
      "peakSearch"
    )
  }
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

  min-width: 48px;

  height: 28px;

  padding: 0 10px;

  border-radius: 6px;

  border: 1px solid var(--sncte-border);

  background: white;

  color: var(--sncte-blue-dark);

  font-size: 12px;

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
