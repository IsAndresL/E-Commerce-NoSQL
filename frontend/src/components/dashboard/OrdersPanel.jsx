import { money, statusTone } from '../../utils/formatters'

function OrdersPanel({ userId, orders }) {
  return (
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
              <th>Direccion envio</th>
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
  )
}

export default OrdersPanel
