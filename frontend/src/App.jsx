import OrderDetailsPanel from './components/dashboard/OrderDetailsPanel'
import OrderItemsPanel from './components/dashboard/OrderItemsPanel'
import OrdersPanel from './components/dashboard/OrdersPanel'
import ProfilePanel from './components/dashboard/ProfilePanel'
import StatsGrid from './components/dashboard/StatsGrid'
import { useDashboardData } from './hooks/useDashboardData'

function App() {
  const { userId, orderId, profile, orders, orderDetails, items, loading, error, hasData } = useDashboardData()

  return (
    <main className="app-shell">
      <section className="hero-card">
        <div>
          <p className="eyebrow">AMAZONIA</p>
          <h1>Panel de control</h1>
        </div>
      </section>

      {error ? <div className="alert-card">{error}</div> : null}
      {!loading && !error && !hasData ? <div className="empty-state-card">No hay datos para mostrar.</div> : null}

      <StatsGrid profile={profile} orders={orders} orderDetails={orderDetails} />

      <section className="content-grid">
        <ProfilePanel profile={profile} userId={userId} loading={loading} />
        <OrdersPanel userId={userId} orders={orders} />
        <OrderDetailsPanel orderDetails={orderDetails} />
        <OrderItemsPanel orderId={orderId} items={items} />
      </section>
    </main>
  )
}

export default App