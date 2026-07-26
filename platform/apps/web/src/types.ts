export type User = {
  id: number;
  email: string;
  full_name: string;
  role: "customer" | "support_agent" | "admin";
  active: boolean;
};

export type BookingSummary = {
  id: number;
  pnr: string;
  last_name: string;
  status: string;
  contact_email: string;
  contact_phone: string;
  timezone: string;
};

export type Passenger = {
  id: number;
  first_name: string;
  last_name: string;
  passenger_type: string;
  seat: string;
};

export type Flight = {
  id: number;
  flight_no: string;
  origin: string;
  destination: string;
  depart_at: string;
  arrive_at: string;
  status: string;
};

export type Baggage = {
  id: number;
  passenger_name: string;
  pieces: number;
  weight_kg: number;
  price_cents: number;
};

export type Refund = {
  id: number;
  reason: string;
  status: string;
  created_at: string;
};

export type Ticket = {
  id: number;
  booking_id: number | null;
  subject: string;
  message: string;
  status: string;
  severity: string;
  created_at: string;
};

export type BookingDetails = BookingSummary & {
  passengers: Passenger[];
  flights: Flight[];
  baggage: Baggage[];
  refunds: Refund[];
  tickets: Ticket[];
};

export type Article = {
  id: number;
  title: string;
  body: string;
  tags: string;
};
