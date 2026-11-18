import { ref } from "vue"

export interface Marker {
  id: string
  enabled: boolean
  selected: boolean
  frequencyHz: number | null
  powerDbm: number | null
}

export const markers = ref<Marker[]>([
  { id: "CENTRO", enabled: true, selected: true, frequencyHz: null, powerDbm: null },
  { id: "M1", enabled: false, selected: false, frequencyHz: null, powerDbm: null },
  { id: "M2", enabled: false, selected: false, frequencyHz: null, powerDbm: null },
  { id: "M3", enabled: false, selected: false, frequencyHz: null, powerDbm: null },
  { id: "M4", enabled: false, selected: false, frequencyHz: null, powerDbm: null },
  { id: "M5", enabled: false, selected: false, frequencyHz: null, powerDbm: null },
])

export function useMarkers() {
  function clearMarkers() {
    markers.value.forEach((marker) => {
      marker.enabled = false
      marker.selected = false
      marker.frequencyHz = null
      marker.powerDbm = null
    })

    markers.value[0].enabled = true
    markers.value[0].selected = true
  }

  function selectMarker(index: number) {
    markers.value.forEach((marker) => {
      marker.selected = false
    })

    if (markers.value[index]) {
      markers.value[index].selected = true
      markers.value[index].enabled = true
    }
  }

  function toggleMarker(id: string, enabled: boolean) {
    const marker = markers.value.find((m) => m.id === id)
    if (!marker) return
    marker.enabled = enabled
    if (!enabled) {
      marker.frequencyHz = null
      marker.powerDbm = null
    }
  }

  function setMarkerPosition(
    id: string,
    frequencyHz: number,
    powerDbm: number | null = null,
  ) {
    const marker = markers.value.find((m) => m.id === id)
    if (!marker) return

    marker.enabled = true
    marker.frequencyHz = frequencyHz
    marker.powerDbm = powerDbm
  }

  function moveMarkerToPeak(
    id: string,
    snapshot: any,
  ) {
    if (!snapshot?.trace?.length) return

    const trace = snapshot.trace as number[]
    let peakIndex = 0
    let peakValue = Number.NEGATIVE_INFINITY

    trace.forEach((value, index) => {
      if (value > peakValue) {
        peakValue = value
        peakIndex = index
      }
    })

    const frequencyHz =
      snapshot.start_frequency_hz + peakIndex * snapshot.bin_size_hz

    setMarkerPosition(id, frequencyHz, peakValue)
  }

  function peakSearch(snapshot: any, markerId = "M1") {
    moveMarkerToPeak(markerId, snapshot)
  }

  function findNearestPeakIndex(
    trace: number[],
    fromIndex: number,
    direction: 1 | -1,
  ) {
    let index = fromIndex

    while (index > 0 && index < trace.length - 1) {
      index += direction

      if (
        trace[index] > trace[index - 1] &&
        trace[index] > trace[index + 1]
      ) {
        return index
      }
    }

    return -1
  }

  function nextPeak(snapshot: any, markerId = "M1") {
    if (!snapshot?.trace?.length) return

    const marker = markers.value.find((m) => m.id === markerId)
    if (!marker?.frequencyHz) return

    const trace = snapshot.trace as number[]
    const ratio =
      (marker.frequencyHz - snapshot.start_frequency_hz) /
      (snapshot.stop_frequency_hz - snapshot.start_frequency_hz)

    const fromIndex = Math.round(ratio * (trace.length - 1))

    const nextIndex = findNearestPeakIndex(trace, fromIndex, 1)

    if (nextIndex < 0) return

    setMarkerPosition(
      markerId,
      snapshot.start_frequency_hz + nextIndex * snapshot.bin_size_hz,
      trace[nextIndex],
    )
  }

  function previousPeak(snapshot: any, markerId = "M1") {
    if (!snapshot?.trace?.length) return

    const marker = markers.value.find((m) => m.id === markerId)
    if (!marker?.frequencyHz) return

    const trace = snapshot.trace as number[]
    const ratio =
      (marker.frequencyHz - snapshot.start_frequency_hz) /
      (snapshot.stop_frequency_hz - snapshot.start_frequency_hz)

    const fromIndex = Math.round(ratio * (trace.length - 1))

    const prevIndex = findNearestPeakIndex(trace, fromIndex, -1)

    if (prevIndex < 0) return

    setMarkerPosition(
      markerId,
      snapshot.start_frequency_hz + prevIndex * snapshot.bin_size_hz,
      trace[prevIndex],
    )
  }

  function centerOnMarker(
    markerId: string,
    snapshot: any,
  ) {
    const marker = markers.value.find((m) => m.id === markerId)
    if (!marker?.frequencyHz) return null

    return {
      center_frequency_hz: marker.frequencyHz,
      span_hz: snapshot.span_hz,
      rbw_hz: snapshot.rbw_hz,
      vbw_hz: snapshot.vbw_hz,
      reference_level_dbm: snapshot.reference_level_dbm,
    }
  }

  return {
    markers,
    clearMarkers,
    selectMarker,
    toggleMarker,
    setMarkerPosition,
    moveMarkerToPeak,
    peakSearch,
    nextPeak,
    previousPeak,
    centerOnMarker,
  }
}