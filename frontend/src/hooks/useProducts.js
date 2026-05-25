import { useState, useEffect } from "react";
import { getProducts } from "../api/ecommerceApi";

export function useProducts() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getProducts()
      .then((data) => {
        setProducts(Array.isArray(data) ? data : []);
      })
      .catch(() => {
        setProducts([]);
        setError("No se encontraron productos");
      })
      .finally(() => setLoading(false));
  }, []);

  return { products, loading, error };
}