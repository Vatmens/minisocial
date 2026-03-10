from fastapi import APIRouter, Depends, status
from src.unitofwork import UnitOfWork, get_uow
from src.users.schemas import UserCreate, UserResponse
from src.users.service import create_user


router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user_route(
    user: UserCreate,
    uow: UnitOfWork = Depends(get_uow)
):
    return await create_user(uow, user)