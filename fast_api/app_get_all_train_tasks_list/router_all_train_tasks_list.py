# import asyncio
# from functools import partial
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from configs.settings import BERT_MODEL_NAMES, BERT_OPTIONS
from db_redis.redis_funcs.func_redis_get_part_key_values import get_redis_values_by_pattern
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from fast_api.app_auth.scheme_auth import AuthDataBert

bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_bert_get_train_tasks_list = APIRouter(prefix=f"/{bert_base_url_name}",
                                             tags=["BERT"])


@router_bert_get_train_tasks_list.post(path="/bert_get_train_tasks_list/",
                                       # TODO: Describe responses here
                                       response_model=None)
async def bert_get_train_tasks_list(auth_data: AuthDataBert):
    verify_prod_username_password(username=auth_data.username,
                                  password=auth_data.password)
    try:
        print("\nGetting train model tasks list:")
        datetime_start = datetime.now()
        redis_match_pattern = f"{BERT_OPTIONS.BERT_NEW_DATASET_CSV_DIR_PREFIX}*"  # * - ends with any symbols
        tasks_dicts_list = await get_redis_values_by_pattern(
            partial_pattern=redis_match_pattern)
        tasks_sorted_list = sorted(tasks_dicts_list,
                                   key=lambda s: s["dataset_name"],
                                   reverse=True)
        getting_time = (datetime.now() - datetime_start).total_seconds()
        getting_time = round(getting_time, 1)

        json_content = {
            "message": "BERT train model tasks list [OK]",
            "username": auth_data.username,
            "model init": BERT_OPTIONS.BERT_MODEL_INIT,
            "model name": BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED,
            "model path": BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH,
            "getting time": getting_time,
            "tasks_sorted_list": tasks_sorted_list}

        json_response = JSONResponse(
            content=json_content,
            status_code=status.HTTP_200_OK)

        print(f"BERT response message: {json_content.get('message')}\n"
              f"BERT response.body keys: {json_content.keys()}\n"
              # f"BERT response.body: {json_response.body}\n"  # Long to log
              f"BERT response.status_code: {json_response.status_code}\n"
              f"username: {auth_data.username}\n"
              f"getting_time: {getting_time}\n"
              f"type(tasks_sorted_list): {type(tasks_sorted_list)}\n"
              f"tasks_sorted_list: {tasks_sorted_list}\n")
        return json_response
    except Exception as error:
        log_text = (f"BERT router train model tasks list [ERROR]: "
                    f"error: {error}")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
