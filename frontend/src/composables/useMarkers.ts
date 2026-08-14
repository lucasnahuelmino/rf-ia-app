import { ref } from "vue"

export interface Marker {

  enabled: boolean

  selected: boolean

  frequencyHz: number | null

  powerDbm: number | null
}

export const markers =
  ref<Marker[]>([
    {
      enabled: true,
      selected: true,
      frequencyHz: null,
      powerDbm: null,
    },
    {
      enabled: false,
      selected: false,
      frequencyHz: null,
      powerDbm: null,
    },
    {
      enabled: false,
      selected: false,
      frequencyHz: null,
      powerDbm: null,
    },
    {
      enabled: false,
      selected: false,
      frequencyHz: null,
      powerDbm: null,
    },
    {
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