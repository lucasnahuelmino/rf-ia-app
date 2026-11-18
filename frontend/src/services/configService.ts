import { API_BASE } from "../config"

export async function getSpectrumConfig() {
  const response = await fetch(
    `${API_BASE}/spectrum/config`
  )

  if (!response.ok) {
    throw new Error(
      `Config request failed: ${response.status}`
    )
  }

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

  if (!response.ok) {
    throw new Error(
      `Config update failed: ${response.status}`
    )
  }

  return await response.json()
}