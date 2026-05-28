import { useCallback, useEffect, useMemo, useState } from "react";

import {
  addCartItem,
  clearCartItems,
  getCart,
  removeCartItem,
  updateCartItem,
} from "../api/ecommerceApi";

function normalizeCart(rawCart = {}) {
  const rawItems = Array.isArray(rawCart.items) ? rawCart.items : [];
  const items = rawItems.map((item) => {
    const unitPrice = Number(item.unit_price ?? item.price ?? 0);
    const quantity = Number(item.quantity ?? 0);
    return {
      ...item,
      price: unitPrice,
      unit_price: unitPrice,
      quantity,
      subtotal: Number(item.subtotal ?? unitPrice * quantity),
      stock_available: Number(item.stock_available ?? 0),
    };
  });

  return {
    items,
    subtotal: Number(rawCart.subtotal ?? items.reduce((sum, item) => sum + item.subtotal, 0)),
    shipping_estimate: Number(rawCart.shipping_estimate ?? 0),
    total_estimate: Number(rawCart.total_estimate ?? 0),
    updated_at: rawCart.updated_at || "",
  };
}

export function useCart(userId) {
  const [items, setItems] = useState([]);
  const [summary, setSummary] = useState(() => normalizeCart());
  const [loading, setLoading] = useState(false);
  const [mutating, setMutating] = useState(false);
  const [error, setError] = useState("");

  const applyCart = useCallback((cart) => {
    const normalized = normalizeCart(cart);
    setItems(normalized.items);
    setSummary(normalized);
    return normalized;
  }, []);

  const refreshCart = useCallback(async () => {
    if (!userId) {
      applyCart();
      return normalizeCart();
    }

    setLoading(true);
    setError("");
    try {
      return applyCart(await getCart(userId));
    } catch (err) {
      setError(err?.message || "No se pudo cargar el carrito.");
      throw err;
    } finally {
      setLoading(false);
    }
  }, [applyCart, userId]);

  useEffect(() => {
    refreshCart().catch(() => {});
  }, [refreshCart]);

  const addToCart = useCallback(async (product, quantity = 1) => {
    if (!userId || !product?.product_id) return null;

    setMutating(true);
    setError("");
    try {
      return applyCart(await addCartItem(userId, product.product_id, quantity));
    } catch (err) {
      setError(err?.message || "No se pudo agregar el producto.");
      throw err;
    } finally {
      setMutating(false);
    }
  }, [applyCart, userId]);

  const removeFromCart = useCallback(async (productId) => {
    if (!userId || !productId) return null;

    setMutating(true);
    setError("");
    try {
      return applyCart(await removeCartItem(userId, productId));
    } catch (err) {
      setError(err?.message || "No se pudo quitar el producto.");
      throw err;
    } finally {
      setMutating(false);
    }
  }, [applyCart, userId]);

  const updateQuantity = useCallback(async (productId, quantity) => {
    if (!userId || !productId) return null;

    setMutating(true);
    setError("");
    try {
      return applyCart(await updateCartItem(userId, productId, quantity));
    } catch (err) {
      setError(err?.message || "No se pudo actualizar la cantidad.");
      throw err;
    } finally {
      setMutating(false);
    }
  }, [applyCart, userId]);

  const clearCart = useCallback(async () => {
    if (!userId) {
      applyCart();
      return normalizeCart();
    }

    setMutating(true);
    setError("");
    try {
      return applyCart(await clearCartItems(userId));
    } catch (err) {
      setError(err?.message || "No se pudo vaciar el carrito.");
      throw err;
    } finally {
      setMutating(false);
    }
  }, [applyCart, userId]);

  const total = summary.subtotal || items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const shipping = summary.shipping_estimate;
  const grandTotal = summary.total_estimate || total + shipping;
  const count = useMemo(() => items.reduce((sum, item) => sum + item.quantity, 0), [items]);

  return {
    items,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    refreshCart,
    total,
    shipping,
    grandTotal,
    count,
    loading,
    mutating,
    error,
    updatedAt: summary.updated_at,
  };
}
