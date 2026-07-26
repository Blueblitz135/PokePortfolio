const cadFormatter = new Intl.NumberFormat("en-CA", {
  style: "currency",
  currency: "CAD",
});

const percentFormatter = new Intl.NumberFormat("en-CA", {
  maximumFractionDigits: 1,
});

export function formatCad(value: string | null): string {
  if (value === null) {
    return "—";
  }

  const amount = Number(value);
  return Number.isFinite(amount) ? cadFormatter.format(amount) : "—";
}

export function formatPercent(value: string | null): string {
  if (value === null) {
    return "—";
  }

  const percentage = Number(value);
  return Number.isFinite(percentage)
    ? `${percentFormatter.format(percentage)}%`
    : "—";
}
