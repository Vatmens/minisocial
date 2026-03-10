from src.unitofwork import UnitOfWork
from src.auth.security import verify_password

async def authenticate_user(uow: UnitOfWork, email: str, password: str):
    user = await uow.users.get_by_email(email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user