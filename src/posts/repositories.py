from sqlalchemy import select, func, asc, desc, or_, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from src.posts.models import Post, Like

class PostRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, post: Post) -> Post:
        self.session.add(post)
        await self.session.flush()
        return post

    async def get_model_by_id(self, post_id: int) -> Post | None:
        result = await self.session.execute(select(Post).where(Post.id == post_id))
        return result.scalar_one_or_none()

    async def get_by_id(self, post_id: int):
        stmt = (
            select(Post, func.count(Like.id).label("likes_count"))
            .outerjoin(Like)
            .options(selectinload(Post.author))
            .where(Post.id == post_id, Post.deleted_at.is_(None))
            .group_by(Post.id)
        )
        result = await self.session.execute(stmt)
        return result.first()

    async def get_all(
        self, limit: int, offset: int, author_id: int | None = None,
        search: str | None = None, sort_by: str = "created_at",
        order: str = "desc", include_deleted: bool = False
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
        result = await self.session.execute(stmt)
        return result.all()


class LikeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def like_post(self, post_id: int, user_id: int):
        stmt = insert(Like).values(post_id=post_id, user_id=user_id).on_conflict_do_nothing()
        await self.session.execute(stmt)
        await self.session.flush()

    async def unlike_post(self, post_id: int, user_id: int):
        stmt = delete(Like).where(Like.post_id == post_id, Like.user_id == user_id)
        await self.session.execute(stmt)
        await self.session.flush()