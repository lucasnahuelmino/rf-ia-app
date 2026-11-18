<template>

  <div class="panel">

    <h3>
      Mediciones
    </h3>

    <div class="grid">

      <div class="card">
        <span class="label">Peak freq</span>
        <span class="value">
          {{
            peak?.frequencyHz
              ? (peak.frequencyHz / 1e6).toFixed(4) + " MHz"
              : "--"
          }}
        </span>
      </div>

      <div class="card">
        <span class="label">Peak level</span>
        <span class="value">
          {{ peak?.level?.toFixed?.(2) ?? "--" }} dBm
        </span>
      </div>

      <div class="card">
        <span class="label">Noise floor</span>
        <span class="value">
          {{ noiseFloor?.toFixed?.(2) ?? "--" }} dBm
        </span>
      </div>

      <div class="card">
        <span class="label">SNR</span>
        <span class="value">
          {{ snr?.toFixed?.(2) ?? "--" }} dB
        </span>
      </div>

      <div class="card">
        <span class="label">Channel power</span>
        <span class="value">
          {{ channelPower?.toFixed?.(2) ?? "--" }} dBm
        </span>
      </div>

      <div class="card">
        <span class="label">Occupied BW</span>
        <span class="value">
          {{
            occupiedBandwidth
              ? (occupiedBandwidth.bandwidthHz / 1e6).toFixed(3) + " MHz"
              : "--"
          }}
        </span>
      </div>

    </div>

    <div class="peak-list">

      <h4>Peak list</h4>

      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Frecuencia</th>
            <th>Nivel</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(item, index) in peakList"
            :key="index"
          >
            <td>{{ index + 1 }}</td>
            <td>
              {{ (item.frequencyHz / 1e6).toFixed(4) }} MHz
            </td>
            <td>
              {{ item.level.toFixed(2) }} dBm
            </td>
          </tr>
        </tbody>
      </table>

    </div>

  </div>

</template>

<script setup lang="ts">

import { computed } from "vue"

const props = defineProps<{
  snapshot: any
}>()

import { useMeasurements } from "../composables/useMeasurements"

const measurements = useMeasurements(
  computed(() => props.snapshot)
)

const {
  peak,
  peakList,
  noiseFloor,
  channelPower,
  occupiedBandwidth,
  snr,
} = measurements

</script>

<style scoped>

.panel {
  background: white;
  border: 1px solid var(--sncte-border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 12px;
  margin-bottom: 12px;
}

.panel h3 {
  margin-top: 0;
  color: var(--sncte-blue-dark);
}

.grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(100px, 1fr));
  gap: 8px;
}

.card {
  padding: 8px;
  border-radius: 8px;
  background: #f6f9ff;
}

.label {
  display: block;
  color: #5a6a85;
  font-size: 11px;
  margin-bottom: 4px;
  text-transform: uppercase;
}

.value {
  color: var(--sncte-blue-dark);
  font-size: 14px;
  font-weight: 600;
}

.peak-list {
  margin-top: 12px;
}

.peak-list h4 {
  margin: 0 0 6px 0;
  color: var(--sncte-blue-dark);
  font-size: 12px;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

th, td {
  padding: 4px;
  border-bottom: 1px solid #eef2f7;
  text-align: left;
}

thead {
  background: #f4f7fc;
}

</style>