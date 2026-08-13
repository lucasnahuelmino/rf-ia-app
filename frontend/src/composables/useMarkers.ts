import { ref } from "vue"

export const marker1 =
  ref<number | null>(null)

export const marker2 =
  ref<number | null>(null)

export function useMarkers() {

  function clearMarkers() {

    marker1.value = null
    marker2.value = null
  }

  return {
    marker1,
    marker2,
    clearMarkers,
  }
}