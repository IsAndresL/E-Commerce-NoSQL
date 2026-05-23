import { formatCOP } from "../utils/formatters";

export default function ProductCard({ product, onAddToCart }) {
  const outOfStock = product.stock === 0;

  return (
    <div className={`product-card ${outOfStock ? "out-of-stock" : ""}`}>
      <div className="product-img-wrap">
        <img
          src={product.image_url || `https://via.placeholder.com/280x200?text=${encodeURIComponent(product.name)}`}
          alt={product.name}
          className="product-img"
          loading="lazy"
        />
        {outOfStock && <span className="badge-sold-out">Sin stock</span>}
        {product.stock > 0 && product.stock <= 5 && (
          <span className="badge-low-stock">¡Últimas {product.stock}!</span>
        )}
      </div>

      <div className="product-info">
        <p className="product-category">{product.category}</p>
        <h3 className="product-name">{product.name}</h3>
        <p className="product-price">{formatCOP(product.price)}</p>
        <p className="product-stock">Stock: {product.stock}</p>

        <button
          className="btn-add-cart"
          disabled={outOfStock}
          onClick={() => onAddToCart(product)}
        >
          {outOfStock ? "Sin disponibilidad" : "Añadir al Carrito"}
        </button>
      </div>
    </div>
  );
}