import { money } from '../../utils/formatters'

function OrderDetailsPanel({ orderDetails }) {
  return (
    <article className="panel details-panel">
      <div className="panel-head">
        <h2>Detalle del pedido</h2>
        <span className="panel-subtitle">{orderDetails.order_id}</span>
      </div>
      <div className="details-grid">
        <div className="detail-card detail-card-wide">
          <span>Informacion general</span>
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
          <span>Direccion de envio</span>
          <strong>{orderDetails.shipping_address}</strong>
        </div>
      </div>
    </article>
  )
}

export default OrderDetailsPanel
