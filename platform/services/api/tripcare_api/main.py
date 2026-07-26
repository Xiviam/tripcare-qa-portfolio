from __future__ import annotations

import re
from typing import Annotated

from fastapi import Depends, FastAPI, Query, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session, selectinload

from .bug_mode import bug_enabled
from .database import Base, engine, get_db
from .errors import ApiError, api_error_handler, validation_error_handler
from .models import AuditLog, Baggage, Booking, KnowledgeArticle, Refund, SupportTicket, User
from .schemas import (
    ArticleRead,
    AuditRead,
    BaggageCreate,
    BaggageRead,
    BookingDetails,
    BookingSummary,
    ContactUpdate,
    LoginRequest,
    RefundCreate,
    RefundRead,
    TicketCreate,
    TicketRead,
    TokenResponse,
    UserRead,
)
from .security import create_access_token, get_current_user, require_roles, verify_password
from .seed import seed_demo_data

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^\+?[0-9]{10,15}$")


def create_app() -> FastAPI:
    app = FastAPI(title="TripCare QA Platform", version="1.0.0")
    app.add_exception_handler(ApiError, api_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def on_startup() -> None:
        Base.metadata.create_all(bind=engine)
        with next(get_db()) as db:
            seed_demo_data(db)

    @app.get("/health")
    def health(db: Session = Depends(get_db)) -> dict:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "ok"}

    @app.post("/auth/login", response_model=TokenResponse)
    def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
        user = db.scalar(select(User).where(User.email == payload.email, User.active.is_(True)))
        if user is None or not verify_password(payload.password, user.password_hash):
            raise ApiError(401, "INVALID_CREDENTIALS", "Email or password is incorrect")
        return TokenResponse(access_token=create_access_token(user))

    @app.get("/auth/me", response_model=UserRead)
    def me(user: Annotated[User, Depends(get_current_user)]) -> User:
        return user

    @app.get("/bookings/search", response_model=list[BookingSummary])
    def search_bookings(
        pnr: str = Query(min_length=3, max_length=12),
        last_name: str = Query(min_length=2, max_length=80),
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> list[Booking]:
        query = select(Booking).where(func.upper(Booking.pnr) == pnr.strip().upper())
        if not bug_enabled("BUG-008"):
            query = query.where(func.lower(Booking.last_name) == last_name.strip().lower())
        if user.role == "customer":
            query = query.where(Booking.owner_id == user.id)
        return list(db.scalars(query).all())

    def load_booking_or_404(booking_id: int, db: Session, user: User) -> Booking:
        query = (
            select(Booking)
            .options(
                selectinload(Booking.passengers),
                selectinload(Booking.flights),
                selectinload(Booking.baggage),
                selectinload(Booking.refunds),
                selectinload(Booking.tickets),
            )
            .where(Booking.id == booking_id)
        )
        if user.role == "customer":
            query = query.where(Booking.owner_id == user.id)
        booking = db.scalar(query)
        if booking is None:
            raise ApiError(404, "BOOKING_NOT_FOUND", "Booking was not found")
        return booking

    @app.get("/bookings/{booking_id}", response_model=BookingDetails)
    def booking_details(
        booking_id: int,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> Booking:
        return load_booking_or_404(booking_id, db, user)

    @app.patch("/bookings/{booking_id}/contacts", response_model=BookingSummary)
    def update_contacts(
        booking_id: int,
        payload: ContactUpdate,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> Booking:
        booking = load_booking_or_404(booking_id, db, user)
        if not bug_enabled("BUG-001") and not EMAIL_RE.match(payload.email.strip()):
            raise ApiError(422, "INVALID_EMAIL", "Email must use a valid format")
        if not bug_enabled("BUG-009") and not PHONE_RE.match(payload.phone.strip()):
            raise ApiError(422, "INVALID_PHONE", "Phone must contain 10 to 15 digits")
        booking.contact_email = payload.email.strip()
        booking.contact_phone = payload.phone.strip()
        db.add(
            AuditLog(
                actor_email=user.email,
                action="update_contacts",
                entity_type="booking",
                entity_id=booking.pnr,
            )
        )
        db.commit()
        db.refresh(booking)
        return booking

    @app.post(
        "/bookings/{booking_id}/baggage",
        status_code=status.HTTP_201_CREATED,
        response_model=BaggageRead,
    )
    def add_baggage(
        booking_id: int,
        payload: BaggageCreate,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> Baggage:
        booking = load_booking_or_404(booking_id, db, user)
        if bug_enabled("BUG-002"):
            price_cents = payload.pieces * 3000
        else:
            price_cents = 3500 + max(payload.pieces - 1, 0) * 4500
            if payload.weight_kg > 23:
                price_cents += (payload.weight_kg - 23) * 250
        baggage = Baggage(
            booking_id=booking.id,
            passenger_name=payload.passenger_name,
            pieces=payload.pieces,
            weight_kg=payload.weight_kg,
            price_cents=price_cents,
        )
        db.add(baggage)
        if not bug_enabled("BUG-007"):
            db.add(
                AuditLog(
                    actor_email=user.email,
                    action="add_baggage",
                    entity_type="booking",
                    entity_id=booking.pnr,
                )
            )
        db.commit()
        db.refresh(baggage)
        return baggage

    @app.post(
        "/bookings/{booking_id}/refunds",
        status_code=status.HTTP_201_CREATED,
        response_model=RefundRead,
    )
    def create_refund(
        booking_id: int,
        payload: RefundCreate,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> Refund:
        booking = load_booking_or_404(booking_id, db, user)
        active_refund = any(
            refund.status in {"refund_pending", "refunded"} for refund in booking.refunds
        )
        if active_refund and not bug_enabled("BUG-003"):
            raise ApiError(
                409,
                "REFUND_ALREADY_EXISTS",
                "Booking already has an active refund request",
            )
        refund = Refund(booking_id=booking.id, reason=payload.reason, status="refund_pending")
        booking.status = "refund_pending"
        db.add(refund)
        db.add(
            AuditLog(
                actor_email=user.email,
                action="create_refund",
                entity_type="booking",
                entity_id=booking.pnr,
            )
        )
        db.commit()
        db.refresh(refund)
        return refund

    @app.get("/knowledge-base", response_model=list[ArticleRead])
    def knowledge_base(q: str = "", db: Session = Depends(get_db)) -> list[KnowledgeArticle]:
        query = select(KnowledgeArticle)
        needle = q.strip()
        if needle:
            if bug_enabled("BUG-005"):
                query = query.where(
                    KnowledgeArticle.title.contains(needle) | KnowledgeArticle.tags.contains(needle)
                )
            else:
                lower = f"%{needle.lower()}%"
                query = query.where(
                    func.lower(KnowledgeArticle.title).like(lower)
                    | func.lower(KnowledgeArticle.body).like(lower)
                    | func.lower(KnowledgeArticle.tags).like(lower)
                )
        return list(db.scalars(query.order_by(KnowledgeArticle.title)).all())

    @app.post("/support/tickets", status_code=status.HTTP_201_CREATED, response_model=TicketRead)
    def create_ticket(
        payload: TicketCreate,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> SupportTicket:
        if not bug_enabled("BUG-004") and not payload.message.strip():
            raise ApiError(422, "EMPTY_MESSAGE", "Support ticket message is required")
        if payload.booking_id is not None:
            load_booking_or_404(payload.booking_id, db, user)
        ticket = SupportTicket(
            booking_id=payload.booking_id,
            created_by_user_id=user.id,
            subject=payload.subject.strip(),
            message=payload.message.strip(),
            severity=payload.severity,
        )
        db.add(ticket)
        db.add(
            AuditLog(
                actor_email=user.email,
                action="create_ticket",
                entity_type="support_ticket",
                entity_id=payload.subject,
            )
        )
        db.commit()
        db.refresh(ticket)
        return ticket

    @app.get("/support/tickets", response_model=list[TicketRead])
    def list_tickets(
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=10, ge=1, le=50),
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> list[SupportTicket]:
        query = select(SupportTicket).order_by(SupportTicket.id.desc())
        if user.role == "customer":
            query = query.where(SupportTicket.created_by_user_id == user.id)
        if bug_enabled("BUG-010"):
            return list(db.scalars(query).all())
        return list(db.scalars(query.offset((page - 1) * page_size).limit(page_size)).all())

    @app.get("/admin/users", response_model=list[UserRead])
    def admin_users(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> list[User]:
        if user.role != "admin" and not bug_enabled("BUG-006"):
            raise ApiError(403, "FORBIDDEN", "Only admin can list users")
        return list(db.scalars(select(User).order_by(User.id)).all())

    @app.get("/audit-log", response_model=list[AuditRead])
    def audit_log(
        _user: User = Depends(require_roles("support_agent", "admin")),
        db: Session = Depends(get_db),
    ) -> list[AuditLog]:
        return list(db.scalars(select(AuditLog).order_by(AuditLog.id.desc()).limit(100)).all())

    return app


app = create_app()
