export function formatPercent(value) {
  return `${(value * 100).toFixed(1)}%`;
}

export function formatNumber(value) {
  return new Intl.NumberFormat("en-US").format(value);
}

export function formatDays(value) {
  return `${Math.round(value)} days`;
}