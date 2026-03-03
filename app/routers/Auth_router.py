from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.Auth_schema import UserCreate, Token, UserResponse
from app.services import Auth_service
from app.dependencies import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await Auth_service.create_user(db, user)

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    access_token = await Auth_service.authenticate_user(db, form_data.username, form_data.password)
    return {"access_token": access_token, "token_type": "bearer"}