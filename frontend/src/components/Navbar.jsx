import { useState } from "react";

export default function Navbar({ cartCount, user, activePage, onNavigate, onLogout }) {
  const [showProfile, setShowProfile] = useState(false);
  const userInitial = (user?.name || "?").trim().charAt(0).toUpperCase();

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
            {user?.avatar_url ? (
              <img src={user.avatar_url} alt={user?.name} className="avatar-sm" />
            ) : (
              <span className="avatar-sm avatar-placeholder">{userInitial}</span>
            )}
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
              <button
                className="dropdown-link logout"
                onClick={() => {
                  setShowProfile(false);
                  onLogout?.();
                }}
              >
                ↩ Cerrar sesión
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}