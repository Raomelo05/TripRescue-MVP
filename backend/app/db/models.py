from datetime import date, datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    and_,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    trips: Mapped[list["Trip"]] = relationship(
        back_populates="user", cascade="all, delete-orphan")


class Trip(Base):
    __tablename__ = "trips"
    __table_args__ = (
        UniqueConstraint("user_id", "id", name="uq_trips_user_id_id"),
        CheckConstraint("ends_on >= starts_on",
                        name="ck_trips_end_on_or_after_start"),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(160))
    destination: Mapped[str] = mapped_column(String(200))
    starts_on: Mapped[date] = mapped_column(Date)
    ends_on: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    user: Mapped[User] = relationship(back_populates="trips")
    segments: Mapped[list["TripSegment"]] = relationship(
        back_populates="trip", cascade="all, delete-orphan")
    commitments: Mapped[list["Commitment"]] = relationship(
        back_populates="trip", cascade="all, delete-orphan")
    incidents: Mapped[list["Incident"]] = relationship(
        back_populates="trip", cascade="all, delete-orphan")
    entries: Mapped[list["TripEntry"]] = relationship(
        back_populates="trip", cascade="all, delete-orphan")


class TripSegment(Base):
    __tablename__ = "trip_segments"
    __table_args__ = (
        ForeignKeyConstraint(["user_id", "trip_id"], [
                             "trips.user_id", "trips.id"], ondelete="CASCADE"),
        UniqueConstraint("trip_id", "position",
                         name="uq_segments_trip_position"),
        CheckConstraint("arrival_at > departure_at",
                        name="ck_segments_arrival_after_departure"),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    trip_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    position: Mapped[int] = mapped_column(Integer)
    origin: Mapped[str] = mapped_column(String(200))
    destination: Mapped[str] = mapped_column(String(200))
    departure_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    arrival_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    carrier: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    reference_code: Mapped[Optional[str]] = mapped_column(
        String(80), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    trip: Mapped[Trip] = relationship(back_populates="segments")


class Commitment(Base):
    __tablename__ = "commitments"
    __table_args__ = (
        ForeignKeyConstraint(["user_id", "trip_id"], [
                             "trips.user_id", "trips.id"], ondelete="CASCADE"),
        CheckConstraint("ends_at > starts_at",
                        name="ck_commitments_end_after_start"),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    trip_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    title: Mapped[str] = mapped_column(String(200))
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    trip: Mapped[Trip] = relationship(back_populates="commitments")


class Incident(Base):
    __tablename__ = "incidents"
    __table_args__ = (
        ForeignKeyConstraint(["user_id", "trip_id"], [
                             "trips.user_id", "trips.id"], ondelete="CASCADE"),
        UniqueConstraint("user_id", "trip_id", "id",
                         name="uq_incidents_user_trip_id"),
        CheckConstraint("status IN ('open', 'resolved', 'archived')",
                        name="ck_incidents_status"),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    trip_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    affected_item: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="open")
    reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now)

    trip: Mapped[Trip] = relationship(back_populates="incidents")
    plans: Mapped[list["ActionPlan"]] = relationship(
        back_populates="incident", cascade="all, delete-orphan")


class ActionPlan(Base):
    __tablename__ = "action_plans"
    __table_args__ = (
        UniqueConstraint("user_id", "trip_id", "id", name="uq_action_plans_user_trip_id"),
        ForeignKeyConstraint(["user_id", "trip_id", "incident_id"], [
                             "incidents.user_id", "incidents.trip_id", "incidents.id"], ondelete="CASCADE"),
        CheckConstraint(
            "status IN ('active', 'completed', 'superseded')", name="ck_action_plans_status"),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    trip_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    incident_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now)

    incident: Mapped[Incident] = relationship(back_populates="plans")
    tasks: Mapped[list["ActionTask"]] = relationship(
        back_populates="plan", cascade="all, delete-orphan")


class ActionTask(Base):
    __tablename__ = "action_tasks"
    __table_args__ = (
        ForeignKeyConstraint(["user_id", "trip_id", "plan_id"], [
                             "action_plans.user_id", "action_plans.trip_id", "action_plans.id"], ondelete="CASCADE"),
        UniqueConstraint("plan_id", "position",
                         name="uq_action_tasks_plan_position"),
        CheckConstraint("priority IN ('urgent', 'high', 'normal', 'low')",
                        name="ck_action_tasks_priority"),
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed', 'skipped')", name="ck_action_tasks_status"),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    trip_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    plan_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    position: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(200))
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rationale: Mapped[str] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(20), default="normal")
    status: Mapped[str] = mapped_column(String(20), default="pending")
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now)

    plan: Mapped[ActionPlan] = relationship(back_populates="tasks")


class TripEntry(Base):
    __tablename__ = "trip_entries"
    __table_args__ = (
        ForeignKeyConstraint(["user_id", "trip_id"], [
                             "trips.user_id", "trips.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["user_id", "trip_id", "incident_id"], [
                             "incidents.user_id", "incidents.trip_id", "incidents.id"], ondelete="CASCADE"),
        CheckConstraint(
            "entry_type IN ('note', 'protocol', 'history')", name="ck_trip_entries_type"),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    trip_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    incident_id: Mapped[Optional[UUID]] = mapped_column(
        Uuid(as_uuid=True), nullable=True, index=True)
    entry_type: Mapped[str] = mapped_column(String(20))
    title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now)

    trip: Mapped[Trip] = relationship(back_populates="entries")
    incident: Mapped[Optional[Incident]] = relationship(
        primaryjoin=lambda: and_(
            Incident.id == foreign(TripEntry.incident_id),
            Incident.user_id == TripEntry.user_id,
            Incident.trip_id == TripEntry.trip_id,
        )
    )
