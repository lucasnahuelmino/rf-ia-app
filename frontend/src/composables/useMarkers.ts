import { ref } from "vue"

export interface Marker {

  enabled: boolean

  frequencyHz: number | null

  powerDbm: number | null
}

export const markers =
  ref<Marker[]>([
    {
      enabled: false,
      frequencyHz: null,
      powerDbm: null,
    },
    {
      enabled: false,
      frequencyHz: null,
      powerDbm: null,
    },
    {
      enabled: false,
      frequencyHz: null,
      powerDbm: null,
    },
    {
      enabled: false,
      frequencyHz: null,
      powerDbm: null,
    },
    {
      enabled: false,
      frequencyHz: null,
      powerDbm: null,
    },
  ])

export function useMarkers() {

  function clearMarkers() {

    markers.value.forEach(
      marker => {

        marker.enabled = false

        marker.frequencyHz = null

        marker.powerDbm = null
      }
    )
  }

  return {

    markers,

    clearMarkers,
  }
}