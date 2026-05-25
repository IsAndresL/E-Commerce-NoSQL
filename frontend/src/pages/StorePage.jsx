import { useMemo, useState, useEffect } from "react";
import ProductCard from "../components/ProductCard";
import { useProducts } from "../hooks/useProducts";
import { CATEGORIES, formatCOP } from "../utils/formatters";
import { getMerchandising } from "../utils/merchandising";

const BANNERS = {
  Todos: [
    { image: "https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?w=1200&h=300&fit=crop", title: "Te damos el primer envío gratis" },
    { image: "https://images.unsplash.com/photo-1516738901601-b53f3cc2c192?w=1200&h=300&fit=crop", title: "Compra con confianza" },
  ],
  Tecnología: [
    { image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=1200&h=300&fit=crop", title: "Devoluciones gratis en 30 días" },
    { image: "https://images.unsplash.com/photo-1633356122544-f134324ef6db?w=1200&h=300&fit=crop", title: "Compra 0% de interés" },
  ],
  Ropa: [
    { image: "https://images.unsplash.com/photo-1556821552-107d12c6b9fe?w=1200&h=300&fit=crop", title: "Última colección llegó" },
    { image: "https://images.unsplash.com/photo-1521595046-a52adf3a0a6e?w=1200&h=300&fit=crop", title: "Descuentos hasta 50%" },
  ],
  Hogar: [
    { image: "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1200&h=300&fit=crop", title: "Decora tu espacio" },
    { image: "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=1200&h=300&fit=crop", title: "Envío gratis hoy" },
  ],
};

export default function StorePage({ onAddToCart, cartItems = [], initialSearch = "", onSearchChange }) {
  const { products, loading } = useProducts();
  const [search, setSearch] = useState(initialSearch);
  const [activeCategory, setActiveCategory] = useState("Todos");
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [currentBannerIndex, setCurrentBannerIndex] = useState(0);

  // Sincronizar búsqueda con navbar
  useEffect(() => {
    setSearch(initialSearch);
  }, [initialSearch]);

  const enrichedProducts = useMemo(() => {
    return products.map((product) => ({ ...product, merch: getMerchandising(product) }));
  }, [products]);

  // Autorotate banners every 5 seconds
  useEffect(() => {
    const banners = BANNERS[activeCategory] || [];
    if (banners.length <= 1) return;
    const timer = setInterval(() => {
      setCurrentBannerIndex((prev) => (prev + 1) % banners.length);
    }, 5000);
    return () => clearInterval(timer);
  }, [activeCategory]);

  // Reset banner index when category changes
  useEffect(() => {
    setCurrentBannerIndex(0);
  }, [activeCategory]);

  const filtered = useMemo(() => {
    return enrichedProducts.filter((product) => {
      const matchCat = activeCategory === "Todos" || product.category === activeCategory;
      const matchSearch = [product.name, product.category].join(" ").toLowerCase().includes(search.toLowerCase());
      return matchCat && matchSearch;
    });
  }, [enrichedProducts, search, activeCategory]);

  return (
    <div className="store-page">
      {/* Category Selector */}
      <div className="category-selector">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            className={`category-select-btn ${activeCategory === cat ? "active" : ""}`}
            onClick={() => setActiveCategory(cat)}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Banner Carousel */}
      <div className="banner-carousel">
        {(BANNERS[activeCategory] || []).length > 0 && (
          <>
            <img
              src={BANNERS[activeCategory][currentBannerIndex]?.image}
              alt={BANNERS[activeCategory][currentBannerIndex]?.title}
              className="banner-image"
            />
            <div className="banner-overlay">
              <h2>{BANNERS[activeCategory][currentBannerIndex]?.title}</h2>
            </div>
            <div className="carousel-dots">
              {(BANNERS[activeCategory] || []).map((_, idx) => (
                <button
                  key={idx}
                  className={`dot ${idx === currentBannerIndex ? "active" : ""}`}
                  onClick={() => setCurrentBannerIndex(idx)}
                />
              ))}
            </div>
            <button
              className="carousel-nav prev"
              onClick={() =>
                setCurrentBannerIndex(
                  (prev) =>
                    (prev - 1 + (BANNERS[activeCategory]?.length || 1)) %
                    (BANNERS[activeCategory]?.length || 1)
                )
              }
            >
              ‹
            </button>
            <button
              className="carousel-nav next"
              onClick={() =>
                setCurrentBannerIndex((prev) => (prev + 1) % (BANNERS[activeCategory]?.length || 1))
              }
            >
              ›
            </button>
          </>
        )}
      </div>

      {/* Products Grid */}
      <div className="store-main">
        <h2 className="section-title">
          {activeCategory === "Todos" ? "Todos nuestros productos" : `Categoría: ${activeCategory}`}
        </h2>
        <div className="catalog-stats">
          <span>{filtered.length} resultados</span>
          <span>{cartItems.length} en carrito</span>
        </div>

        {loading ? (
          <div className="loading-grid">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="skeleton-card" />
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="no-results">
            <p>😕 No se encontraron productos</p>
            <button
              onClick={() => {
                setSearch("");
                setActiveCategory("Todos");
              }}
            >
              Limpiar búsqueda
            </button>
          </div>
        ) : (
          <div className="products-grid">
            {filtered.map((product) => (
              <ProductCard
                key={product.product_id}
                product={product}
                onAddToCart={onAddToCart}
                onViewDetails={() => setSelectedProduct(product)}
                onBuyNow={() => {
                  onAddToCart(product);
                  setSelectedProduct(product);
                }}
              />
            ))}
          </div>
        )}
      </div>

      {selectedProduct && (
        <div className="product-modal-overlay" onClick={() => setSelectedProduct(null)}>
          <section className="product-modal" onClick={(event) => event.stopPropagation()}>
            <button className="modal-close" onClick={() => setSelectedProduct(null)}>✕</button>
            <div className="product-modal-media">
              <img src={selectedProduct.image_url} alt={selectedProduct.name} />
              <div className="media-caption">
                <span>{selectedProduct.merch.videoLabel}</span>
                <strong>Imágenes en contexto real y vista rápida del producto</strong>
              </div>
            </div>
            <div className="product-modal-body">
              <p className="product-category">{selectedProduct.category}</p>
              <h2>{selectedProduct.name}</h2>
              <div className="product-rating-row">
                <span>⭐ {selectedProduct.merch.rating}</span>
                <span>{selectedProduct.merch.reviews} reseñas</span>
                <span>{selectedProduct.stock > 0 ? `Stock ${selectedProduct.stock}` : "Sin stock"}</span>
              </div>
              <p className="product-description">{selectedProduct.description}</p>
              <div className="product-highlights">
                {selectedProduct.merch.features.map((feature) => (
                  <span key={feature}>{feature}</span>
                ))}
              </div>
              <div className="detail-grid">
                <div>
                  <span className="detail-label">Color sugerido</span>
                  <strong>{selectedProduct.merch.featuredColor}</strong>
                </div>
                <div>
                  <span className="detail-label">Talla / formato</span>
                  <strong>{selectedProduct.merch.featuredSize}</strong>
                </div>
                <div>
                  <span className="detail-label">Uso recomendado</span>
                  <strong>{selectedProduct.merch.useCase}</strong>
                </div>
              </div>
              <div className="product-modal-actions">
                <button className="btn-primary-strong" onClick={() => { onAddToCart(selectedProduct); setSelectedProduct(null); }}>
                  Añadir al carrito
                </button>
                <button className="btn-secondary" onClick={() => { onAddToCart(selectedProduct); setSelectedProduct(null); }}>
                  Comprar ahora
                </button>
              </div>
              <div className="trust-band">
                <span>Checkout simplificado</span>
                <span>ePayco · Mercado Pago · PayU</span>
                <span>Pago seguro</span>
              </div>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}