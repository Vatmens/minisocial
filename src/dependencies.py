import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

from src.users.models import User
from src.config import settings
from src.unitofwork import UnitOfWork, get_uow

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        uow: UnitOfWork = Depends(get_uow)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception


    user = await uow.users.get_by_id(int(user_id))

    if user is None:
        raise credentials_exception
    return user


async def get_optional_current_user(
        token: Optional[str] = Depends(oauth2_scheme_optional),
        uow: UnitOfWork = Depends(get_uow)
) -> Optional[User]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except jwt.InvalidTokenError:
        return None


    user = await uow.users.get_by_id(int(user_id))
    return user