from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.User_model import User
from app.schemas.Auth_schema import UserCreate
from app.core.security import get_password_hash, verify_password, create_access_token


async def create_user(db: AsyncSession, user: UserCreate):
    result = await db.execute(select(User).where(User.email == user.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    db_user = User(email=user.email, hashed_password=get_password_hash(user.password))
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> str:
    result = await db.execute(select(User).where(User.email == email))
    db_user = result.scalar_one_or_none()

    if not db_user or not verify_password(password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    return create_access_token(data={"sub": str(db_user.id)})