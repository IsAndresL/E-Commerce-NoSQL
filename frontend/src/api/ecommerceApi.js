const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

async function fetchJson(url, signal, { allow404 = false } = {}) {
  const response = await fetch(url, { signal })

  if (allow404 && response.status === 404) {
    return null
  }

  if (!response.ok) {
    throw new Error(`Error ${response.status}`)
  }

  return response.json()
}

export function getUserProfile(userId, signal) {
  return fetchJson(
    `${API_BASE_URL}/ecommerce/user/${encodeURIComponent(userId)}/profile`,
    signal,
    { allow404: true },
  )
}

export function getUserOrders(userId, signal) {
  return fetchJson(`${API_BASE_URL}/ecommerce/user/${encodeURIComponent(userId)}/orders`, signal)
}

export function getUserOrderDetails(userId, orderId, signal) {
  return fetchJson(
    `${API_BASE_URL}/ecommerce/user/${encodeURIComponent(userId)}/order/${encodeURIComponent(orderId)}/details`,
    signal,
    { allow404: true },
  )
}

export function getUserOrderItems(userId, orderId, signal) {
  return fetchJson(
    `${API_BASE_URL}/ecommerce/user/${encodeURIComponent(userId)}/order/${encodeURIComponent(orderId)}/items`,
    signal,
    { allow404: true },
  )
}
