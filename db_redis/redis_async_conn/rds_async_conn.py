from typing import Union

import redis
from fastapi import HTTPException, status

from configs.settings import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD, REDIS_OPTIONS


class RedisAsyncConnection:
    def __init__(self,
                 host: str = None,
                 port: int = None,
                 db: str = None,
                 password: Union[str, None] = None,
                 decode_responses: bool = None,
                 socket_connect_timeout=None,
                 socket_keepalive=None,
                 **kwargs):
        self.host = REDIS_HOST if host is None else host
        self.port = REDIS_PORT if port is None else port
        self.db = REDIS_DB if db is None else db
        self.password = REDIS_PASSWORD if password is None else password
        self.extra_params = kwargs
        self.redis_connection = None

        self.decode_responses = decode_responses \
            if decode_responses else REDIS_OPTIONS.DECODE_RESPONSES

        self.socket_connect_timeout = socket_connect_timeout \
            if socket_connect_timeout else REDIS_OPTIONS.SOCKET_CONNECTION_TIMEOUT

        self.socket_keepalive = socket_keepalive \
            if socket_keepalive else REDIS_OPTIONS.SOCKET_KEEPALIVE

    async def get_redis_connection(self):
        try:
            redis_connection = redis.asyncio.Redis(
                host=self.host, port=self.port,
                db=self.db, password=self.password,
                decode_responses=self.decode_responses,
                socket_connect_timeout=self.socket_connect_timeout,
                socket_keepalive=self.socket_keepalive,
                **self.extra_params)

            await redis_connection.ping()
            return redis_connection
        except (redis.ConnectionError, redis.TimeoutError,
                redis.AuthenticationError, Exception) as redis_error:
            error_log = (
                f"Redis connection [ERROR]: error: {redis_error}\n"
                f"host: {self.host}, port: {self.port}, db: {self.db}\n"
                f"extra_params: {self.extra_params}\n")
            print(error_log)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_log)

    async def __aenter__(self):
        self.redis_connection = await self.get_redis_connection()
        return self.redis_connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.redis_connection:
            try:
                await self.redis_connection.ping()
                await self.redis_connection.close()
            except (redis.ConnectionError, Exception) as pre_planned_error:
                print(f"Pre-planned exception to check Redis connection [OK]:"
                      f"pre_planned_error: {pre_planned_error}, "
                      f"Not existing Redis connection not closed right")
