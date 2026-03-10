from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, Text, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from src.database.core import Base
from src.models import TimeStampMixin

class Post(Base, TimeStampMixin):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    author = relationship("User", back_populates="posts")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")


class Like(Base, TimeStampMixin):
    __tablename__ = "likes"
    __table_args__ = (
        UniqueConstraint('user_id', 'post_id', name='uix_user_post_like'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))

    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")