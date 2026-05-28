import { useState, useEffect, useRef } from "react";
import {
  IconBrand,
  IconSearch,
  IconCart,
  IconMapPin,
  IconProfile,
  IconLogout,
} from "./icons/Icons";
import { IconClose } from "./icons/Icons";

export default function Navbar({ cartCount, user, activePage, onNavigate, onLogout, onSearch, searchValue = "" }) {
  const [showProfile, setShowProfile] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const mobileMenuRef = useRef(null);
  const profileRef = useRef(null);
  // Close menus when clicking outside
  useOutsideClick(profileRef, () => setShowProfile(false));
  useOutsideClick(mobileMenuRef, () => setShowMobileMenu(false));
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
        <IconBrand className="brand-icon" />
        <span className="brand-name">EcoCart</span>
      </div>

      <div className="navbar-search-box">
        <IconSearch className="search-icon" />
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
            <IconClose className="search-reset-icon" />
          </button>
        )}
      </div>

      <div className="navbar-actions">
        {/* Desktop actions (hidden on small screens) */}
        <div className="navbar-actions-desktop">
          <button className="cart-btn" onClick={() => onNavigate("cart")}> 
            <IconCart className="cart-icon" /> Carrito
            {cartCount > 0 && <span className="cart-badge">{cartCount}</span>}
          </button>

          <div className="profile-wrapper" ref={profileRef}>
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
                  <IconMapPin className="dropdown-address-icon" /> <span>{user?.default_address}</span>
                </p>
                <hr />
                <button
                  className="dropdown-link"
                  onClick={() => { setShowProfile(false); onNavigate("profile"); }}
                >
                  <IconProfile className="dropdown-link-icon" /> Mi Perfil
                </button>
                <hr />
                <button
                  className="dropdown-link logout"
                  onClick={() => {
                    setShowProfile(false);
                    onLogout?.();
                  }}
                >
                  <IconLogout className="dropdown-link-icon" /> Cerrar sesión
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Mobile hamburger */}
        <div className="navbar-actions-mobile">
          <button
            className="hamburger-btn"
            aria-label="Abrir menú"
            onClick={() => setShowMobileMenu((s) => !s)}
          >
            <span className="hamburger-line" />
            <span className="hamburger-line" />
            <span className="hamburger-line" />
          </button>

          {showMobileMenu && (
            <div className="mobile-menu" ref={mobileMenuRef}>
              <button className="mobile-menu-item" onClick={() => { setShowMobileMenu(false); onNavigate("cart"); }}>
                <IconCart className="cart-icon" /> Carrito {cartCount > 0 && <span className="cart-badge">{cartCount}</span>}
              </button>
              <button className="mobile-menu-item" onClick={() => { setShowMobileMenu(false); onNavigate("profile"); }}>
                <IconProfile className="dropdown-link-icon" /> Mi Perfil
              </button>
              <button className="mobile-menu-item logout" onClick={() => { setShowMobileMenu(false); onLogout?.(); }}>
                <IconLogout className="dropdown-link-icon" /> Cerrar sesión
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}

// Close mobile menu when clicking outside
function useOutsideClick(ref, handler) {
  useEffect(() => {
    const listener = (e) => {
      if (!ref.current || ref.current.contains(e.target)) return;
      handler(e);
    };
    document.addEventListener("mousedown", listener);
    return () => document.removeEventListener("mousedown", listener);
  }, [ref, handler]);
}

// hook usage: close menus when clicking outside
// (placed after declaration so it's available when component runs)
// (no-op) helper removed