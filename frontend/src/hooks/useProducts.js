import { useCallback, useEffect, useState } from "react";
import { getProductCategories, getProducts } from "../api/ecommerceApi";

export function useProducts({ category = "", search = "", limit = 12 } = {}) {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [nextCursor, setNextCursor] = useState("");
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState(null);

  const fetchProducts = useCallback(
    async ({ cursor = "", append = false } = {}) => {
      if (append) {
        setLoadingMore(true);
      } else {
        setLoading(true);
      }
      setError(null);

      try {
        const data = await getProducts({
          category,
          search,
          limit,
          cursor,
        });
        const items = Array.isArray(data) ? data : data.items || [];
        setProducts((prev) => (append ? [...prev, ...items] : items));
        setNextCursor(Array.isArray(data) ? "" : data.next_cursor || "");
      } catch {
        if (!append) setProducts([]);
        setError("No se encontraron productos");
      } finally {
        setLoading(false);
        setLoadingMore(false);
      }
    },
    [category, limit, search]
  );

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  useEffect(() => {
    getProductCategories()
      .then((data) => setCategories(Array.isArray(data) ? data : []))
      .catch(() => setCategories([]));
  }, []);

  const loadMore = useCallback(() => {
    if (!nextCursor || loadingMore) return;
    fetchProducts({ cursor: nextCursor, append: true });
  }, [fetchProducts, loadingMore, nextCursor]);

  return { products, categories, loading, loadingMore, error, nextCursor, loadMore };
}
