import { useState } from "react";

export default function Navbar({ cartCount, user, activePage, onNavigate, onLogout, onSearch, searchValue = "" }) {
  const [showProfile, setShowProfile] = useState(false);
  const [search, setSearch] = useState(searchValue);
  const userInitial = (user?.name || "?").trim().charAt(0).toUpperCase();

  const handleSearchChange = (e) => {
    const value = e.target.value;
    setSearch(value);
    onSearch?.(value);
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand" onClick={() => onNavigate("store")}>
        <span className="brand-icon">🛍</span>
        <span className="brand-name">EcoCart</span>
      </div>

      <div className="navbar-search-box">
        <span className="search-icon">🔎</span>
        <input
          type="text"
          placeholder="Busca productos..."
          value={search}
          onChange={handleSearchChange}
          className="navbar-search-input"
        />
        {search && (
          <button 
            className="search-reset-navbar" 
            onClick={() => {
              setSearch("");
              onSearch?.("");
            }}
          >
            ✕
          </button>
        )}
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
              <p className="dropdown-greeting">Bienvenido, <strong>{user?.name}</strong></p>
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