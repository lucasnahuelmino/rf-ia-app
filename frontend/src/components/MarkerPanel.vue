<template>

  <div class="panel">

    <h3>
      Markers
    </h3>

    <div
      class="marker-row"
      v-for="(marker,index) in markers"
      :key="index"
    >

      <input
        type="checkbox"
        v-model="marker.enabled"
      />

      <span>

        M{{ index + 1 }}

      </span>

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
} = useMarkers()

</script>