from fastapi import APIRouter, Depends, Query, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from typing import List, Optional

from app.schemas.Post_schema import PostCreate, PostResponse, PostUpdate
from app.services import Post_service, Analytics_service
from app.dependencies import get_db, get_current_user, get_optional_current_user
from app.models.User_model import User

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("/", response_model=PostResponse)
async def create_post(
    post: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await Post_service.create_post(db, post, current_user.id)


@router.get("/{post_id}", response_model=PostResponse)
async def read_post(
        post_id: int,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_db),
        current_user: Optional[User] = Depends(get_optional_current_user)
):
    post = await Post_service.get_post_by_id(db, post_id)


    user_id = current_user.id if current_user else None
    background_tasks.add_task(Analytics_service.log_post_view, post_id, user_id)

    return post

@router.get("/", response_model=List[PostResponse])
async def read_posts(
    limit: int = Query(10, ge=1, le=100, description="Number of posts per page"),
    offset: int = Query(0, ge=0, description="Number of posts to skip"),
    author_id: Optional[int] = Query(None, description="Filter by author ID"),
    search: Optional[str] = Query(None, description="Search by title or content"),
    sort: str = Query("created_at", pattern="^(created_at|likes)$", description="Sort field (created_at or likes)"),
    order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order (asc or desc)"),
    include_deleted: bool = Query(False, description="Include deleted posts"),
    db: AsyncSession = Depends(get_db)
):

    return await Post_service.get_posts(
        db=db,
        limit=limit,
        offset=offset,
        author_id=author_id,
        search=search,
        sort_by=sort,
        order=order,
        include_deleted=include_deleted
    )


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_update: PostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await Post_service.update_post(db, post_id, current_user.id, post_update)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await Post_service.delete_post(db, post_id, current_user.id)


@router.get("/{post_id}/analytics")
async def get_analytics(
    post_id: int,
    date_from: date = Query(..., alias="from", description="Format: YYYY-MM-DD"),
    date_to: date = Query(..., alias="to", description="Format: YYYY-MM-DD")
):

    return await Analytics_service.get_post_analytics(post_id, date_from, date_to)


