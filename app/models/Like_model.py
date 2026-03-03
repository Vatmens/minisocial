from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base


class Like(Base):
    __tablename__ = "likes"
    __table_args__ = (
        UniqueConstraint('user_id', 'post_id', name='uix_user_post_like'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))

    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")