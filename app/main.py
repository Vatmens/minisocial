import uvicorn
from fastapi import FastAPI
from app.routers import Auth_router, Post_router, Like_router


app = FastAPI(
    title="Mini Social API",
    description="backend-сервіс Mini Social API",
    version="1.0.0"
)

app.include_router(Auth_router.router)
app.include_router(Post_router.router)
app.include_router(Like_router.router)

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok"}
