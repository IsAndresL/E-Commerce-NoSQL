import { useState, useEffect } from "react";
import { getUserProfile, getRecentOrders } from "../api/ecommerceApi";

const normalizeOrder = (order) => ({
  order_id: order?.order_id || order?.id || "ORD#000",
  status: order?.status || "Pendiente",
  created_at: order?.created_at || order?.createdAt || order?.date || "-",
  shipping_address: order?.shipping_address || order?.shippingAddress || "-",
  total: order?.total ?? 0,
});

export function useUserProfile(userId) {
  const [profile, setProfile] = useState(null);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    const activeUserId = String(userId || "").trim();

    if (!activeUserId) {
      setProfile(null);
      setOrders([]);
      setLoading(false);
      return () => {
        cancelled = true;
      };
    }

    Promise.all([
      getUserProfile(activeUserId).catch(() => null),
      getRecentOrders(activeUserId).catch(() => null),
    ]).then(([profileData, ordersData]) => {
      if (cancelled) return;

      setProfile(profileData || null);
      setOrders(Array.isArray(ordersData) ? ordersData.map(normalizeOrder) : []);
      setLoading(false);
    });

    return () => {
      cancelled = true;
    };
  }, [userId]);

  return { profile, orders, loading };
}