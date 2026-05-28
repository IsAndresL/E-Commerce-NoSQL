import { formatCOP } from "../utils/formatters";
import { getMerchandising } from "../utils/merchandising";
import { IconStar } from "./icons/Icons";

export default function ProductCard({ product, onAddToCart, onViewDetails, onBuyNow }) {
  const outOfStock = product.stock === 0;
  const merch = product.merch || getMerchandising(product);

  return (
    <article className={`product-card ${outOfStock ? "out-of-stock" : ""}`}>
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
        <div className="product-meta-line">
          <span><IconStar className="rating-star" /> {merch.rating}</span>
          <span>{merch.reviews} reseñas</span>
        </div>
        <div className="product-attributes">
          <span>{merch.featuredColor}</span>
          <span>{merch.featuredSize}</span>
        </div>

        <div className="product-actions">
          <button className="btn-link" onClick={() => onViewDetails?.(product)}>Ver detalle</button>
          <button
            className="btn-add-cart"
            disabled={outOfStock}
            onClick={() => onAddToCart(product)}
          >
            {outOfStock ? "Sin disponibilidad" : "Añadir al carrito"}
          </button>
          <button
            className="btn-buy-now"
            disabled={outOfStock}
            onClick={() => onBuyNow?.(product)}
          >
            Comprar ahora
          </button>
        </div>
      </div>
    </article>
  );
}