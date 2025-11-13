from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid id")
        return ObjectId(v)
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class Seat(BaseModel):
    row: int
    number: int

class Movie(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str
    duration_min: int
    description: Optional[str]

class Screening(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    movie_id: str
    start_time: datetime
    hall: str
    seats_total: int

class Booking(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    screening_id: str
    user_email: str
    seats: List[Seat]
    created_at: datetime = Field(default_factory=datetime.utcnow)
