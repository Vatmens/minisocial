from motor.motor_asyncio import AsyncIOMotorClient
import os
from app.core.config import MONGO_URL, MONGO_DB_NAME


client = AsyncIOMotorClient(MONGO_URL)
mongo_db = client[MONGO_DB_NAME]

def get_mongo_db():
    return mongo_db