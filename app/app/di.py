import os
from app.infrastructure.db import MongoDB
from app.adapters.repo.mongo_repo import MongoRepository
from app.usecase.services import MovieService, BookingService, AuthService

def create_container():
    mongo_uri = os.getenv("MONGO_URI")
    dbname = os.getenv("DB_NAME", "moviebookingdb")
    db = MongoDB(mongo_uri, dbname)
    repo = MongoRepository(db)
    auth = AuthService()
    movie_service = MovieService(repo)
    booking_service = BookingService(repo)
    return {
        "db": db,
        "repo": repo,
        "auth": auth,
        "movie_service": movie_service,
        "booking_service": booking_service
    }
