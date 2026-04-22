import { money } from '../../utils/formatters'

function OrderItemsPanel({ orderId, items }) {
  return (
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
  )
}

export default OrderItemsPanel
