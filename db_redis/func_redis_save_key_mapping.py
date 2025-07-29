from datetime import timedelta

from db_redis.init_redis import RedisAsyncConnection


async def redis_save_key_mapping_dict(key_name: str,
                                      mapping_dict: dict,
                                      expiry_seconds: timedelta | int
                                      ) -> None | str:
    async with RedisAsyncConnection(host=None, port=None,
                                    db=None, password=None,
                                    decode_responses=None,
                                    socket_connect_timeout=None,
                                    socket_keepalive=None) as redis_conn:
        try:
            await redis_conn.hset(name=key_name, mapping=mapping_dict)
            await redis_conn.expire(name=key_name, time=expiry_seconds)

            # TODO: Make redis transaction pipeline in the future
            # async with redis_conn.pipeline() as redis_pipeline:
            #     await redis_pipeline.multi()
            #     await redis_pipeline.hset(name=key_name, mapping=mapping_dict)
            #     await redis_pipeline.expire(name=key_name, time=expiry_seconds)
            #     await redis_pipeline.execute()
        except Exception as redis_error:
            error_log = (f"Redis DB saving [ERROR]: "
                         f"redis_error: {redis_error}")
            return error_log
