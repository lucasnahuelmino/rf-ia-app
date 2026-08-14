import { ref } from "vue"

export interface Marker {

  id: string

  enabled: boolean

  selected: boolean

  frequencyHz: number | null

  powerDbm: number | null
}

export const markers =
  ref<Marker[]>([
    {
      id: "CENTRO",
      enabled: true,
      selected: true,
      frequencyHz: null,
      powerDbm: null,
    },

    {
      id: "M1",
      enabled: false,
      selected: false,
      frequencyHz: null,
      powerDbm: null,
    },

    {
      id: "M2",
      enabled: false,
      selected: false,
      frequencyHz: null,
      powerDbm: null,
    },

    {
      id: "M3",
      enabled: false,
      selected: false,
      frequencyHz: null,
      powerDbm: null,
    },

    {
      id: "M4",
      enabled: false,
      selected: false,
      frequencyHz: null,
      powerDbm: null,
    },

    {
      id: "M5",
      enabled: false,
      selected: false,
      frequencyHz: null,
      powerDbm: null,
    },
  ])

export function useMarkers() {

  function clearMarkers() {

    markers.value.forEach(
      marker => {

        marker.enabled = false
        marker.selected = false
        marker.frequencyHz = null
        marker.powerDbm = null
      }
    )

    markers.value[0].enabled = true
    markers.value[0].selected = true

  }

  function selectMarker(
    index: number,
  ) {

    markers.value.forEach(
      marker => {

        marker.selected = false
      }
    )

    markers.value[index].selected = true

    markers.value[index].enabled = true
  }

  return {

    markers,

    clearMarkers,

    selectMarker,
  }
}