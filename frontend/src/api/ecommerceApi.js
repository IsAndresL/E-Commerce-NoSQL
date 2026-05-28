const rawBaseUrl = import.meta.env.VITE_API_BASE_URL;

if (!rawBaseUrl) {
  throw new Error("Missing VITE_API_BASE_URL in frontend environment");
}

const BASE_URL = String(rawBaseUrl).replace(/\/+$/, "");

function buildUrl(path) {
  const cleanPath = String(path || "").replace(/^\/+/, "");
  return `${BASE_URL}/${cleanPath}`;
}

function encodePathPart(value) {
  return encodeURIComponent(String(value));
}

async function apiFetch(path, options = {}) {
  const { body, headers, ...fetchOptions } = options;
  const hasBody = body !== undefined;
  const requestHeaders = { ...(headers || {}) };

  if (hasBody && !requestHeaders["Content-Type"]) {
    requestHeaders["Content-Type"] = "text/plain;charset=UTF-8";
  }

  const res = await fetch(buildUrl(path), {
    ...fetchOptions,
    headers: requestHeaders,
    body: hasBody ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const payload = await res.json();
      detail = payload?.detail || detail;
    } catch {
      // Keep the HTTP status text when the backend does not return JSON.
    }
    throw new Error(`Error ${res.status}: ${detail}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const getUserProfile = (userId) =>
  apiFetch(`/ecommerce/user/${encodePathPart(userId)}/profile`);

export const getRecentOrders = (userId) =>
  apiFetch(`/ecommerce/user/${encodePathPart(userId)}/orders`);

export const getOrderDetails = (orderId) =>
  apiFetch(`/ecommerce/order/${encodePathPart(orderId)}/details`);

export const getOrderItems = (orderId) =>
  apiFetch(`/ecommerce/order/${encodePathPart(orderId)}/items`);

export const getUserOrderDetails = (userId, orderId) =>
  apiFetch(`/ecommerce/user/${encodePathPart(userId)}/order/${encodePathPart(orderId)}/details`);

export const getUserOrderItems = (userId, orderId) =>
  apiFetch(`/ecommerce/user/${encodePathPart(userId)}/order/${encodePathPart(orderId)}/items`);

export const getDashboardData = () =>
  apiFetch(`/ecommerce/dashboard-data`);

function toQueryString(params = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      query.set(key, value);
    }
  });
  const serialized = query.toString();
  return serialized ? `?${serialized}` : "";
}

export const getProducts = (params = {}) =>
  apiFetch(`/products${toQueryString(params)}`);

export const getProductCategories = () =>
  apiFetch(`/products/categories`);

export const getUsers = () =>
  apiFetch(`/ecommerce/users`);

export const getCart = (userId) =>
  apiFetch(`/ecommerce/user/${encodePathPart(userId)}/cart`);

export const addCartItem = (userId, productId, quantity = 1) =>
  apiFetch(`/ecommerce/user/${encodePathPart(userId)}/cart/items`, {
    method: "POST",
    body: { product_id: productId, quantity },
  });

export const updateCartItem = (userId, productId, quantity) =>
  apiFetch(`/ecommerce/user/${encodePathPart(userId)}/cart/items/${encodePathPart(productId)}`, {
    method: "POST",
    body: { quantity },
  });

export const removeCartItem = (userId, productId) =>
  apiFetch(`/ecommerce/user/${encodePathPart(userId)}/cart/items/${encodePathPart(productId)}`, {
    method: "POST",
    body: { quantity: 0 },
  });

export const clearCartItems = (userId) =>
  apiFetch(`/ecommerce/user/${encodePathPart(userId)}/cart`, {
    method: "DELETE",
  });

export const createOrder = (userId, payload) =>
  apiFetch(`/ecommerce/user/${encodePathPart(userId)}/orders`, {
    method: "POST",
    body: payload,
  });
