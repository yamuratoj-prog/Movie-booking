from app.adapters.repo.mongo_repo import MongoRepository
from app.infrastructure.security import hash_password, verify_password, create_access_token
from datetime import datetime

# In-memory users for demo
class AuthService:
    def __init__(self):
        self.users = {}  # email: hashed

    async def signup(self, email: str, password: str):
        if email in self.users:
            raise ValueError("exists")
        self.users[email] = hash_password(password)
        token = create_access_token(email)
        return token

    async def login(self, email: str, password: str):
        h = self.users.get(email)
        if not h or not verify_password(password, h):
            raise ValueError("invalid")
        return create_access_token(email)

class MovieService:
    def __init__(self, repo: MongoRepository):
        self.repo = repo

    async def create_movie(self, payload: dict):
        return await self.repo.create_movie(payload)

    async def list_movies(self):
        return await self.repo.list_movies()

    async def get_movie(self, movie_id: str):
        return await self.repo.get_movie(movie_id)

    async def update_movie(self, movie_id: str, patch: dict):
        return await self.repo.update_movie(movie_id, patch)

    async def delete_movie(self, movie_id: str):
        await self.repo.delete_movie(movie_id)

class BookingService:
    def __init__(self, repo: MongoRepository):
        self.repo = repo

    async def create_screening(self, payload: dict):
        return await self.repo.create_screening(payload)

    async def list_screenings(self):
        return await self.repo.list_screenings()

    async def book(self, booking_payload: dict):
        # check seat availability
        screenings = await self.repo.get_screening(booking_payload["screening_id"])
        if not screenings:
            raise ValueError("screening_not_found")
        existing = await self.repo.list_bookings_for_screening(booking_payload["screening_id"])
        # flatten occupied seats
        occupied = {(s["row"], s["number"]) for b in existing for s in b["seats"]}
        for s in booking_payload["seats"]:
            if (s["row"], s["number"]) in occupied:
                raise ValueError(f"seat_taken {s}")
        # ok -> create
        booking_payload["created_at"] = datetime.utcnow()
        return await self.repo.create_booking(booking_payload)
