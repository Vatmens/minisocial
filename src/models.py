from datetime import datetime, timezone
from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declarative_base

# Функція для отримання поточного часу в UTC
def get_utc_now():
    return datetime.now(timezone.utc)

class TimeStampMixin:
    created_at = Column(
        DateTime(timezone=True),
        default=get_utc_now,
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=get_utc_now,
        onupdate=get_utc_now,
        nullable=False
    )