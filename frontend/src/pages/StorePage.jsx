import { useState, useMemo } from "react";
import ProductCard from "../components/ProductCard";
import { useProducts } from "../hooks/useProducts";
import { CATEGORIES } from "../utils/formatters";

export default function StorePage({ onAddToCart }) {
  const { products, loading } = useProducts();
  const [search, setSearch] = useState("");
  const [activeCategory, setActiveCategory] = useState("Todos");

  const filtered = useMemo(() => {
    return products.filter((p) => {
      const matchCat = activeCategory === "Todos" || p.category === activeCategory;
      const matchSearch = p.name.toLowerCase().includes(search.toLowerCase());
      return matchCat && matchSearch;
    });
  }, [products, search, activeCategory]);

  return (
    <div className="store-page">
      {/* Search bar */}
      <div className="store-search-wrap">
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Buscar productos..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="search-input"
          />
        </div>
      </div>

      <div className="store-layout">
        {/* Sidebar categories */}
        <aside className="store-sidebar">
          <h3>Categorías</h3>
          <ul className="category-list">
            {CATEGORIES.map((cat) => (
              <li key={cat}>
                <button
                  className={`category-btn ${activeCategory === cat ? "active" : ""}`}
                  onClick={() => setActiveCategory(cat)}
                >
                  {cat}
                </button>
              </li>
            ))}
          </ul>
        </aside>

        {/* Products grid */}
        <main className="store-main">
          <h2 className="section-title">Nuestros Productos</h2>

          {loading ? (
            <div className="loading-grid">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="skeleton-card" />
              ))}
            </div>
          ) : filtered.length === 0 ? (
            <div className="no-results">
              <p>😕 No se encontraron productos</p>
              <button onClick={() => { setSearch(""); setActiveCategory("Todos"); }}>
                Limpiar filtros
              </button>
            </div>
          ) : (
            <div className="products-grid">
              {filtered.map((product) => (
                <ProductCard
                  key={product.product_id}
                  product={product}
                  onAddToCart={onAddToCart}
                />
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}