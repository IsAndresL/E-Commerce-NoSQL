function StatsGrid({ profile, orders, orderDetails }) {
  return (
    <section className="stats-grid">
      <article className="stat-card">
        <span>Usuario</span>
        <strong>{profile.name}</strong>
        <p>{profile.email}</p>
      </article>
      <article className="stat-card">
        <span>Pedidos</span>
        <strong>{orders.length}</strong>
        <p>Recientes del usuario</p>
      </article>
      <article className="stat-card">
        <span>Pedido activo</span>
        <strong>{orderDetails.order_id}</strong>
        <p>{orderDetails.status}</p>
      </article>
    </section>
  )
}

export default StatsGrid
