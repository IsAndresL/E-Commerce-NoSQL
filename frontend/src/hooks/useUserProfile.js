import { useState, useEffect } from "react";
import { getUserProfile, getRecentOrders } from "../api/ecommerceApi";

const MOCK_USER = {
  user_id: "jgarcia",
  name: "Juan García",
  email: "jgarcia@x.com",
  default_address: "Calle 100 # 12-34, Apto 501, Bogotá, Colombia",
  payment_methods: ["Visa ...1234", "PayPal"],
  avatar_url: "https://i.pravatar.cc/150?u=jgarcia",
};

const MOCK_ORDERS = [
  { order_id: "ORD#555", status: "Pago exitoso", created_at: "2023-11-15T14:36Z", shipping_address: "Calle 10" },
  { order_id: "ORD#554", status: "Enviado", created_at: "2023-11-01T09:15Z", shipping_address: "Calle 10" },
  { order_id: "ORD#553", status: "Pago exitoso", created_at: "2023-10-27T08:00Z", shipping_address: "Calle 10" },
  { order_id: "ORD#552", status: "Enviado", created_at: "2023-10-10T11:45Z", shipping_address: "Ave. 5" },
  { order_id: "ORD#551", status: "Pago exitoso", created_at: "2023-09-25T16:00Z", shipping_address: "Ave. 5" },
];

export function useUserProfile(userId = "jgarcia") {
  const [profile, setProfile] = useState(null);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getUserProfile(userId).catch(() => MOCK_USER),
      getRecentOrders(userId).catch(() => MOCK_ORDERS),
    ]).then(([profileData, ordersData]) => {
      setProfile(profileData || MOCK_USER);
      setOrders(Array.isArray(ordersData) ? ordersData : MOCK_ORDERS);
      setLoading(false);
    });
  }, [userId]);

  return { profile: profile || MOCK_USER, orders, loading };
}