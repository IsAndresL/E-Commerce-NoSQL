const CATEGORY_PROFILES = {
  Electrónica: {
    colors: ["Negro", "Azul grafito", "Plata"],
    sizes: ["Compacto", "Estándar"],
    features: ["Pantalla premium", "Conectividad rápida", "Garantía oficial"],
    useCase: "Pensado para trabajo, estudio y entretenimiento.",
  },
  Ropa: {
    colors: ["Negro", "Blanco", "Azul marino", "Arena"],
    sizes: ["S", "M", "L", "XL"],
    features: ["Tejido suave", "Ajuste cómodo", "Corte versátil"],
    useCase: "Ideal para looks diarios y combinaciones fáciles.",
  },
  Hogar: {
    colors: ["Gris", "Madera", "Blanco"],
    sizes: ["Pequeño", "Mediano", "Grande"],
    features: ["Uso práctico", "Acabado premium", "Fácil de limpiar"],
    useCase: "Aporta orden, comodidad y sensación de hogar.",
  },
  Deportes: {
    colors: ["Negro", "Verde", "Rojo", "Azul"],
    sizes: ["XS", "S", "M", "L"],
    features: ["Ligero", "Resistente", "Listo para entrenar"],
    useCase: "Diseñado para movimiento, rendimiento y durabilidad.",
  },
  default: {
    colors: ["Negro", "Blanco", "Gris"],
    sizes: ["Único"],
    features: ["Compra segura", "Entrega rápida", "Buen soporte"],
    useCase: "Seleccionado para una compra rápida y sin fricción.",
  },
};

const FEATURE_KEYWORDS = [
  ["pantalla", "Pantalla alta definición"],
  ["cámara", "Cámara destacada"],
  ["batería", "Autonomía extendida"],
  ["bluetooth", "Bluetooth estable"],
  ["mecánico", "Respuesta táctil precisa"],
  ["algodón", "Tela suave"],
  ["fitness", "Listo para entrenar"],
  ["inteligente", "Funciones smart"],
];

function hashText(value) {
  return String(value || "")
    .split("")
    .reduce((total, char) => total + char.charCodeAt(0), 0);
}

function pick(list, seed) {
  if (!Array.isArray(list) || list.length === 0) return null;
  return list[seed % list.length];
}

export function getMerchandising(product) {
  const profile = CATEGORY_PROFILES[product?.category] || CATEGORY_PROFILES.default;
  const seed = hashText(product?.product_id || product?.id || product?.name);
  const rating = Math.min(5, 4.2 + ((seed % 7) * 0.1)).toFixed(1);
  const reviews = 18 + (seed % 142);
  const color = pick(profile.colors, seed);
  const size = pick(profile.sizes, seed + 1);
  const keywordFeature = FEATURE_KEYWORDS.find(([keyword]) => (product?.name || "").toLowerCase().includes(keyword))?.[1];

  return {
    rating,
    reviews,
    colors: profile.colors,
    sizes: profile.sizes,
    featuredColor: color,
    featuredSize: size,
    features: [
      profile.features[0],
      keywordFeature,
      profile.features[1],
      profile.features[2],
    ].filter(Boolean),
    useCase: profile.useCase,
    buyingReasons: ["Compra segura", "Entrega confiable", "Soporte postventa"],
    reviewQuote: "Buena relación entre precio, presentación y entrega.",
    videoLabel: "Vista en uso real",
  };
}

export function buildSmartRecommendations(products, cartItems = []) {
  const catalog = Array.isArray(products) ? products : [];
  const cartIds = new Set((Array.isArray(cartItems) ? cartItems : []).map((item) => item.product_id));
  const cartCategories = new Set((Array.isArray(cartItems) ? cartItems : []).map((item) => item.category));

  return catalog
    .filter((product) => !cartIds.has(product.product_id))
    .map((product) => {
      const merch = getMerchandising(product);
      const categoryBoost = cartCategories.has(product.category) ? 2 : 0;
      const priceBoost = product.price >= 100000 ? 1 : 0;
      return {
        ...product,
        merch,
        score: categoryBoost + priceBoost + Number(merch.rating),
      };
    })
    .sort((a, b) => b.score - a.score || b.price - a.price)
    .slice(0, 4);
}

export function getPriceBounds(products) {
  const prices = (Array.isArray(products) ? products : []).map((product) => Number(product.price) || 0);
  if (prices.length === 0) return { min: 0, max: 0 };
  return { min: Math.min(...prices), max: Math.max(...prices) };
}
