from bson import ObjectId
from typing import List
from app.app.infrastructure.db import mongo

class MongoRepository:
    def __init__(self):
        self.db = mongo.db

    # Movies
    async def create_movie(self, data: dict) -> dict:
        res = await self.db.movies.insert_one(data)
        return await self.db.movies.find_one({"_id": res.inserted_id})

    async def list_movies(self) -> List[dict]:
        cursor = self.db.movies.find()
        return await cursor.to_list(length=100)

    async def get_movie(self, movie_id: str):
        return await self.db.movies.find_one({"_id": ObjectId(movie_id)})

    async def update_movie(self, movie_id: str, patch: dict):
        await self.db.movies.update_one({"_id": ObjectId(movie_id)}, {"$set": patch})
        return await self.get_movie(movie_id)

    async def delete_movie(self, movie_id: str):
        await self.db.movies.delete_one({"_id": ObjectId(movie_id)})
