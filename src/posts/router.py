from fastapi import APIRouter, Depends, Query, status, BackgroundTasks
from datetime import date
from typing import List, Optional

from src.unitofwork import UnitOfWork, get_uow
from src.posts.schemas import PostCreate, PostResponse, PostUpdate, LikeResponse
from src.posts.service import (
    get_post_by_id, log_post_view, create_post, get_posts,
    update_post, delete_post, like_post, unlike_post, get_post_analytics
)
from src.dependencies import get_current_user, get_optional_current_user
from src.users.models import User

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post_route(
    post: PostCreate,
    uow: UnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_user)
):
    return await create_post(uow, post, current_user.id)


@router.get("/{post_id}", response_model=PostResponse)
async def read_post_route(
    post_id: int,
    background_tasks: BackgroundTasks,
    uow: UnitOfWork = Depends(get_uow),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    post = await get_post_by_id(uow, post_id)

    user_id = current_user.id if current_user else None
    background_tasks.add_task(log_post_view, post_id, user_id)

    return post


@router.get("/", response_model=List[PostResponse])
async def read_posts_route(
    limit: int = Query(10, ge=1, le=100, description="Number of posts per page"),
    offset: int = Query(0, ge=0, description="Number of posts to skip"),
    author_id: Optional[int] = Query(None, description="Filter by author ID"),
    search: Optional[str] = Query(None, description="Search by title or content"),
    sort: str = Query("created_at", pattern="^(created_at|likes)$", description="Sort field (created_at or likes)"),
    order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order (asc or desc)"),
    include_deleted: bool = Query(False, description="Include deleted posts"),
    uow: UnitOfWork = Depends(get_uow)
):
    return await get_posts(
        uow=uow,
        limit=limit,
        offset=offset,
        author_id=author_id,
        search=search,
        sort_by=sort,
        order=order,
        include_deleted=include_deleted
    )


@router.put("/{post_id}", response_model=PostResponse)
async def update_post_route(
    post_id: int,
    post_update: PostUpdate,
    uow: UnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_user)
):
    return await update_post(uow, post_id, current_user.id, post_update)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post_route(
    post_id: int,
    uow: UnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_user)
):
    await delete_post(uow, post_id, current_user.id)


@router.get("/{post_id}/analytics")
async def get_analytics_route(
    post_id: int,
    date_from: date = Query(..., alias="from", description="Format: YYYY-MM-DD"),
    date_to: date = Query(..., alias="to", description="Format: YYYY-MM-DD")
):
    # Тут UoW не потрібен, бо аналітика йде прямо в MongoDB
    return await get_post_analytics(post_id, date_from, date_to)


@router.post("/{post_id}/like", response_model=LikeResponse)
async def like_post_route(
    post_id: int,
    uow: UnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_user)
):
    await like_post(uow, post_id, current_user.id)
    return {"message": "Post liked successfully"}


@router.delete("/{post_id}/like", response_model=LikeResponse)
async def unlike_post_route(
    post_id: int,
    uow: UnitOfWork = Depends(get_uow),
    current_user: User = Depends(get_current_user)
):
    await unlike_post(uow, post_id, current_user.id)
    return {"message": "Post unliked successfully"}