import { useState } from "react";
import Navbar from "./components/Navbar";
import CartDrawer from "./components/CartDrawer";
import StorePage from "./pages/StorePage";
import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";
import { useCart } from "./hooks/useCart";
import { useUserProfile } from "./hooks/useUserProfile";
import { useSession } from "./hooks/useSession";

export default function App() {
  const [page, setPage] = useState("store"); // "store" | "dashboard" | "cart"
  const [cartOpen, setCartOpen] = useState(false);
  const { userId, isAuthenticated, signIn, signOut } = useSession();

  const handleLogin = (nextUserId) => {
    signIn(nextUserId);
    setPage("store");
  };

  if (!isAuthenticated) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <AuthenticatedApp
      page={page}
      setPage={setPage}
      cartOpen={cartOpen}
      setCartOpen={setCartOpen}
      userId={userId}
      onLogout={signOut}
    />
  );
}

function AuthenticatedApp({ page, setPage, cartOpen, setCartOpen, userId, onLogout }) {
  const { profile } = useUserProfile(userId);
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
        onLogout={onLogout}
      />

      <main className="app-main">
        {page === "store" && (
          <StorePage onAddToCart={handleAddToCart} />
        )}
        {page === "dashboard" && (
          <DashboardPage onNavigate={handleNavigate} userId={userId} />
        )}
        {page === "profile" && (
          <DashboardPage onNavigate={handleNavigate} userId={userId} />
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