const rawBaseUrl = import.meta.env.VITE_API_BASE_URL;

if (!rawBaseUrl) {
  throw new Error("Missing VITE_API_BASE_URL in frontend environment");
}

const BASE_URL = String(rawBaseUrl).replace(/\/+$/, "");

function buildUrl(path) {
  const cleanPath = String(path || "").replace(/^\/+/, "");
  return `${BASE_URL}/${cleanPath}`;
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
  if (!res.ok) throw new Error(`Error ${res.status}: ${res.statusText}`);
  return res.json();
}

export const getUserProfile = (userId) =>
  apiFetch(`/ecommerce/user/${userId}/profile`);

export const getRecentOrders = (userId) =>
  apiFetch(`/ecommerce/user/${userId}/orders`);

export const getOrderDetails = (orderId) =>
  apiFetch(`/ecommerce/order/${orderId}/details`);

export const getOrderItems = (orderId) =>
  apiFetch(`/ecommerce/order/${orderId}/items`);

export const getUserOrderDetails = (userId, orderId) =>
  apiFetch(`/ecommerce/user/${userId}/order/${orderId}/details`);

export const getUserOrderItems = (userId, orderId) =>
  apiFetch(`/ecommerce/user/${userId}/order/${orderId}/items`);

export const getDashboardData = () =>
  apiFetch(`/ecommerce/dashboard-data`);

export const getProducts = () =>
  apiFetch(`/products`);

export const getUsers = () =>
  apiFetch(`/ecommerce/users`);

export const createOrder = (userId, payload) =>
  apiFetch(`/ecommerce/user/${userId}/orders`, {
    method: "POST",
    body: payload,
  });