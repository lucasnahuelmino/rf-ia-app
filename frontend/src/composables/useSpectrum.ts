import { ref } from "vue"

import {
  createSpectrumSocket,
  type ConnectionStatus,
  type SpectrumSocketHandle,
} from "../services/spectrumService"

export function useSpectrum() {
  const spectrum = ref<any>(null)
  const connectionStatus =
    ref<ConnectionStatus>("disconnected")

  let socketHandle: SpectrumSocketHandle | null = null

  const connect = () => {
    if (socketHandle) return

    socketHandle = createSpectrumSocket(
      (payload) => {
        spectrum.value = payload
      },
      (status) => {
        connectionStatus.value = status
      },
    )
  }

  const disconnect = () => {
    socketHandle?.close()
    socketHandle = null
  }

  return {
    spectrum,
    connectionStatus,
    connect,
    disconnect,
  }
}