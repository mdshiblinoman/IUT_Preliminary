"""Pydantic request/response models."""
from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    org_name: str
    username: str
    password: str


class LoginRequest(BaseModel):
    org_name: str
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class RoomCreateRequest(BaseModel):
    name: str
    capacity: int
    hourly_rate_cents: int


class BookingCreateRequest(BaseModel):
    room_id: int
    start_time: str
    end_time: str
