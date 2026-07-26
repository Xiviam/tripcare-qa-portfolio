from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ApiErrorBody(BaseModel):
    code: str
    message: str
    details: dict[str, object] = Field(default_factory=dict)


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: str
    active: bool


class PassengerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    passenger_type: str
    seat: str


class FlightRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    flight_no: str
    origin: str
    destination: str
    depart_at: str
    arrive_at: str
    status: str


class BaggageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    passenger_name: str
    pieces: int
    weight_kg: int
    price_cents: int


class RefundRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reason: str
    status: str
    created_at: datetime


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    booking_id: int | None
    subject: str
    message: str
    status: str
    severity: str
    created_at: datetime


class BookingSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pnr: str
    last_name: str
    status: str
    contact_email: str
    contact_phone: str
    timezone: str


class BookingDetails(BookingSummary):
    passengers: list[PassengerRead]
    flights: list[FlightRead]
    baggage: list[BaggageRead]
    refunds: list[RefundRead]
    tickets: list[TicketRead]


class ContactUpdate(BaseModel):
    email: str
    phone: str


class BaggageCreate(BaseModel):
    passenger_name: str = Field(min_length=2)
    pieces: int = Field(ge=1, le=5)
    weight_kg: int = Field(ge=1, le=45)


class RefundCreate(BaseModel):
    reason: str = Field(min_length=10, max_length=500)


class ArticleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    body: str
    tags: str


class TicketCreate(BaseModel):
    booking_id: int | None = None
    subject: str = Field(min_length=3, max_length=180)
    message: str
    severity: str = Field(default="medium")


class AuditRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor_email: str
    action: str
    entity_type: str
    entity_id: str
    created_at: datetime
