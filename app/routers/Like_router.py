from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.Like_schema import LikeResponse
from app.services import Like_service
from app.dependencies import get_db, get_current_user
from app.models.User_model import User

router = APIRouter(prefix="/posts", tags=["Likes"])


@router.post("/{post_id}/like", response_model=LikeResponse)
async def like_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await Like_service.like_post(db, post_id, current_user.id)
    return {"message": "Post liked successfully"}


@router.delete("/{post_id}/like", response_model=LikeResponse)
async def unlike_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await Like_service.unlike_post(db, post_id, current_user.id)
    return {"message": "Post unliked successfully"}