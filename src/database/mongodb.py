from motor.motor_asyncio import AsyncIOMotorClient
from src.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

mongo = MongoDB()

async def connect_to_mongo():
    mongo.client = AsyncIOMotorClient(settings.MONGO_URL)
    mongo.db = mongo.client[settings.MONGO_NAME]
    print("MongoDB connected!")

async def close_mongo_connection():
    if mongo.client:
        mongo.client.close()
        print("MongoDB connection closed.")

def get_mongo_db():
    return mongo.db