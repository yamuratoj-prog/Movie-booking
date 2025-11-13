from fastapi import APIRouter, Depends, HTTPException, Header
from app.schemas import MovieCreate, ScreeningCreate, BookingCreate, Token
from app.di import create_container
from app.infrastructure.security import decode_token
import os

# Create fresh container per import (simple DI)
container = create_container()
movie_service = container["movie_service"]
booking_service = container["booking_service"]
auth_service = container["auth"]

router = APIRouter()

# Auth endpoints
@router.post("/auth/signup", response_model=Token)
async def signup(body: dict):
    try:
        token = await auth_service.signup(body["email"], body["password"])
        return {"access_token": token}
    except ValueError:
        raise HTTPException(400, "user exists")

@router.post("/auth/login", response_model=Token)
async def login(body: dict):
    try:
        token = await auth_service.login(body["email"], body["password"])
        return {"access_token": token}
    except ValueError:
        raise HTTPException(401, "invalid credentials")

# simple dependency
async def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "missing token")
    token = authorization.split(" ", 1)[1]
    sub = decode_token(token)
    if not sub:
        raise HTTPException(401, "invalid token")
    return sub

# Movies CRUD
@router.post("/movies")
async def create_movie(payload: MovieCreate, user=Depends(get_current_user)):
    return await movie_service.create_movie(payload.dict())

@router.get("/movies")
async def list_movies():
    return await movie_service.list_movies()

@router.get("/movies/{movie_id}")
async def get_movie(movie_id: str):
    m = await movie_service.get_movie(movie_id)
    if not m:
        raise HTTPException(404, "not found")
    return m

@router.put("/movies/{movie_id}")
async def update_movie(movie_id: str, patch: dict, user=Depends(get_current_user)):
    return await movie_service.update_movie(movie_id, patch)

@router.delete("/movies/{movie_id}")
async def delete_movie(movie_id: str, user=Depends(get_current_user)):
    await movie_service.delete_movie(movie_id)
    return {"status": "deleted"}

# Screenings
@router.post("/screenings")
async def create_screening(payload: ScreeningCreate, user=Depends(get_current_user)):
    return await booking_service.create_screening(payload.dict())

@router.get("/screenings")
async def list_screenings():
    return await booking_service.list_screenings()

# Bookings
@router.post("/bookings")
async def create_booking(payload: BookingCreate, user=Depends(get_current_user)):
    try:
        return await booking_service.book(payload.dict())
    except ValueError as e:
        raise HTTPException(400, str(e))
