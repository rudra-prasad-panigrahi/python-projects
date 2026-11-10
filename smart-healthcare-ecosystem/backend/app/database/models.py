from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import uuid4

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"usr-{uuid4().hex}")
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(80), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    last_name: Mapped[str] = mapped_column(String(80), nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str] = mapped_column(String(32), nullable=False, default="prefer_not_to_say")
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    state: Mapped[str | None] = mapped_column(String(128), nullable=True)
    country: Mapped[str | None] = mapped_column(String(128), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    blood_group: Mapped[str | None] = mapped_column(String(16), nullable=True)
    important_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferred_hospital: Mapped[str | None] = mapped_column(Text, nullable=True)
    emergency_directives: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    profile: Mapped["PersonalProfile"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")


class PersonalProfile(Base):
    __tablename__ = "personal_profiles"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"prof-{uuid4().hex}")
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id"), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    state: Mapped[str | None] = mapped_column(String(128), nullable=True)
    country: Mapped[str | None] = mapped_column(String(128), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    blood_group: Mapped[str | None] = mapped_column(String(16), nullable=True)
    allergies: Mapped[str | None] = mapped_column(Text, default="[]")
    conditions: Mapped[str | None] = mapped_column(Text, default="[]")
    important_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferred_hospital: Mapped[str | None] = mapped_column(Text, nullable=True)
    emergency_directives: Mapped[str | None] = mapped_column(Text, nullable=True)
    emergency_contacts: Mapped[str | None] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped[User] = relationship(back_populates="profile")


class OAuthIdentity(Base):
    __tablename__ = "oauth_identities"
    __table_args__ = (
        UniqueConstraint("provider", "subject", name="uq_oauth_provider_subject"),
        UniqueConstraint("user_id", "provider", name="uq_oauth_user_provider"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"oauth-{uuid4().hex}")
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"evt-{uuid4().hex}")
    user_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
