import { watch } from "vue"

import {
  markers,
} from "./useMarkers"

export function usePeakTracking(
  snapshot: any,
  enabled: any,
) {

  watch(
    snapshot,
    value => {

      if (
        !enabled.value ||
        !value?.trace
      ) {
        return
      }

      const trace =
        value.trace

      let peakIndex = 0

      let peakValue =
        Number.NEGATIVE_INFINITY

      trace.forEach(
        (
          level: number,
          index: number,
        ) => {

          if (
            level >
            peakValue
          ) {

            peakValue =
              level

            peakIndex =
              index
          }
        }
      )

      const frequencyHz =
        value.start_frequency_hz
        +
        (
          peakIndex
          *
          value.bin_size_hz
        )

      const marker =
        markers.value.find(
          marker =>
            marker.id === "M1"
        )

      if (!marker)
        return

      marker.enabled = true

      marker.frequencyHz =
        frequencyHz

      marker.powerDbm =
        peakValue
    },
    {
      deep: true,
    },
  )
}