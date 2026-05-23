import { useState } from "react";
import { useUserProfile } from "../hooks/useUserProfile";
import { formatDate, statusColor, formatCOP } from "../utils/formatters";
import { getOrderItems } from "../api/ecommerceApi";

export default function DashboardPage({ onNavigate }) {
  const { profile, orders, loading } = useUserProfile("jgarcia");
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [orderItems, setOrderItems] = useState([]);
  const [loadingOrder, setLoadingOrder] = useState(false);

  const handleSelectOrder = async (order) => {
    setSelectedOrder(order);
    setLoadingOrder(true);
    try {
      const items = await getOrderItems(order.order_id.replace("#", ""));
      setOrderItems(Array.isArray(items) ? items : MOCK_ITEMS);
    } catch {
      setOrderItems(MOCK_ITEMS);
    } finally {
      setLoadingOrder(false);
    }
  };

  const MOCK_ITEMS = [
    { product_id: "p1", name: "Laptop XPS", quantity: 1, unit_price: 1200000, subtotal: 1200000, image_url: "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=60&h=60&fit=crop" },
    { product_id: "p2", name: 'Libro "El Capital"', quantity: 2, unit_price: 25000, subtotal: 50000, image_url: "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=60&h=60&fit=crop" },
  ];

  if (loading) return <div className="loading-screen">Cargando...</div>;

  return (
    <div className="dashboard-page">
      <h1 className="page-title">Mi Mercado Global — Panel de Control</h1>
      <p className="breadcrumb">Inicio › Usuario › {profile.user_id} › Pedidos Recientes</p>

      <div className="dashboard-grid">
        {/* Profile card */}
        <aside className="profile-card">
          <h2>Mi Perfil</h2>
          <div className="profile-header">
            <img
              src={profile.avatar_url || `https://i.pravatar.cc/80?u=${profile.user_id}`}
              alt={profile.name}
              className="avatar-lg"
            />
            <div>
              <p className="profile-name">{profile.name}</p>
              <p className="profile-email">{profile.email}</p>
            </div>
          </div>
          <div className="profile-details">
            <p><strong>📍 Direcciones:</strong></p>
            <p className="detail-value">{profile.default_address}</p>
            <p><strong>💳 Pagos:</strong></p>
            <p className="detail-value">
              {(profile.payment_methods || []).join(", ")}
            </p>
          </div>

          <h3>Pedidos Recientes</h3>
          <table className="orders-table">
            <thead>
              <tr>
                <th>Estado</th>
                <th>Fecha Creación</th>
                <th>Dirección Envío</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((order) => (
                <tr
                  key={order.order_id}
                  className={`order-row ${selectedOrder?.order_id === order.order_id ? "selected" : ""}`}
                  onClick={() => handleSelectOrder(order)}
                >
                  <td>
                    <span className={`status-badge ${statusColor(order.status)}`}>
                      {order.status}
                    </span>
                  </td>
                  <td>{formatDate(order.created_at)}</td>
                  <td>{order.shipping_address}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </aside>

        {/* Order detail */}
        {selectedOrder && (
          <section className="order-detail-card">
            <h2>Detalle del Pedido {selectedOrder.order_id}</h2>

            <div className="order-meta">
              <div className="meta-block">
                <span className="meta-label">🧾 {selectedOrder.order_id}</span>
                <span className={`status-badge ${statusColor(selectedOrder.status)}`}>
                  Estado: {selectedOrder.status}
                </span>
              </div>
              <div className="meta-block">
                <span>📅 {formatDate(selectedOrder.created_at)}</span>
                <span>📍 Dir: {selectedOrder.shipping_address}</span>
                {selectedOrder.total && <span>💰 Total: {formatCOP(selectedOrder.total)}</span>}
              </div>
            </div>

            <h3>Ítems del Pedido</h3>
            {loadingOrder ? (
              <p>Cargando ítems...</p>
            ) : (
              <table className="items-table">
                <thead>
                  <tr>
                    <th>Producto</th>
                    <th>Cantidad</th>
                    <th>Precio Unit.</th>
                    <th>Subtotal</th>
                  </tr>
                </thead>
                <tbody>
                  {orderItems.map((item) => (
                    <tr key={item.product_id}>
                      <td className="item-name-cell">
                        {item.image_url && (
                          <img src={item.image_url} alt={item.name} className="item-thumb" />
                        )}
                        {item.name}
                      </td>
                      <td>{item.quantity}</td>
                      <td>{formatCOP(item.unit_price)}</td>
                      <td>{formatCOP(item.subtotal)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>
        )}

        {!selectedOrder && (
          <section className="order-detail-card empty-detail">
            <p>👈 Selecciona un pedido para ver su detalle</p>
          </section>
        )}
      </div>
    </div>
  );
}