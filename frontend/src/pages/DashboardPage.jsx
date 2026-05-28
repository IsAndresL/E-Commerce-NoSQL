import { useState } from "react";
import { useUserProfile } from "../hooks/useUserProfile";
import { formatDate, statusColor, formatCOP } from "../utils/formatters";
import { IconReceipt, IconCalendar, IconMapPin, IconMoney, IconBack } from "../components/icons/Icons";
import { getOrderItems } from "../api/ecommerceApi";

export default function DashboardPage({ onNavigate, userId }) {
  const { profile, orders, loading } = useUserProfile(userId);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [orderItems, setOrderItems] = useState([]);
  const [loadingOrder, setLoadingOrder] = useState(false);

  const handleSelectOrder = async (order) => {
    setSelectedOrder(order);
    setLoadingOrder(true);
    try {
      const orderKey = String(order.order_id || order.id || "").replace(/^[A-Z]+#/, "");
      const items = await getOrderItems(orderKey);
      setOrderItems(Array.isArray(items) ? items : []);
    } catch {
      setOrderItems([]);
    } finally {
      setLoadingOrder(false);
    }
  };

  if (loading) return <div className="loading-screen">Cargando perfil y pedidos...</div>;

  if (!profile) {
    return (
      <div className="dashboard-page">
        <h1 className="page-title">Mi Mercado Global — Panel de Control</h1>
        <p className="empty-state-message">No se encontró el usuario.</p>
      </div>
    );
  }

  const profileInitial = (profile.name || "?").trim().charAt(0).toUpperCase();

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <button className="back-to-store" onClick={() => onNavigate?.("store")} aria-label="Volver a tienda">
          <IconBack className="back-icon" /> Volver a tienda
        </button>
        <h1 className="page-title">Mi Mercado Global — Panel de Control</h1>
      </div>
      <p className="breadcrumb">Inicio › Usuario › {profile.name} › Pedidos Recientes</p>

      <div className="dashboard-grid">
        {/* Profile card */}
        <aside className="profile-card">
          <h2>Mi Perfil</h2>
          <div className="profile-header">
            {profile.avatar_url ? (
              <img src={profile.avatar_url} alt={profile.name} className="avatar-lg" />
            ) : (
              <span className="avatar-lg avatar-placeholder">{profileInitial}</span>
            )}
            <div>
              <p className="profile-name">{profile.name}</p>
              <p className="profile-email">{profile.email}</p>
            </div>
          </div>
          <div className="profile-details">
            <p><strong>Direcciones:</strong></p>
            <p className="detail-value">{profile.default_address}</p>
            <p><strong>Métodos de Pago:</strong></p>
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
                  <span className="meta-label"><IconReceipt className="meta-icon" /> {selectedOrder.order_id}</span>
                  <span className={`status-badge ${statusColor(selectedOrder.status)}`}>
                    Estado: {selectedOrder.status}
                  </span>
                </div>
              <div className="meta-block">
                  <span><IconCalendar className="meta-small-icon" /> {formatDate(selectedOrder.created_at)}</span>
                  <span><IconMapPin className="meta-small-icon" /> Dir: {selectedOrder.shipping_address}</span>
                  {selectedOrder.total && <span><IconMoney className="meta-small-icon" /> Total: {formatCOP(selectedOrder.total)}</span>}
              </div>
            </div>

            <h3>Ítems del Pedido</h3>
            {loadingOrder ? (
              <p>Cargando ítems...</p>
            ) : orderItems.length === 0 ? (
              <p className="empty-state-message">No se encontraron productos.</p>
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
                    <tr key={item.product_id || `${item.name}-${item.quantity}-${item.unit_price}`}>
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
            <p>Selecciona un pedido para ver su detalle</p>
          </section>
        )}
      </div>
    </div>
  );
}