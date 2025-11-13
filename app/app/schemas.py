from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.domain.models import Seat

class MovieCreate(BaseModel):
    title: str
    duration_min: int
    description: str = ""

class ScreeningCreate(BaseModel):
    movie_id: str
    start_time: datetime
    hall: str
    seats_total: int

class BookingCreate(BaseModel):
    screening_id: str
    user_email: str
    seats: List[Seat]

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
