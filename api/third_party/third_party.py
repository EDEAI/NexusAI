import json
from typing import Any, Dict

from fastapi import APIRouter, Body, Query

from api.utils.common import response_error, response_success
from config import settings
from core.database import redis

router = APIRouter()


@router.post("/sandbox-callback")
def sandbox_callback(
    token: str = Query(..., min_length=1),
    payload: Dict[str, Any] = Body(...)
):
    """
    Receive third-party webhook callbacks and forward payloads to Redis.

    The payload will be stored under `sandbox_callback:{token}` with a TTL
    equal to `SANDBOX_MAX_ALIVE_SECONDS`, so a waiting sandbox skill can
    unblock and continue processing.
    """
    if not token.strip():
        return response_error("Missing callback token")

    redis_key = f"sandbox_callback:{token}"
    redis.rpush(redis_key, json.dumps(payload))
    redis.expire(redis_key, settings.SANDBOX_MAX_ALIVE_SECONDS)
    return response_success()
