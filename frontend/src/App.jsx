import { useState } from "react";
import Navbar from "./components/Navbar";
import CartDrawer from "./components/CartDrawer";
import StorePage from "./pages/StorePage";
import DashboardPage from "./pages/DashboardPage";
import { useCart } from "./hooks/useCart";
import { useUserProfile } from "./hooks/useUserProfile";

export default function App() {
  const [page, setPage] = useState("store"); // "store" | "dashboard" | "cart"
  const [cartOpen, setCartOpen] = useState(false);
  const { profile } = useUserProfile("jgarcia");
  const { items, addToCart, removeFromCart, updateQuantity, clearCart, total, count } = useCart();

  const handleAddToCart = (product) => {
    addToCart(product);
    setCartOpen(true);
  };

  const handleNavigate = (dest) => {
    if (dest === "cart") {
      setCartOpen(true);
    } else {
      setPage(dest);
    }
  };

  return (
    <div className="app">
      <Navbar
        cartCount={count}
        user={profile}
        activePage={page}
        onNavigate={handleNavigate}
      />

      <main className="app-main">
        {page === "store" && (
          <StorePage onAddToCart={handleAddToCart} />
        )}
        {page === "dashboard" && (
          <DashboardPage onNavigate={handleNavigate} />
        )}
        {page === "profile" && (
          <DashboardPage onNavigate={handleNavigate} />
        )}
      </main>

      <footer className="app-footer">
        <div className="footer-links">
          <button onClick={() => setPage("dashboard")}>Mis Pedidos</button>
          <button>Soporte</button>
          <button>Política de Privacidad</button>
        </div>
        <span>© 2024 EcoCart Inc.</span>
      </footer>

      {cartOpen && (
        <CartDrawer
          items={items}
          total={total}
          onUpdateQuantity={updateQuantity}
          onRemove={removeFromCart}
          onClose={() => setCartOpen(false)}
          onCheckout={() => {
            alert("¡Gracias por tu compra! (checkout no implementado aún)");
            clearCart();
            setCartOpen(false);
          }}
        />
      )}
    </div>
  );
}