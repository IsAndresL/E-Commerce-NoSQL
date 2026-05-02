import React, { useEffect, useState } from "react";
import { getDashboardData } from "./api/ecommerceApi";
import OrderDetailsPanel from './components/dashboard/OrderDetailsPanel'
import OrderItemsPanel from './components/dashboard/OrderItemsPanel'
import OrdersPanel from './components/dashboard/OrdersPanel'
import ProfilePanel from './components/dashboard/ProfilePanel'
import StatsGrid from './components/dashboard/StatsGrid'

function App() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const userId = new URLSearchParams(window.location.search).get("user_id");
  const orderId = new URLSearchParams(window.location.search).get("order_id");

  useEffect(() => {
    if (!userId || !orderId) {
      setError("Faltan parámetros user_id y order_id en la URL");
      setLoading(false);
      return;
    }

    const controller = new AbortController();
    const signal = controller.signal;

    getDashboardData(userId, orderId, signal)
      .then((data) => {
        setDashboard(data);
        setLoading(false);
      })
      .catch((err) => {
        if (err.name !== "AbortError") {
          setError(err.message);
          setLoading(false);
        }
      });

    return () => controller.abort();
  }, [userId, orderId]);

  if (loading) {
    return <div>Cargando datos del dashboard...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!dashboard) {
    return <div>No hay datos disponibles.</div>;
  }

  const { profile, orders, order_details, items } = dashboard;

  return (
    <main className="app-shell">
      <section className="hero-card">
        <div>
          <p className="eyebrow">AMAZONIA</p>
          <h1>Panel de control</h1>
        </div>
      </section>

      {error ? <div className="alert-card">{error}</div> : null}
      {!loading && !error && !Object.keys(dashboard).length ? <div className="empty-state-card">No hay datos para mostrar.</div> : null}

      <StatsGrid profile={profile} orders={orders} orderDetails={order_details} />

      <section className="content-grid">
        <ProfilePanel profile={profile} userId={userId} loading={loading} />
        <OrdersPanel userId={userId} orders={orders} />
        <OrderDetailsPanel orderDetails={order_details} />
        <OrderItemsPanel orderId={orderId} items={items} />
      </section>
    </main>
  );
}

export default App;