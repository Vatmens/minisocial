import os

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB_NAME = os.getenv("MONGO_NAME")

SECRET_KEY = os.getenv("SECRET_KEY", "insecure_default_key_for_development_only")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
