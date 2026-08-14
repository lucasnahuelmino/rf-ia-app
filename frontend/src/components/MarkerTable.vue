<template>

  <div class="panel">

    <h3>
      Tabla de Markers
    </h3>

    <table>

      <thead>

        <tr>

          <th>
            Marker
          </th>

          <th>
            Frecuencia
          </th>

          <th>
            Nivel
          </th>

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
              ).toFixed(3)
              :
              "-"
            }}

          </td>

          <td>

            {{
              marker.powerDbm !== null
              ?
              marker.powerDbm.toFixed(2)
              :
              "-"
            }}

          </td>

        </tr>

      </tbody>

    </table>

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