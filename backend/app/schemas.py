from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class Credentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TripInput(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    destination: str = Field(min_length=1, max_length=200)
    starts_on: date
    ends_on: date

    @model_validator(mode="after")
    def dates_in_order(self):
        if self.ends_on < self.starts_on:
            raise ValueError("ends_on must be on or after starts_on")
        return self


class TripPatch(BaseModel):
    title: str = Field(default=None, min_length=1, max_length=160)
    destination: str = Field(default=None, min_length=1, max_length=200)
    starts_on: date = None
    ends_on: date = None

    @model_validator(mode="after")
    def patch_is_not_empty(self):
        if not self.model_fields_set:
            raise ValueError("at least one field is required")
        return self


class TripResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    destination: str
    starts_on: date
    ends_on: date
