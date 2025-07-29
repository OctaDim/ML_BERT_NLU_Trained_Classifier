from configs.settings import (
    REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD, REDIS_OPTIONS)
from db_redis.init_redis import RedisAsyncConnection


async def get_values_by_key_list(partial_pattern: str) -> dict:
    """'partial_pattern can be like '*any_string', 'any_string*',
    '*any_string*' or '*any*str*:*'"""
    async with RedisAsyncConnection(
            host=REDIS_HOST, port=REDIS_PORT,
            db=REDIS_DB, password=REDIS_PASSWORD,
            decode_responses=REDIS_OPTIONS.DECODE_RESPONSES,
            socket_connect_timeout=REDIS_OPTIONS.SOCKET_CONNECTION_TIMEOUT,
            socket_keepalive=REDIS_OPTIONS.SOCKET_KEEPALIVE
    ) as redis_conn:
        pattern_key_values = {}
        async for cur_key in redis_conn.scan_iter(match=partial_pattern):
            value = await redis_conn.get(cur_key)
            pattern_key_values[cur_key] = value
        return pattern_key_values
