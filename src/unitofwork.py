from sqlalchemy.ext.asyncio import AsyncSession
from src.database.core import async_session_maker
from src.users.repositories import UserRepository
from src.posts.repositories import PostRepository, LikeRepository


class UnitOfWork:
    def __init__(self):
        self.session: AsyncSession | None = None

    async def __aenter__(self):
        self.session = async_session_maker()

        self.users = UserRepository(self.session)
        self.posts = PostRepository(self.session)
        self.likes = LikeRepository(self.session)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()

        await self.session.close()


async def get_uow():
    async with UnitOfWork() as uow:
        yield uow