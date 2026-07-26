from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (
    AuditLog,
    Baggage,
    Booking,
    Flight,
    KnowledgeArticle,
    Passenger,
    Refund,
    SupportTicket,
    User,
)
from .security import hash_password


def seed_demo_data(db: Session) -> None:
    if db.scalar(select(User).where(User.email == "customer@example.com")):
        return

    customer = User(
        email="customer@example.com",
        password_hash=hash_password("Customer123!"),
        full_name="Ivan Ivanov",
        role="customer",
    )
    agent = User(
        email="agent@example.com",
        password_hash=hash_password("Agent123!"),
        full_name="Support Agent",
        role="support_agent",
    )
    admin = User(
        email="admin@example.com",
        password_hash=hash_password("Admin123!"),
        full_name="TripCare Admin",
        role="admin",
    )
    db.add_all([customer, agent, admin])
    db.flush()

    rows = [
        ("TC1001", "Ivanov", "confirmed", "Europe/Moscow", 1),
        ("TC1002", "Petrova", "changed", "Europe/Samara", 2),
        ("TC1003", "Smirnov", "cancelled", "Asia/Yekaterinburg", 1),
        ("TC1004", "Kuznetsova", "refund_pending", "Europe/Moscow", 2),
        ("TC1005", "Sokolov", "refunded", "Europe/Kaliningrad", 1),
        ("TC1006", "Popova", "confirmed", "Asia/Novosibirsk", 3),
        ("TC1007", "Lebedev", "changed", "Europe/Moscow", 2),
        ("TC1008", "Kozlova", "confirmed", "Asia/Irkutsk", 1),
        ("TC1009", "Morozov", "cancelled", "Europe/Moscow", 2),
        ("TC1010", "Novikova", "confirmed", "Asia/Vladivostok", 1),
        ("TC1011", "Fedorov", "refund_pending", "Europe/Moscow", 2),
        ("TC1012", "Mikhailova", "refunded", "Europe/Samara", 3),
    ]

    for index, (pnr, last_name, status, timezone, passenger_count) in enumerate(rows, start=1):
        booking = Booking(
            pnr=pnr,
            last_name=last_name,
            status=status,
            contact_email=f"{last_name.lower()}@example.test",
            contact_phone=f"+7999000{index:04d}",
            timezone=timezone,
            owner_id=customer.id,
        )
        db.add(booking)
        db.flush()

        for passenger_index in range(1, passenger_count + 1):
            db.add(
                Passenger(
                    booking_id=booking.id,
                    first_name=f"Passenger{passenger_index}",
                    last_name=last_name,
                    passenger_type="adult" if passenger_index == 1 else "child",
                    seat=f"{10 + passenger_index}{chr(64 + passenger_index)}",
                )
            )

        db.add(
            Flight(
                booking_id=booking.id,
                flight_no=f"TC{600 + index}",
                origin="SVO" if index % 2 else "LED",
                destination="AER" if index % 3 else "KGD",
                depart_at=f"2026-08-{10 + index:02d}T08:30:00{timezone}",
                arrive_at=f"2026-08-{10 + index:02d}T11:10:00{timezone}",
                status="on_time" if status != "cancelled" else "cancelled",
            )
        )

        if index in {2, 7, 12}:
            db.add(
                Baggage(
                    booking_id=booking.id,
                    passenger_name=f"Passenger1 {last_name}",
                    pieces=1,
                    weight_kg=20,
                    price_cents=3500,
                )
            )

        if status in {"refund_pending", "refunded"}:
            db.add(
                Refund(
                    booking_id=booking.id,
                    reason="Passenger requested refund after schedule change",
                    status=status,
                )
            )

        if index in {8, 11, 12}:
            db.add(
                SupportTicket(
                    booking_id=booking.id,
                    created_by_user_id=customer.id,
                    subject="Need help with booking",
                    message="Please clarify baggage and refund options for this trip.",
                    status="open",
                    severity="medium" if index != 11 else "high",
                )
            )

    articles = [
        (
            "How to add baggage",
            "Baggage can be added from the booking details page.",
            "baggage,web,mobile",
        ),
        (
            "Refund status explained",
            "Refund requests move from pending to completed after review.",
            "refund,status",
        ),
        (
            "Contact data rules",
            "Email and phone are validated before they are saved.",
            "contacts,validation",
        ),
        (
            "Offline mobile mode",
            "Mobile shows cached booking state and an error banner offline.",
            "mobile,offline",
        ),
        (
            "Support ticket SLA",
            "Support tickets are prioritized by severity and booking status.",
            "support,sla",
        ),
    ]
    db.add_all(
        [KnowledgeArticle(title=title, body=body, tags=tags) for title, body, tags in articles]
    )
    db.add(
        AuditLog(
            actor_email="system",
            action="seed_demo_data",
            entity_type="database",
            entity_id="demo",
        )
    )
    db.commit()
