import { ref } from "vue"

const maxHoldTrace = ref<number[]>([])
const averageTrace = ref<number[]>([])

let averageCount = 0

export function useSpectrumTools() {

  function update(trace: number[]) {

    if (!trace?.length)
      return

    if (maxHoldTrace.value.length === 0) {

      maxHoldTrace.value = [...trace]

    } else {

      maxHoldTrace.value =
        maxHoldTrace.value.map(
          (value, index) =>
            Math.max(
              value,
              trace[index],
            ),
        )
    }

    if (averageTrace.value.length === 0) {

      averageTrace.value = [...trace]

      averageCount = 1

    } else {

      averageCount++

      averageTrace.value =
        averageTrace.value.map(
          (value, index) =>
            (
              value *
              (averageCount - 1)
              +
              trace[index]
            )
            /
            averageCount
        )
    }
  }

  function clear() {

    maxHoldTrace.value = []

    averageTrace.value = []

    averageCount = 0
  }

  return {
    maxHoldTrace,
    averageTrace,
    update,
    clear,
  }
}