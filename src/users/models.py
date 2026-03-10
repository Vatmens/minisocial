from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.core import Base
from src.models import TimeStampMixin

class User(Base, TimeStampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))

    posts = relationship("Post", back_populates="author")
    likes = relationship("Like", back_populates="user")