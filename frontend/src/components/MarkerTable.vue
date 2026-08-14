<template>

  <div class="panel">

    <table>

      <thead>

        <tr>

          <th>Marker</th>
          <th>Frecuencia</th>
          <th>Nivel</th>

        </tr>

      </thead>

      <tbody>

        <tr
          v-for="(marker,index) in markers"
          :key="index"
        >

          <td>

            M{{ index + 1 }}

          </td>

          <td>

            {{
              marker.frequencyHz
              ?
              (
                marker.frequencyHz / 1e6
              ).toFixed(3) + " MHz"
              :
              "-"
            }}

          </td>

          <td>

            {{
              marker.powerDbm !== null
              ?
              marker.powerDbm.toFixed(2) + " dBm"
              :
              "-"
            }}

          </td>

        </tr>

      </tbody>

    </table>

    <div
      v-if="
        markers[0].frequencyHz &&
        markers[1].frequencyHz
      "
      class="delta"
    >

      <div>

        <strong>Δ Frecuencia:</strong>

        {{
          (
            Math.abs(
              markers[1].frequencyHz -
              markers[0].frequencyHz
            ) / 1000
          ).toFixed(3)
        }}

        kHz

      </div>

      <div>

        <strong>Δ Nivel:</strong>

        {{
          Math.abs(
            (
              markers[1].powerDbm ?? 0
            )
            -
            (
              markers[0].powerDbm ?? 0
            )
          ).toFixed(2)
        }}

        dB

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

.panel {

  background: white;

  border: 1px solid var(--sncte-border);

  border-radius: var(--radius);

  box-shadow: var(--shadow);

  padding: 12px;
}

table {

  width: 100%;

  border-collapse: collapse;

  font-size: 12px;
}

thead {

  background: #f4f7fc;
}

th {

  text-align: left;

  padding: 8px;

  color: var(--sncte-blue-dark);

  border-bottom: 1px solid var(--sncte-border);
}

td {

  padding: 8px;

  border-bottom: 1px solid #eef2f7;
}

tr:last-child td {

  border-bottom: none;
}

.delta {

  margin-top: 12px;

  padding: 10px;

  background: #f8fbff;

  border: 1px solid var(--sncte-border);

  border-radius: 8px;

  font-size: 13px;

  color: var(--sncte-blue-dark);
}

</style>