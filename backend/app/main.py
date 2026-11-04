import os
from uuid import UUID

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Trip, User
from app.db.session import get_db
from app.schemas import AuthResponse, Credentials, TripInput, TripPatch, TripResponse, UserResponse
from app.security import create_access_token, decode_access_token, get_secret, password_hash


cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:8081").split(",")
    if origin.strip()
]
if not cors_origins or "*" in cors_origins:
    raise RuntimeError("CORS_ORIGINS must contain explicit origins")

app = FastAPI(title="TripRescue API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
bearer = HTTPBearer(auto_error=False)


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Bearer token required")
    try:
        user_id = decode_access_token(credentials.credentials)
    except (jwt.PyJWTError, ValueError, KeyError, RuntimeError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token") from None
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    return user


def trip_or_404(db: Session, trip_id: UUID, user_id: UUID) -> Trip:
    trip = db.scalar(select(Trip).where(Trip.id == trip_id, Trip.user_id == user_id))
    if trip is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Trip not found")
    return trip


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: Credentials, db: Session = Depends(get_db)) -> AuthResponse:
    get_secret()
    user = User(email=str(payload.email), password_hash=password_hash.hash(payload.password))
    db.add(user)
    try:
        db.flush()
        token = create_access_token(user.id)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists") from None
    db.refresh(user)
    return AuthResponse(access_token=token, user=UserResponse.model_validate(user))


@app.post("/auth/login", response_model=AuthResponse)
def login(payload: Credentials, db: Session = Depends(get_db)) -> AuthResponse:
    user = db.scalar(select(User).where(User.email == str(payload.email)))
    if user is None or not password_hash.verify(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    return AuthResponse(access_token=create_access_token(user.id), user=UserResponse.model_validate(user))


@app.get("/trips", response_model=list[TripResponse])
def list_trips(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[Trip]:
    return list(db.scalars(select(Trip).where(Trip.user_id == user.id).order_by(Trip.starts_on, Trip.id)))


@app.post("/trips", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def create_trip(payload: TripInput, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Trip:
    trip = Trip(user_id=user.id, **payload.model_dump())
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


@app.get("/trips/{trip_id}", response_model=TripResponse)
def get_trip(trip_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Trip:
    return trip_or_404(db, trip_id, user.id)


@app.patch("/trips/{trip_id}", response_model=TripResponse)
def update_trip(trip_id: UUID, payload: TripPatch, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Trip:
    trip = trip_or_404(db, trip_id, user.id)
    values = payload.model_dump(exclude_unset=True)
    proposed = {"title": trip.title, "destination": trip.destination, "starts_on": trip.starts_on, "ends_on": trip.ends_on} | values
    try:
        TripInput.model_validate(proposed)
    except ValidationError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="ends_on must be on or after starts_on") from exc
    for field, value in values.items():
        setattr(trip, field, value)
    db.commit()
    db.refresh(trip)
    return trip


@app.delete("/trips/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(trip_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)) -> None:
    trip = trip_or_404(db, trip_id, user.id)
    db.delete(trip)
    db.commit()
