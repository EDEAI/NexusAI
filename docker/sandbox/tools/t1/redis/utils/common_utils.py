from typing import Any, Sized

import redis
from redis.client import Redis
from rediscluster import RedisCluster

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 6379


def default_if_empty(value: Any, default=None) -> Any:
    if value:
        if isinstance(value, Sized):
            return value if len(value) else default
        return value
    else:
        return default


def get_redis_cluster(data: dict[str, Any]) -> RedisCluster:
    return RedisCluster(
        startup_nodes=[{
            'host': default_if_empty(data.get('host'), DEFAULT_HOST),
            'port': int(default_if_empty(data.get('port'), DEFAULT_PORT))
        }],
        password=default_if_empty(data.get('password')),
        decode_responses=True
    )


def get_redis_single(data: dict[str, Any]) -> Redis:
    return redis.Redis(connection_pool=redis.ConnectionPool(
        host=default_if_empty(data.get('host'), DEFAULT_HOST),
        port=int(default_if_empty(data.get('port'), DEFAULT_PORT)),
        password=default_if_empty(data.get('password')),
        decode_responses=True
    ))


def get_redis_connection(data: dict[str, Any]) -> RedisCluster | Redis:
    is_cluster = bool(default_if_empty(data.get('cluster'), False))
    if is_cluster:
        return get_redis_cluster(data)
    else:
        return get_redis_single(data)
