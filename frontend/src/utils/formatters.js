export const formatCOP = (value) =>
  new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);

export const formatDate = (dateStr) => {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  return d.toLocaleDateString("es-CO", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
};

export const statusColor = (status) => {
  const s = (status || "").toLowerCase();
  if (s.includes("exitoso") || s.includes("entregado")) return "status-success";
  if (s.includes("enviado") || s.includes("transito")) return "status-info";
  if (s.includes("cancelado")) return "status-error";
  return "status-pending";
};
