import { formatCOP } from "../utils/formatters";

export default function CartDrawer({ items, total, onUpdateQuantity, onRemove, onClose, onCheckout, checkoutLoading = false }) {
  const shipping = total >= 180000 ? 0 : items.length > 0 ? 14900 : 0;
  const grandTotal = total + shipping;

  return (
    <div className="cart-overlay" onClick={onClose}>
      <aside className="cart-drawer" onClick={(e) => e.stopPropagation()}>
        <div className="cart-header">
          <h2>🛒 Tu Carrito</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        {items.length === 0 ? (
          <div className="cart-empty">
            <p>🛍 Tu carrito está vacío</p>
            <div className="empty-trust">
              <span>Pago seguro</span>
              <span>Checkout como invitado</span>
              <span>Mercado Pago · PayU · ePayco</span>
            </div>
            <button className="btn-primary" onClick={onClose}>
              Explorar productos
            </button>
          </div>
        ) : (
          <>
            <div className="cart-items">
              {items.map((item) => (
                <div key={item.product_id} className="cart-item">
                  <img
                    src={item.image_url}
                    alt={item.name}
                    className="cart-item-img"
                  />
                  <div className="cart-item-info">
                    <p className="cart-item-name">{item.name}</p>
                    <p className="cart-item-price">{formatCOP(item.price)}</p>
                    <div className="qty-controls">
                      <button onClick={() => onUpdateQuantity(item.product_id, item.quantity - 1)}>−</button>
                      <span>{item.quantity}</span>
                      <button onClick={() => onUpdateQuantity(item.product_id, item.quantity + 1)}>+</button>
                    </div>
                  </div>
                  <div className="cart-item-right">
                    <p className="cart-item-subtotal">{formatCOP(item.price * item.quantity)}</p>
                    <button className="remove-btn" onClick={() => onRemove(item.product_id)}>🗑</button>
                  </div>
                </div>
              ))}
            </div>

            <div className="cart-footer">
              <div className="cart-total">
                <span>Total</span>
                <span>{formatCOP(total)}</span>
              </div>
              <div className="checkout-breakdown">
                <div>
                  <span>Envío estimado</span>
                  <strong>{shipping === 0 ? "Gratis" : formatCOP(shipping)}</strong>
                </div>
                <div>
                  <span>Seguridad y soporte</span>
                  <strong>Incluidos</strong>
                </div>
                <div>
                  <span>Total a pagar</span>
                  <strong>{formatCOP(grandTotal)}</strong>
                </div>
              </div>
              <div className="payment-badges">
                <span>ePayco</span>
                <span>Mercado Pago</span>
                <span>PayU</span>
              </div>
              <p className="checkout-note">Compra como invitado o con cuenta. Mostramos costos antes de completar el pago.</p>
              <button className="btn-checkout" onClick={onCheckout} disabled={checkoutLoading}>
                {checkoutLoading ? "Procesando pago..." : "Proceder al pago seguro →"}
              </button>
            </div>
          </>
        )}
      </aside>
    </div>
  );
}