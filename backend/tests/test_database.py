from datetime import date, datetime
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models import Trip, TripSegment, User


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, _connection_record):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    with Session(engine) as db_session:
        yield db_session
    Base.metadata.drop_all(engine)
    engine.dispose()


def test_trip_requires_existing_owner(session: Session):
    trip = Trip(
        user_id=uuid4(),
        title="Fim de semana",
        destination="Recife",
        starts_on=date(2026, 12, 1),
        ends_on=date(2026, 12, 4),
    )
    session.add(trip)

    with pytest.raises(IntegrityError):
        session.commit()


def test_user_owns_trip(session: Session):
    user = User(email="pessoa@example.com", password_hash="hash")
    trip = Trip(
        user=user,
        title="Fim de semana",
        destination="Recife",
        starts_on=date(2026, 12, 1),
        ends_on=date(2026, 12, 4),
    )
    session.add(trip)
    session.commit()

    assert trip.user_id == user.id
    assert user.trips == [trip]


def test_trip_segment_cannot_cross_user_boundary(session: Session):
    owner = User(email="owner@example.com", password_hash="hash")
    other_user = User(email="other@example.com", password_hash="hash")
    trip = Trip(
        user=owner,
        title="Fim de semana",
        destination="Recife",
        starts_on=date(2026, 12, 1),
        ends_on=date(2026, 12, 4),
    )
    session.add_all([owner, other_user, trip])
    session.flush()

    segment = TripSegment(
        user_id=other_user.id,
        trip_id=trip.id,
        position=0,
        origin="Sao Paulo",
        destination="Recife",
        departure_at=datetime(2026, 12, 1, 9),
        arrival_at=datetime(2026, 12, 1, 12),
    )
    session.add(segment)

    with pytest.raises(IntegrityError):
        session.commit()


def test_trip_end_date_cannot_precede_start_date(session: Session):
    trip = Trip(
        user=User(email="dates@example.com", password_hash="hash"),
        title="Datas inválidas",
        destination="Recife",
        starts_on=date(2026, 12, 4),
        ends_on=date(2026, 12, 1),
    )
    session.add(trip)

    with pytest.raises(IntegrityError):
        session.commit()
