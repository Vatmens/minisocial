import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from src.config import settings
from src.router import api_router
from src.errors import setup_exception_handlers
from src.database.mongodb import connect_to_mongo, close_mongo_connection, get_mongo_db
from src.database.core import close_pg_connection, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()

    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        raise RuntimeError(f"PostgreSQL is not working: {e}")

    try:
        db = get_mongo_db()
        await db.command("ping")
    except Exception as e:
        raise RuntimeError(f"MongoDB is not working: {e}")

    logger = logging.getLogger("uvicorn.access")
    console_formatter = uvicorn.logging.ColourizedFormatter(
        "{asctime} {levelprefix} : {message}", style="{", use_colors=False
    )
    if logger.handlers:
        logger.handlers[0].setFormatter(console_formatter)

    yield


    await close_mongo_connection()
    await close_pg_connection()



if settings.ENVIRONMENT == "dev":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app = FastAPI(
        title="Mini Social API",
        description="backend-сервіс Mini Social API",
        lifespan=lifespan,
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,
            "syntaxHighlight.theme": "arta",
            "displayRequestDuration": True,
            "filter": True
        },
    )
elif settings.ENVIRONMENT == "prod":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '0'
    app = FastAPI(
        docs_url=None,
        redoc_url=None,
        lifespan=lifespan
    )
else:
    raise EnvironmentError("Set correct ENVIRONMENT in .env file. Possible values: 'dev' or 'prod'")


app = FastAPI(
    title="Mini Social API",

    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers",
                   "Access-Control-Allow-Origins", "Authorization"],
    expose_headers=["Authorization"]
)

setup_exception_handlers(app)

app.include_router(api_router)
@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "dev" else False
    )