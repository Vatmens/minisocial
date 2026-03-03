from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import delete
from app.models.Like_model import Like


async def like_post(db: AsyncSession, post_id: int, user_id: int):
    stmt = insert(Like).values(post_id=post_id, user_id=user_id).on_conflict_do_nothing()
    await db.execute(stmt)
    await db.commit()


async def unlike_post(db: AsyncSession, post_id: int, user_id: int):
    stmt = delete(Like).where(Like.post_id == post_id, Like.user_id == user_id)
    await db.execute(stmt)
    await db.commit()