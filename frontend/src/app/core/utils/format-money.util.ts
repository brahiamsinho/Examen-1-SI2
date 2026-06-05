const MONEY_FORMATTER = new Intl.NumberFormat('es-BO', {
  style: 'currency',
  currency: 'BOB',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

export function formatMoneyBob(value: string | number | null | undefined): string {
  const n = toNumber(value);
  return MONEY_FORMATTER.format(n);
}

export function toNumber(value: string | number | null | undefined): number {
  if (typeof value === 'number') return value;
  if (!value) return 0;
  const n = Number(value);
  return Number.isFinite(n) ? n : 0;
}

export function formatPct(value: string | number | null | undefined): string {
  return `${toNumber(value).toFixed(2)}%`;
}
