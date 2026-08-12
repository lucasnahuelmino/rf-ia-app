import { ref } from "vue"

import {
  createSpectrumSocket
} from "../services/spectrumService"

export function useSpectrum() {

  const spectrum = ref<any>(null)

  const connect = () => {

    createSpectrumSocket(
      (payload) => {

        spectrum.value = payload
      }
    )
  }

  return {
    spectrum,
    connect,
  }
}