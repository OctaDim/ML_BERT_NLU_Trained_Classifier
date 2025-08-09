# import asyncio
# from functools import partial
import json
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from configs.console_colors import CONSOLE_COLORS
from configs.settings import BERT_MODEL_NAMES, BERT_OPTIONS
from db_redis.func_redis_get_part_key_values import get_redis_values_by_pattern
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from fast_api.app_auth.scheme_auth import AuthDataBert
from fast_api.app_get_checkset_result.scheme_get_checkset_result import CheckSetData

bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_bert_single_checkset_result = APIRouter(prefix=f"/{bert_base_url_name}",
                                               tags=["BERT"])


@router_bert_single_checkset_result.post(path="/bert_get_checkset_result/",
                                         # TODO: Describe responses here
                                         response_model=None)
async def bert_get_single_checkset_result(auth_data: AuthDataBert,
                                          checkset_data: CheckSetData):
    verify_prod_username_password(username=auth_data.username,
                                  password=auth_data.password)
    try:
        print("\nGetting check-sets result by check-set file name:")
        checkset_filename = checkset_data.checkset_filename
        if not checkset_filename:
            log_text = (f"Check-sets empty file name [ERROR]: "
                        f"checkset_filename: {checkset_filename}")
            print(log_text)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=log_text)

        datetime_start = datetime.now()
        checkset_prefix = BERT_OPTIONS.BERT_CHECKSET_NAME_REDIS_PREFIX
        redis_checkset_name = f"{checkset_prefix}_{checkset_filename}"
        redis_match_pattern = f"{redis_checkset_name}"  # * - starts, ends with any symbols
        redis_checksets_results = await get_redis_values_by_pattern(
            partial_pattern=redis_match_pattern,
            get_dictionary=False)

        if redis_checksets_results:
            checkset_result = redis_checksets_results[0]
            try:
                dict_json_str = checkset_result["checkset_test_results"]
                dict_python = json.loads(dict_json_str)
                checkset_result["checkset_test_results"] = dict_python
            except (json.JSONDecodeError, Exception) as json_error:
                log_text = (f"Redis json deserialization [ERROR]: "
                            f"json_error: {json_error}")
                print(log_text)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=log_text)
        else:
            checkset_result = {}
        getting_time = (datetime.now() - datetime_start).total_seconds()
        getting_time = round(getting_time, 1)

        json_response = JSONResponse(
            content={"message": "BERT train model tasks list [OK]",
                     "username": auth_data.username,
                     "model init": BERT_OPTIONS.BERT_MODEL_INIT,
                     "model name": BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED,
                     "model path": BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH,
                     "getting_time": getting_time,
                     "checkset_result": checkset_result},
            status_code=status.HTTP_200_OK)

        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        reset_color = CONSOLE_COLORS.RESET
        print(f"BERT response.body: {json_response.body}\n"
              f"BERT response.status_code: {json_response.status_code}\n"
              f"username: {auth_data.username}\n"
              f"checkset_result: {blue_color}{checkset_result}{reset_color}\n"
              f"getting_time: {getting_time}\n")
        return json_response
    except Exception as error:
        log_text = (f"BERT router get check-set model test result [ERROR]: "
                    f"error: {error}")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
