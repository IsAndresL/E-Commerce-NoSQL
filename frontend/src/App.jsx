import { useEffect, useMemo, useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

function money(value) {
  if (value === null || value === undefined || value === '') {
    return '$0'
  }

  if (typeof value === 'number') {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(value)
  }

  const text = String(value)
  return text.startsWith('$') ? text : `$${text}`
}

function statusTone(status) {
  const normalized = String(status || '').toLowerCase()

  if (normalized.includes('pago')) {
    return 'tone-success'
  }

  if (normalized.includes('enviado')) {
    return 'tone-warning'
  }

  return 'tone-neutral'
}

function App() {
  const [dashboard, setDashboard] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const { userId, orderId } = useMemo(() => {
    const params = new URLSearchParams(window.location.search)
    return {
      userId: params.get('user_id') || '1',
      orderId: params.get('order_id') || '555',
    }
  }, [])

  useEffect(() => {
    const controller = new AbortController()

    const fetchJson = async (url, { allow404 = false } = {}) => {
      const response = await fetch(url, { signal: controller.signal })

      if (allow404 && response.status === 404) {
        return null
      }

      if (!response.ok) {
        throw new Error(`Error ${response.status}`)
      }

      return response.json()
    }

    const loadDashboard = async () => {
      setLoading(true)
      setError('')

      try {
        const [profile, orders] = await Promise.all([
          fetchJson(`${API_BASE_URL}/ecommerce/user/${encodeURIComponent(userId)}/profile`, { allow404: true }),
          fetchJson(`${API_BASE_URL}/ecommerce/user/${encodeURIComponent(userId)}/orders`),
        ])

        let orderDetails = null
        let items = []

        try {
          const [detailsResult, itemsResult] = await Promise.all([
            fetchJson(
              `${API_BASE_URL}/ecommerce/user/${encodeURIComponent(userId)}/order/${encodeURIComponent(orderId)}/details`,
              { allow404: true },
            ),
            fetchJson(`${API_BASE_URL}/ecommerce/user/${encodeURIComponent(userId)}/order/${encodeURIComponent(orderId)}/items`, {
              allow404: true,
            }),
          ])
          orderDetails = detailsResult
          items = Array.isArray(itemsResult) ? itemsResult : []
        } catch (orderError) {
          if (orderError.name === 'AbortError') {
            throw orderError
          }
          orderDetails = null
          items = []
        }

        setDashboard({
          user_id: userId,
          order_id: orderId,
          profile,
          orders: Array.isArray(orders) ? orders : [],
          order_details: orderDetails,
          items,
        })
      } catch (err) {
        if (err.name !== 'AbortError') {
          setError('No se pudo conectar con la API.')
          setDashboard(null)
        }
      } finally {
        setLoading(false)
      }
    }

    loadDashboard()

    return () => controller.abort()
  }, [userId, orderId])

  const profile = dashboard?.profile || {
    name: 'Sin datos',
    email: '-',
    addresses: [],
    payments: [],
  }

  const orders = dashboard?.orders || []
  const orderDetails = dashboard?.order_details || {
    order_id: '-',
    date: '-',
    status: '-',
    shipping_address: '-',
    total: 0,
  }
  const items = dashboard?.items || []
  const hasData =
    Boolean(profile?.name && profile.name !== 'Sin datos') ||
    orders.length > 0 ||
    items.length > 0 ||
    (orderDetails.order_id && orderDetails.order_id !== 'ORD#000')

  return (
    <main className="app-shell">
      <section className="hero-card">
        <div>
          <p className="eyebrow">Mi Mercado Global</p>
          <h1>Panel de control conectado a FastAPI y DynamoDB</h1>
        </div>
      </section>

      {error ? <div className="alert-card">{error}</div> : null}
      {!loading && !error && !hasData ? <div className="empty-state-card">No hay datos para mostrar.</div> : null}

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

      <section className="content-grid">
        <article className={`panel profile-panel ${loading ? 'is-loading' : ''}`}>
          <div className="panel-head">
            <h2>Mi perfil</h2>
            <span className="panel-subtitle">USER#{userId}</span>
          </div>
          <div className="profile-layout">
            <div className="avatar">{profile.name ? profile.name.slice(0, 1).toUpperCase() : 'U'}</div>
            <div>
              <h3>{profile.name}</h3>
              <p>{profile.email}</p>
              <div className="chips">
                {(profile.addresses || []).map((item) => (
                  <span key={item} className="chip">
                    {item}
                  </span>
                ))}
              </div>
              <div className="chips">
                {(profile.payments || []).map((item) => (
                  <span key={item} className="chip chip-alt">
                    {item}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </article>

        <article className="panel orders-panel">
          <div className="panel-head">
            <h2>Pedidos recientes</h2>
            <span className="panel-subtitle">USER#{userId}</span>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Estado</th>
                  <th>Fecha</th>
                  <th>Dirección envío</th>
                  <th className="align-right">Total</th>
                </tr>
              </thead>
              <tbody>
                {orders.length > 0 ? (
                  orders.map((order) => (
                    <tr key={`${order.id}-${order.created_at}`}>
                      <td>
                        <span className={`badge ${statusTone(order.status)}`}>{order.status}</span>
                      </td>
                      <td>{order.created_at}</td>
                      <td>{order.shipping_address}</td>
                      <td className="align-right">{money(order.total)}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td className="empty" colSpan="4">
                      No hay pedidos disponibles.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </article>

        <article className="panel details-panel">
          <div className="panel-head">
            <h2>Detalle del pedido</h2>
            <span className="panel-subtitle">{orderDetails.order_id}</span>
          </div>
          <div className="details-grid">
            <div className="detail-card detail-card-wide">
              <span>Información general</span>
              <strong>{orderDetails.status}</strong>
              <p>Pedido {orderDetails.order_id}</p>
            </div>
            <div className="detail-card">
              <span>Fecha</span>
              <strong>{orderDetails.date}</strong>
            </div>
            <div className="detail-card">
              <span>Total</span>
              <strong>{money(orderDetails.total)}</strong>
            </div>
            <div className="detail-card detail-card-wide">
              <span>Dirección de envío</span>
              <strong>{orderDetails.shipping_address}</strong>
            </div>
          </div>
        </article>

        <article className="panel items-panel">
          <div className="panel-head">
            <h2>Items del pedido</h2>
            <span className="panel-subtitle">ORDER#{orderId}</span>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Producto</th>
                  <th className="align-center">Cantidad</th>
                  <th className="align-right">Precio unitario</th>
                  <th className="align-right">Subtotal</th>
                </tr>
              </thead>
              <tbody>
                {items.length > 0 ? (
                  items.map((item) => (
                    <tr key={`${item.name}-${item.quantity}`}>
                      <td>{item.name}</td>
                      <td className="align-center">{item.quantity}</td>
                      <td className="align-right">{money(item.unit_price)}</td>
                      <td className="align-right">{money(item.subtotal)}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td className="empty" colSpan="4">
                      No hay items disponibles.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </article>
      </section>
    </main>
  )
}

export default App