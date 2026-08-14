<template>

  <details class="panel" open>

    <summary>
      Herramientas del Analizador
    </summary>

    <div class="tools-container">

      <div class="marker-group">

        <button
          v-for="(marker,index) in markers"
          :key="index"
          class="tool-button"
          :class="{
            active: marker.selected
          }"
          @click="selectMarker(index)"
        >

          M{{ index + 1 }}

        </button>

      </div>

      <label class="tool-check">
        <input
          type="checkbox"
          v-model="showPeakMarker"
        />
        Peak
      </label>

      <label class="tool-check">
        <input
          type="checkbox"
          v-model="showDelta"
        />
        Delta
      </label>

      <label class="tool-check">
        <input
          type="checkbox"
          v-model="showMaxHold"
        />
        Max Hold
      </label>

      <input
        v-model.number="maxHoldSeconds"
        class="small-input"
        type="number"
      />

      <span>s</span>

      <label class="tool-check">
        <input
          type="checkbox"
          v-model="showMinHold"
        />
        Min Hold
      </label>

      <input
        v-model.number="minHoldSeconds"
        class="small-input"
        type="number"
      />

      <span>s</span>

      <label class="tool-check">
        <input
          type="checkbox"
          v-model="showAverage"
        />
        Average
      </label>

      <input
        v-model.number="averageSweeps"
        class="small-input"
        type="number"
      />

      <span>sweeps</span>

      <button
        class="action-button"
        @click="$emit('peakSearch')"
      >
        Buscar Pico
      </button>

      <button
        class="action-button"
        @click="$emit('centerMarker')"
      >
        Centrar M1
      </button>

      <button
        class="action-button"
        @click="$emit('clear')"
      >
        Limpiar
      </button>

    </div>

  </details>

</template>

<script setup lang="ts">

import {
  ref,
} from "vue"

import {
  useMarkers,
} from "../composables/useMarkers"

defineEmits([
  "peakSearch",
  "centerMarker",
  "clear",
])

const {
  markers,
  selectMarker,
} = useMarkers()

const showPeakMarker = ref(true)

const showDelta = ref(false)

const showMaxHold = ref(false)

const showMinHold = ref(false)

const showAverage = ref(false)

const maxHoldSeconds = ref(60)

const minHoldSeconds = ref(60)

const averageSweeps = ref(20)

</script>

<style scoped>

.panel {

  background: white;

  border: 1px solid var(--sncte-border);

  border-radius: var(--radius);

  box-shadow: var(--shadow);

  padding: 12px;

  margin-bottom: 15px;
}

summary {

  cursor: pointer;

  font-weight: 600;

  color: var(--sncte-blue-dark);
}

.tools-container {

  display: flex;

  flex-wrap: wrap;

  align-items: center;

  gap: 8px;

  margin-top: 12px;
}

.marker-group {

  display: flex;

  gap: 4px;
}

.tool-button {

  min-width: 48px;

  border-radius: 6px;

  border: 1px solid var(--sncte-border);

  background: white;
}

.tool-button.active {

  background: var(--sncte-blue);

  color: white;
}

.tool-check {

  display: flex;

  align-items: center;

  gap: 4px;

  white-space: nowrap;
}

.small-input {

  width: 60px;

  text-align: center;
}

.action-button {

  background: var(--sncte-blue);

  color: white;

  border: none;

  border-radius: 8px;

  padding: 8px 12px;
}

.action-button:hover {

  background: var(--sncte-blue-light);
}

</style>