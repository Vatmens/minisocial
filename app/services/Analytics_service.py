from datetime import datetime, timezone, date
from app.database.mongodb import get_mongo_db


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