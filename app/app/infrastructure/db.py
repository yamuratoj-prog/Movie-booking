from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError
import os

class MongoDB:
    def __init__(self):
        self.uri = os.getenv("MONGO_URI")
        self.db_name = os.getenv("DB_NAME", "movie_booking")
        self._client = AsyncIOMotorClient(self.uri, tls=True)
        self.db = self._client[self.db_name]

    async def ping(self):
        try:
            await self._client.admin.command("ping")
            return True
        except ServerSelectionTimeoutError:
            return False

# Создаём объект MongoDB
mongo = MongoDB()
