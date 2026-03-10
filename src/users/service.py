from src.unitofwork import UnitOfWork
from src.users.models import User
from src.users.schemas import UserCreate
from src.auth.security import get_password_hash
from fastapi import HTTPException, status


async def create_user(uow: UnitOfWork, user_in: UserCreate):

    existing_user = await uow.users.get_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    hashed_password = get_password_hash(user_in.password)
    new_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
    )

    created_user = await uow.users.add(new_user)
    return created_user