from db_redis.redis_async_conn.rds_async_conn import (
    RedisAsyncConnection)


async def get_redis_values_by_pattern(
        partial_pattern: str,
        get_dictionary: bool = False) -> list | dict:
    """'partial_pattern can be like '*any_string', 'any_string*',
    '*any_string*' or '*any*str*:*'"""
    if get_dictionary:
        redis_values = {}
    else:
        redis_values = []

    async with RedisAsyncConnection(host=None, port=None,
                                    db=None, password=None,
                                    decode_responses=None,
                                    socket_connect_timeout=None,
                                    socket_keepalive=None) as redis_conn:
        redis_matched_keys = redis_conn.scan_iter(match=partial_pattern)

    async for cur_redis_key in redis_matched_keys:
        redis_key_dict = await redis_conn.hgetall(cur_redis_key)  # Always returns dict or {}, not None
        if get_dictionary:
            redis_values[cur_redis_key] = redis_key_dict
        else:
            redis_values.append(redis_key_dict)
    return redis_values
