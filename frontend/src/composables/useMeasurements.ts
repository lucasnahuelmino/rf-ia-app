import { computed } from "vue"

export function useMeasurements(snapshotRef: any) {
  const peak = computed(() => {
    const snapshot = snapshotRef.value
    if (!snapshot?.trace?.length) return null

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
      snapshot.start_frequency_hz +
      peakIndex * snapshot.bin_size_hz

    return {
      index: peakIndex,
      frequencyHz,
      level: peakValue,
    }
  })

  const peakList = computed(() => {
    const snapshot = snapshotRef.value
    if (!snapshot?.trace?.length) return []

    const trace = snapshot.trace as number[]
    const results: { index: number; frequencyHz: number; level: number }[] = []

    for (let i = 1; i < trace.length - 1; i++) {
      if (
        trace[i] > trace[i - 1] &&
        trace[i] > trace[i + 1]
      ) {
        results.push({
          index: i,
          frequencyHz:
            snapshot.start_frequency_hz +
            i * snapshot.bin_size_hz,
          level: trace[i],
        })
      }
    }

    return results
      .sort((a, b) => b.level - a.level)
      .slice(0, 8)
  })

  const noiseFloor = computed(() => {
    const snapshot = snapshotRef.value
    if (!snapshot?.trace?.length) return null

    const trace = [...(snapshot.trace as number[])].sort(
      (a, b) => a - b
    )

    const index = Math.floor(trace.length * 0.1)

    return trace[Math.max(0, index)]
  })

  const channelPower = computed(() => {
    const snapshot = snapshotRef.value
    if (!snapshot?.trace?.length) return null

    const trace = snapshot.trace as number[]
    const binWidth = snapshot.bin_size_hz as number

    let linearSum = 0

    for (const value of trace) {
      linearSum += Math.pow(10, value / 10)
    }

    const powerDbm =
      10 * Math.log10(linearSum * binWidth / 1e3) // approximate scaling

    return powerDbm
  })

  const occupiedBandwidth = computed(() => {
    const snapshot = snapshotRef.value
    if (!snapshot?.trace?.length) return null

    const trace = snapshot.trace as number[]
    const binWidth = snapshot.bin_size_hz as number

    const linear = trace.map((value) =>
      Math.pow(10, value / 10)
    )

    const total = linear.reduce((a, b) => a + b, 0)

    const target = total * 0.99

    let cumulative = 0
    let startIndex = 0
    let stopIndex = trace.length - 1

    // lower
    for (let i = 0; i < trace.length; i++) {
      cumulative += linear[i]
      if (cumulative >= (total - target) / 2) {
        startIndex = i
        break
      }
    }

    cumulative = 0
    for (let i = trace.length - 1; i >= 0; i--) {
      cumulative += linear[i]
      if (cumulative >= (total - target) / 2) {
        stopIndex = i
        break
      }
    }

    const startFreq =
      snapshot.start_frequency_hz + startIndex * binWidth
    const stopFreq =
      snapshot.start_frequency_hz + stopIndex * binWidth

    return {
      startFrequencyHz: startFreq,
      stopFrequencyHz: stopFreq,
      bandwidthHz: stopFreq - startFreq,
    }
  })

  const snr = computed(() => {
    const peakValue = peak.value?.level
    const noise = noiseFloor.value

    if (peakValue === undefined || noise === null) return null

    return peakValue - noise
  })

  return {
    peak,
    peakList,
    noiseFloor,
    channelPower,
    occupiedBandwidth,
    snr,
  }
}