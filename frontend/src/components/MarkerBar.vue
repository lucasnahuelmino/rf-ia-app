<template>

  <div class="marker-bar">

    <div
      v-for="(marker, index) in markers"
      :key="index"
      class="marker-chip"
      :class="{ active: marker.selected }"
    >

      <span class="marker-id">
        {{ marker.id }}
      </span>

      <span class="marker-freq">
        {{
          marker.frequencyHz
            ? (marker.frequencyHz / 1e6).toFixed(3)
            : "---"
        }}
      </span>

      <span class="marker-level">
        {{
          marker.powerDbm !== null
            ? marker.powerDbm.toFixed(1)
            : "---"
        }}
      </span>

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
  gap: 4px;
  padding: 2px 4px;
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  height: 32px;
  align-items: center;
  overflow-x: auto;
}

.marker-chip {
  display: flex;
  gap: 4px;
  align-items: center;
  padding: 2px 6px;
  border-radius: 4px;
  background: var(--bg-panel-2);
  border: 1px solid var(--border);
  font-size: 10px;
  white-space: nowrap;
}

.marker-chip.active {
  border-color: var(--accent);
  background: rgba(34, 211, 238, 0.1);
}

.marker-id {
  color: var(--accent);
  font-weight: 700;
}

.marker-freq {
  color: var(--text);
  font-family: var(--font-mono);
}

.marker-level {
  color: var(--text-muted);
  font-family: var(--font-mono);
}

</style>