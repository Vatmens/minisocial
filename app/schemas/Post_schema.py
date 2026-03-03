from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AuthorResponse(BaseModel):
    id: int
    email: str


class PostCreate(BaseModel):
    title: str
    content: str


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    author: AuthorResponse
    likes_count: int = 0

    model_config = {"from_attributes": True}

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

