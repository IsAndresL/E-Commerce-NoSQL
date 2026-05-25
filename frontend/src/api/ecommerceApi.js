const BASE_URL = String(
  import.meta.env.VITE_API_BASE_URL ||
    import.meta.env.VITE_API_URL ||
    "http://localhost:4566"
).replace(/\/+$/, "");

function buildUrl(path) {
  const cleanPath = String(path || "").replace(/^\/+/, "");
  return `${BASE_URL}/${cleanPath}`;
}

async function apiFetch(path) {
  const res = await fetch(buildUrl(path));
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