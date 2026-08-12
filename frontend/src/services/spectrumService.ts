export function createSpectrumSocket(
  onMessage: (data: any) => void
) {
  const socket = new WebSocket(
    "ws://127.0.0.1:8000/ws/spectrum"
  )

  socket.onmessage = (event) => {
    const payload = JSON.parse(
      event.data
    )

    onMessage(payload)
  }

  return socket
}