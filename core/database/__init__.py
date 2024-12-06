from redis import Redis

from config import settings

from .sql_database import SQLDatabase
from .mysql import MySQL, Conditions


redis = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD
)

__all__ = [
    "SQLDatabase",
    "MySQL",
    "Conditions",
    "redis"
]
