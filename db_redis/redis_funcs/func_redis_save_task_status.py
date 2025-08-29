# import json
# from datetime import timedelta
#
# from configs.settings import (
#     REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD, REDIS_OPTIONS)
# from db_redis.init_redis import RedisAsyncConnection
#
#
# async def redis_save_task_status(train_task_id: str,
#                                  task_status: str,
#                                  expiry_days: int) -> None:
#     async with RedisAsyncConnection(
#             host=REDIS_HOST, port=REDIS_PORT,
#             db=REDIS_DB, password=REDIS_PASSWORD,
#             decode_responses=REDIS_OPTIONS.DECODE_RESPONSES,
#             socket_connect_timeout=REDIS_OPTIONS.SOCKET_CONNECTION_TIMEOUT,
#             socket_keepalive=REDIS_OPTIONS.SOCKET_KEEPALIVE
#     ) as redis_conn:
#         task_data_dict = {"status": task_status}
#         task_data_json = json.dumps(task_data_dict)
#         task_id_prefix = REDIS_OPTIONS.TRAIN_TASK_ID_PREFIX
#         redis_key_name = f"{task_id_prefix}{train_task_id}"
#         await redis_conn.setex(name=redis_key_name,
#                                time=timedelta(days=expiry_days),
#                                value=task_data_json)
