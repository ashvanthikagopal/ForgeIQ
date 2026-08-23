export function formatNumber(num) {
  if (num === null || num === undefined) return '0';
  return new Intl.NumberFormat().format(num);
}

export function formatPercent(value, total) {
  if (!total) return '0%';
  const pct = Math.round((value / total) * 100);
  return `${pct}%`;
}

export function formatConfidence(score) {
  if (score === null || score === undefined || isNaN(score)) return '0%';
  return `${Math.round(score * 100)}%`;
}

export function formatDate(dateString) {
  if (!dateString) return '-';
  try {
    return new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  } catch (e) {
    return dateString;
  }
}
