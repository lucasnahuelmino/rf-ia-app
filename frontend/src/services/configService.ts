const API_BASE = "http://127.0.0.1:8000"

export async function getSpectrumConfig() {
  const response = await fetch(
    `${API_BASE}/spectrum/config`
  )

  return await response.json()
}

export async function updateSpectrumConfig(
  payload: any
) {
  const response = await fetch(
    `${API_BASE}/spectrum/config`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(payload),
    }
  )

  return await response.json()
}