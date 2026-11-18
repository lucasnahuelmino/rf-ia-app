import { WS_BASE } from "../config"

export type ConnectionStatus =
  | "connecting"
  | "connected"
  | "disconnected"
  | "error"

export interface SpectrumSocketHandle {
  close: () => void
}

export function createSpectrumSocket(
  onMessage: (data: any) => void,
  onStatus?: (status: ConnectionStatus) => void,
): SpectrumSocketHandle {
  let socket: WebSocket | null = null
  let shouldReconnect = true
  let attempts = 0
  let reconnectTimer: number | null = null

  function scheduleReconnect() {
    if (!shouldReconnect) return

    const delay = Math.min(
      1000 * Math.pow(2, attempts),
      10000,
    )

    attempts += 1

    reconnectTimer = window.setTimeout(
      connect,
      delay,
    )
  }

  function connect() {
    onStatus?.("connecting")

    try {
      socket = new WebSocket(
        `${WS_BASE}/ws/spectrum`
      )
    } catch (error) {
      onStatus?.("error")
      scheduleReconnect()
      return
    }

    socket.onopen = () => {
      attempts = 0
      onStatus?.("connected")
    }

    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data)
        onMessage(payload)
      } catch (error) {
        console.error(
          "Invalid spectrum payload",
          error,
        )
      }
    }

    socket.onerror = () => {
      onStatus?.("error")
    }

    socket.onclose = () => {
      onStatus?.("disconnected")

      if (shouldReconnect) {
        scheduleReconnect()
      }
    }
  }

  connect()

  return {
    close() {
      shouldReconnect = false

      if (reconnectTimer !== null) {
        clearTimeout(reconnectTimer)
      }

      socket?.close()
    },
  }
}