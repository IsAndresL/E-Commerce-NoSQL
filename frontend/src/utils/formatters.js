export function money(value) {
  if (value === null || value === undefined || value === '') {
    return '$0'
  }

  if (typeof value === 'number') {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(value)
  }

  const text = String(value)
  return text.startsWith('$') ? text : `$${text}`
}

export function statusTone(status) {
  const normalized = String(status || '').toLowerCase()

  if (normalized.includes('pago')) {
    return 'tone-success'
  }

  if (normalized.includes('enviado')) {
    return 'tone-warning'
  }

  return 'tone-neutral'
}
