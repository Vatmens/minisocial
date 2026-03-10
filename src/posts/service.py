from datetime import datetime, timezone, date
from fastapi import HTTPException, status
from src.unitofwork import UnitOfWork
from src.posts.schemas import PostCreate, PostUpdate
from src.posts.models import Post
from src.database.mongodb import get_mongo_db

async def create_post(uow: UnitOfWork, post_data: PostCreate, author_id: int):
    new_post = Post(**post_data.model_dump(), author_id=author_id)
    created_post = await uow.posts.add(new_post)
    return created_post

async def get_post_by_id(uow: UnitOfWork, post_id: int):
    row = await uow.posts.get_by_id(post_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    post, likes_count = row
    post_dict = post.__dict__.copy()
    post_dict["likes_count"] = likes_count
    post_dict["author"] = post.author
    return post_dict

async def get_posts(
        uow: UnitOfWork,
        limit: int = 10,
        offset: int = 0,
        author_id: int | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        order: str = "desc",
        include_deleted: bool = False
):
    results = await uow.posts.get_all(
        limit=limit, offset=offset, author_id=author_id, search=search,
        sort_by=sort_by, order=order, include_deleted=include_deleted
    )

    posts = []
    for post, likes_count in results:
        post_dict = post.__dict__.copy()
        post_dict["likes_count"] = likes_count
        post_dict["author"] = post.author
        posts.append(post_dict)
    return posts

async def update_post(uow: UnitOfWork, post_id: int, user_id: int, post_update: PostUpdate):
    post = await uow.posts.get_model_by_id(post_id)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.author_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit this post")

    if post_update.title is not None:
        post.title = post_update.title
    if post_update.content is not None:
        post.content = post_update.content

    await uow.session.flush()


    updated_row = await uow.posts.get_by_id(post_id)
    updated_post, likes_count = updated_row

    post_dict = updated_post.__dict__.copy()
    post_dict["likes_count"] = likes_count
    post_dict["author"] = updated_post.author
    return post_dict

async def delete_post(uow: UnitOfWork, post_id: int, user_id: int):
    post = await uow.posts.get_model_by_id(post_id)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.author_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this post")

    post.deleted_at = datetime.now(timezone.utc)

async def like_post(uow: UnitOfWork, post_id: int, user_id: int):
    await uow.likes.like_post(post_id, user_id)

async def unlike_post(uow: UnitOfWork, post_id: int, user_id: int):
    await uow.likes.unlike_post(post_id, user_id)

async def log_post_view(post_id: int, user_id: int | None):
    db = get_mongo_db()
    event = {
        "post_id": post_id,
        "user_id": user_id,
        "timestamp": datetime.now(timezone.utc)
    }
    await db.views.insert_one(event)

async def get_post_analytics(post_id: int, date_from: date, date_to: date):
    db = get_mongo_db()
    start = datetime.combine(date_from, datetime.min.time()).replace(tzinfo=timezone.utc)
    end = datetime.combine(date_to, datetime.max.time()).replace(tzinfo=timezone.utc)

    pipeline = [
        {"$match": {"post_id": post_id, "timestamp": {"$gte": start, "$lte": end}}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
            "views": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]

    cursor = db.views.aggregate(pipeline)
    results = await cursor.to_list(length=None)
    return {row["_id"]: row["views"] for row in results}