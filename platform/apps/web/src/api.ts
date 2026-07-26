import type { Article, Baggage, BookingDetails, BookingSummary, Ticket, User } from "./types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

type ApiError = {
  error?: {
    code: string;
    message: string;
  };
};

async function request<T>(path: string, options: RequestInit = {}, token?: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });
  if (!response.ok) {
    const payload = (await response.json().catch(() => ({}))) as ApiError;
    throw new Error(payload.error?.message ?? `HTTP ${response.status}`);
  }
  return (await response.json()) as T;
}

export async function login(email: string, password: string): Promise<string> {
  const data = await request<{ access_token: string }>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  return data.access_token;
}

export const api = {
  me: (token: string) => request<User>("/auth/me", {}, token),
  searchBookings: (token: string, pnr: string, lastName: string) =>
    request<BookingSummary[]>(
      `/bookings/search?pnr=${encodeURIComponent(pnr)}&last_name=${encodeURIComponent(lastName)}`,
      {},
      token,
    ),
  booking: (token: string, id: number) => request<BookingDetails>(`/bookings/${id}`, {}, token),
  updateContacts: (token: string, id: number, email: string, phone: string) =>
    request<BookingSummary>(
      `/bookings/${id}/contacts`,
      { method: "PATCH", body: JSON.stringify({ email, phone }) },
      token,
    ),
  addBaggage: (token: string, id: number, passengerName: string, pieces: number, weightKg: number) =>
    request<Baggage>(
      `/bookings/${id}/baggage`,
      {
        method: "POST",
        body: JSON.stringify({ passenger_name: passengerName, pieces, weight_kg: weightKg }),
      },
      token,
    ),
  createRefund: (token: string, id: number, reason: string) =>
    request(`/bookings/${id}/refunds`, { method: "POST", body: JSON.stringify({ reason }) }, token),
  articles: (q: string) => request<Article[]>(`/knowledge-base?q=${encodeURIComponent(q)}`),
  tickets: (token: string) => request<Ticket[]>("/support/tickets?page=1&page_size=10", {}, token),
  createTicket: (
    token: string,
    bookingId: number | null,
    subject: string,
    message: string,
    severity: string,
  ) =>
    request<Ticket>(
      "/support/tickets",
      { method: "POST", body: JSON.stringify({ booking_id: bookingId, subject, message, severity }) },
      token,
    ),
  users: (token: string) => request<User[]>("/admin/users", {}, token),
};
