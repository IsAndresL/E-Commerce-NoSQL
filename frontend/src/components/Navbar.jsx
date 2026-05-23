import { useState } from "react";

export default function Navbar({ cartCount, user, activePage, onNavigate }) {
  const [showProfile, setShowProfile] = useState(false);

  return (
    <nav className="navbar">
      <div className="navbar-brand" onClick={() => onNavigate("store")}>
        <span className="brand-icon">🛍</span>
        <span className="brand-name">EcoCart</span>
      </div>

      <div className="navbar-links">
        <button
          className={`nav-link ${activePage === "store" ? "active" : ""}`}
          onClick={() => onNavigate("store")}
        >
          Inicio
        </button>
        <button className="nav-link" onClick={() => onNavigate("store")}>
          Categorías
        </button>
        <button className="nav-link" onClick={() => onNavigate("store")}>
          Ofertas
        </button>
      </div>

      <div className="navbar-actions">
        <button className="cart-btn" onClick={() => onNavigate("cart")}>
          🛒 Carrito
          {cartCount > 0 && <span className="cart-badge">{cartCount}</span>}
        </button>

        <div className="profile-wrapper">
          <button
            className="profile-btn"
            onClick={() => setShowProfile((p) => !p)}
            aria-label="Perfil"
          >
            <img
              src={user?.avatar_url || `https://i.pravatar.cc/40?u=${user?.user_id}`}
              alt={user?.name}
              className="avatar-sm"
            />
          </button>

          {showProfile && (
            <div className="profile-dropdown">
              <p className="dropdown-greeting">Bienvenido, <strong>{user?.user_id}</strong></p>
              <p className="dropdown-address">
                📍 <span>{user?.default_address}</span>
              </p>
              <hr />
              <button
                className="dropdown-link"
                onClick={() => { setShowProfile(false); onNavigate("dashboard"); }}
              >
                📦 Mis Pedidos
              </button>
              <button
                className="dropdown-link"
                onClick={() => { setShowProfile(false); onNavigate("profile"); }}
              >
                👤 Mi Perfil
              </button>
              <hr />
              <button className="dropdown-link logout">↩ Cerrar sesión</button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}