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

      <b>ΔF:</b>

      {{
        (
          Math.abs(
            markers[1].frequencyHz -
            markers[0].frequencyHz
          ) / 1000
        ).toFixed(3)
      }}

      kHz

      <br>

      <b>ΔP:</b>

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

</template>

<script setup lang="ts">

import {
  useMarkers,
} from "../composables/useMarkers"

const {
  markers,
} = useMarkers()

</script>