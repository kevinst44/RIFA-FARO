from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class ParticipantStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class ParticipantResponse(BaseModel):
    id: str
    nombre: str
    cedula: str
    celular: str
    payment_image_url: str
    status: ParticipantStatus
    ticket_number: Optional[int] = None
    created_at: datetime


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
