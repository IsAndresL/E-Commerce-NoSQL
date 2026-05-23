import { useState, useEffect } from "react";
import { getProducts } from "../api/ecommerceApi";

// Mock products for development/demo when API is not available
const MOCK_PRODUCTS = [
  { product_id: "p1", name: "Teléfono Inteligente X100", price: 850000, stock: 15, category: "Electrónica", image_url: "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=300&h=300&fit=crop", description: "Smartphone de última generación" },
  { product_id: "p2", name: "Portátil WorkPro 15", price: 2200000, stock: 8, category: "Electrónica", image_url: "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=300&h=300&fit=crop", description: "Laptop profesional de alto rendimiento" },
  { product_id: "p3", name: "Auriculares Bluetooth Z5", price: 120000, stock: 25, category: "Electrónica", image_url: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop", description: "Sonido premium inalámbrico" },
  { product_id: "p4", name: "Reloj Inteligente FitTrack", price: 350000, stock: 3, category: "Electrónica", image_url: "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300&h=300&fit=crop", description: "Smartwatch deportivo" },
  { product_id: "p5", name: "Mochila de Viaje", price: 90000, stock: 50, category: "Deportes", image_url: "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=300&h=300&fit=crop", description: "Mochila resistente 30L" },
  { product_id: "p6", name: "Camiseta Algodón Hombre", price: 45000, stock: 100, category: "Ropa", image_url: "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=300&h=300&fit=crop", description: "100% algodón orgánico" },
  { product_id: "p7", name: "Lámpara de Escritorio LED", price: 65000, stock: 20, category: "Hogar", image_url: "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=300&h=300&fit=crop", description: "Luz ajustable USB" },
  { product_id: "p8", name: "Teclado Mecánico RGB", price: 280000, stock: 12, category: "Electrónica", image_url: "https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=300&h=300&fit=crop", description: "Switches blue, retroiluminado" },
];

export function useProducts() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getProducts()
      .then((data) => {
        setProducts(Array.isArray(data) ? data : MOCK_PRODUCTS);
      })
      .catch(() => {
        // Fallback to mock data if API is not available
        setProducts(MOCK_PRODUCTS);
        setError(null); // Don't show error when using mock data
      })
      .finally(() => setLoading(false));
  }, []);

  return { products, loading, error };
}