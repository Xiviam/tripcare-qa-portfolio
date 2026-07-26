export function formatMoney(cents: number): string {
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 0,
  }).format(cents / 100);
}

export function baggagePreviewPrice(pieces: number, weightKg: number, bugMode = false): number {
  if (bugMode) {
    return pieces * 3000;
  }
  const base = 3500 + Math.max(pieces - 1, 0) * 4500;
  return base + (weightKg > 23 ? (weightKg - 23) * 250 : 0);
}

export function normalizePnr(value: string, bugMode = false): string {
  return bugMode ? value.toUpperCase() : value.trim().toUpperCase();
}

export function validateContactInput(email: string, phone: string): string[] {
  const errors: string[] = [];
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
    errors.push("Email должен быть в корректном формате");
  }
  if (!/^\+?[0-9]{10,15}$/.test(phone)) {
    errors.push("Телефон должен содержать от 10 до 15 цифр");
  }
  return errors;
}
