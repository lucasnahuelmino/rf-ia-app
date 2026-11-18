import { ref, watch } from "vue"

interface TraceAccumulator {
  sum: number[]
  count: number
}

export function useTraceAnalysis(snapshotRef: any) {
  const maxHold = ref<number[] | null>(null)
  const minHold = ref<number[] | null>(null)
  const average = ref<number[] | null>(null)

  const accumulator =
    ref<TraceAccumulator | null>(null)

  let lastKey: string | null = null

  function reset() {
    maxHold.value = null
    minHold.value = null
    average.value = null
    accumulator.value = null
  }

  watch(
    snapshotRef,
    (snapshot: any) => {
      if (!snapshot?.trace?.length) return

      const key = `${snapshot.start_frequency_hz}_${snapshot.stop_frequency_hz}_${snapshot.trace.length}`

      if (key !== lastKey) {
        reset()
        lastKey = key
      }

      const trace = snapshot.trace as number[]

      if (!maxHold.value) {
        maxHold.value = [...trace]
      } else {
        maxHold.value = maxHold.value.map(
          (value, index) =>
            Math.max(value, trace[index])
        )
      }

      if (!minHold.value) {
        minHold.value = [...trace]
      } else {
        minHold.value = minHold.value.map(
          (value, index) =>
            Math.min(value, trace[index])
        )
      }

      if (!accumulator.value) {
        accumulator.value = {
          sum: [...trace],
          count: 1,
        }
      } else {
        accumulator.value = {
          sum: accumulator.value.sum.map(
            (value, index) =>
              value + trace[index]
          ),
          count: accumulator.value.count + 1,
        }
      }

      const acc = accumulator.value
      if (!acc) return

      average.value = acc.sum.map(
        (value) => value / acc.count
      )
    },
    { deep: true },
  )

  return {
    maxHold,
    minHold,
    average,
    reset,
  }
}