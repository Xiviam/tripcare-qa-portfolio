from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(128))
    full_name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(40), index=True)
    active: Mapped[bool] = mapped_column(default=True)

    bookings: Mapped[list[Booking]] = relationship(back_populates="owner")


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    pnr: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    last_name: Mapped[str] = mapped_column(String(80), index=True)
    status: Mapped[str] = mapped_column(String(40), index=True)
    contact_email: Mapped[str] = mapped_column(String(255))
    contact_phone: Mapped[str] = mapped_column(String(40))
    timezone: Mapped[str] = mapped_column(String(80))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    owner: Mapped[User] = relationship(back_populates="bookings")
    passengers: Mapped[list[Passenger]] = relationship(
        back_populates="booking", cascade="all, delete-orphan"
    )
    flights: Mapped[list[Flight]] = relationship(
        back_populates="booking", cascade="all, delete-orphan"
    )
    baggage: Mapped[list[Baggage]] = relationship(
        back_populates="booking", cascade="all, delete-orphan"
    )
    refunds: Mapped[list[Refund]] = relationship(
        back_populates="booking", cascade="all, delete-orphan"
    )
    tickets: Mapped[list[SupportTicket]] = relationship(
        back_populates="booking", cascade="all, delete-orphan"
    )


class Passenger(Base):
    __tablename__ = "passengers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"))
    first_name: Mapped[str] = mapped_column(String(80))
    last_name: Mapped[str] = mapped_column(String(80))
    passenger_type: Mapped[str] = mapped_column(String(20))
    seat: Mapped[str] = mapped_column(String(8))

    booking: Mapped[Booking] = relationship(back_populates="passengers")


class Flight(Base):
    __tablename__ = "flights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"))
    flight_no: Mapped[str] = mapped_column(String(12))
    origin: Mapped[str] = mapped_column(String(8))
    destination: Mapped[str] = mapped_column(String(8))
    depart_at: Mapped[str] = mapped_column(String(40))
    arrive_at: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(40))

    booking: Mapped[Booking] = relationship(back_populates="flights")


class Baggage(Base):
    __tablename__ = "baggage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"))
    passenger_name: Mapped[str] = mapped_column(String(160))
    pieces: Mapped[int] = mapped_column(Integer)
    weight_kg: Mapped[int] = mapped_column(Integer)
    price_cents: Mapped[int] = mapped_column(Integer)

    booking: Mapped[Booking] = relationship(back_populates="baggage")


class Refund(Base):
    __tablename__ = "refunds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"))
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="refund_pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    booking: Mapped[Booking] = relationship(back_populates="refunds")


class KnowledgeArticle(Base):
    __tablename__ = "knowledge_articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(160))
    body: Mapped[str] = mapped_column(Text)
    tags: Mapped[str] = mapped_column(String(160))


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    booking_id: Mapped[int | None] = mapped_column(ForeignKey("bookings.id"), nullable=True)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    subject: Mapped[str] = mapped_column(String(180))
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="open")
    severity: Mapped[str] = mapped_column(String(20), default="medium")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    booking: Mapped[Booking | None] = relationship(back_populates="tickets")
    created_by: Mapped[User] = relationship()


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_email: Mapped[str] = mapped_column(String(255))
    action: Mapped[str] = mapped_column(String(120))
    entity_type: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
