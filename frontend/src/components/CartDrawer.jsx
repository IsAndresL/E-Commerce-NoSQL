import { formatCOP } from "../utils/formatters";

export default function CartDrawer({ items, total, onUpdateQuantity, onRemove, onClose, onCheckout }) {
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
              <button className="btn-checkout" onClick={onCheckout}>
                Proceder al pago →
              </button>
            </div>
          </>
        )}
      </aside>
    </div>
  );
}