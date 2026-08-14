<template>

  <div class="panel">

    <h3>
      Markers
    </h3>

    <div class="marker-container">

      <button
        v-for="(marker,index) in markers"
        :key="index"
        class="marker-btn"
        :class="{
          active: marker.selected
        }"
        @click="selectMarker(index)"
      >

        M{{ index + 1 }}

      </button>

    </div>

    <div class="buttons">

      <button
        @click="$emit('peakSearch')"
      >
        Buscar Pico
      </button>

      <button
        @click="clearMarkers"
      >
        Limpiar
      </button>

    </div>

  </div>

</template>

<script setup lang="ts">

import {
  useMarkers,
} from "../composables/useMarkers"

defineEmits([
  "peakSearch",
])

const {
  markers,
  clearMarkers,
  selectMarker,
} = useMarkers()

</script>

<style scoped>

.marker-container {

  display: flex;

  gap: 10px;

  flex-wrap: wrap;

  margin-bottom: 15px;
}

.marker-btn {

  min-width: 60px;

  background: white;

  border: 1px solid var(--sncte-border);
}

.active {

  background: var(--sncte-blue);

  color: white;
}

.buttons {

  display: flex;

  gap: 10px;
}

</style>