<template>

  <div class="marker-bar">

    <div
      v-for="(marker,index) in markers"
      :key="index"
      class="marker-card"
      :class="{
        active: marker.selected
      }"
    >

      <div class="marker-title">

        {{ marker.id }}

      </div>

      <div class="marker-frequency">

        {{
          marker.frequencyHz
          ? (marker.frequencyHz / 1e6).toFixed(3)
          : "---"
        }}

        MHz

      </div>

      <div class="marker-level">

        {{
          marker.powerDbm !== null
          ? marker.powerDbm.toFixed(2)
          : "---"
        }}

        dBm

      </div>

    </div>

  </div>

</template>

<script setup lang="ts">

import {
  useMarkers,
} from "../composables/useMarkers"

const {
  markers,
} = useMarkers()

</script>

<style scoped>

.marker-bar {

  display: flex;

  gap: 10px;

  margin-top: 10px;

  flex-wrap: wrap;
}

.marker-card {

  min-width: 120px;

  background: #f5f8ff;

  border: 1px solid var(--sncte-border);

  border-radius: 10px;

  padding: 8px;
}

.marker-card.active {

  background: var(--sncte-blue);

  color: white;
}

.marker-title {

  font-size: 11px;

  font-weight: 700;

  text-transform: uppercase;
}

.marker-frequency {

  margin-top: 4px;

  font-size: 13px;

  font-weight: 700;
}

.marker-level {

  margin-top: 2px;

  font-size: 12px;
}

</style>