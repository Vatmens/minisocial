from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func, asc, desc, or_
from app.models.Post_model import Post
from app.models.Like_model import Like
from fastapi import HTTPException, status
from app.schemas.Post_schema import PostCreate, PostUpdate


async def create_post(db: AsyncSession, post: PostCreate, user_id: int):
    db_post = Post(title=post.title, content=post.content, author_id=user_id)
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)

    stmt = select(Post).options(selectinload(Post.author)).where(Post.id == db_post.id)
    result = await db.execute(stmt)
    return result.scalar_one()


async def get_post_by_id(db: AsyncSession, post_id: int):
    stmt = (
        select(Post, func.count(Like.id).label("likes_count"))
        .outerjoin(Like)
        .options(selectinload(Post.author))
        .where(Post.id == post_id, Post.deleted_at.is_(None))
        .group_by(Post.id)
    )
    result = await db.execute(stmt)
    row = result.first()

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    post, likes_count = row
    post_dict = post.__dict__.copy()
    post_dict["likes_count"] = likes_count
    post_dict["author"] = post.author
    return post_dict


async def get_posts(
        db: AsyncSession,
        limit: int = 10,
        offset: int = 0,
        author_id: int | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        order: str = "desc",
        include_deleted: bool = False
):
    stmt = (
        select(Post, func.count(Like.id).label("likes_count"))
        .outerjoin(Like)
        .options(selectinload(Post.author))
        .group_by(Post.id)
    )

    if not include_deleted:
        stmt = stmt.where(Post.deleted_at.is_(None))

    if author_id is not None:
        stmt = stmt.where(Post.author_id == author_id)

    if search:
        stmt = stmt.where(
            or_(
                Post.title.ilike(f"%{search}%"),
                Post.content.ilike(f"%{search}%")
            )
        )

    sort_column = func.count(Like.id) if sort_by == "likes" else Post.created_at

    if order == "asc":
        stmt = stmt.order_by(asc(sort_column))
    else:
        stmt = stmt.order_by(desc(sort_column))

    stmt = stmt.limit(limit).offset(offset)

    result = await db.execute(stmt)

    posts = []
    for post, likes_count in result.all():
        post_dict = post.__dict__.copy()
        post_dict["likes_count"] = likes_count
        post_dict["author"] = post.author
        posts.append(post_dict)
    return posts


async def update_post(db: AsyncSession, post_id: int, user_id: int, post_update: PostUpdate):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.author_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit this post")

    if post_update.title is not None:
        post.title = post_update.title
    if post_update.content is not None:
        post.content = post_update.content

    await db.commit()
    await db.refresh(post)
    stmt = (
        select(Post, func.count(Like.id).label("likes_count"))
        .outerjoin(Like)
        .options(selectinload(Post.author))
        .where(Post.id == post_id)
        .group_by(Post.id)
    )
    updated_result = await db.execute(stmt)
    updated_post, likes_count = updated_result.one()

    post_dict = updated_post.__dict__.copy()
    post_dict["likes_count"] = likes_count
    post_dict["author"] = updated_post.author
    return post_dict


async def delete_post(db: AsyncSession, post_id: int, user_id: int):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.author_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this post")

    post.deleted_at = datetime.now(timezone.utc)
    await db.commit()