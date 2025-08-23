# import asyncio
# from functools import partial
import json
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from configs.settings import BERT_MODEL_NAMES, BERT_OPTIONS
from db_redis.func_redis_get_part_key_values import get_redis_values_by_pattern
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from fast_api.app_auth.scheme_auth import AuthDataBert

bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_bert_all_checksets_results = APIRouter(prefix=f"/{bert_base_url_name}",
                                              tags=["BERT"])


@router_bert_all_checksets_results.post(path="/bert_get_all_checksets_result/",
                                        # TODO: Describe responses here
                                        response_model=None)
async def bert_get_all_checksets_results(auth_data: AuthDataBert):
    verify_prod_username_password(username=auth_data.username,
                                  password=auth_data.password)
    try:
        print("\nGetting all check-sets test results list:")
        datetime_start = datetime.now()
        redis_match_pattern = f"{BERT_OPTIONS.BERT_CHECKSET_NAME_REDIS_PREFIX}*"  # * - ends with any symbols

        redis_checksets_results = await get_redis_values_by_pattern(
            partial_pattern=redis_match_pattern,
            get_dictionary=True)

        checksets_results = {}
        for redis_checkset_name, cur_res_dict in redis_checksets_results.items():
            print("#" * 65)
            print(f"redis_checkset_name: "
                  f"{type(redis_checkset_name)}, {redis_checkset_name}")
            orig_checkset_filename = redis_checkset_name.lstrip(
                BERT_OPTIONS.BERT_CHECKSET_NAME_REDIS_PREFIX)
            print(f"orig_checkset_filename: "
                  f"{type(orig_checkset_filename)}, {orig_checkset_filename}")
            try:
                json_str_list = cur_res_dict.get("checkset_test_results")
                print(f"type(json_str_list): {type(json_str_list)}")
                # print(f"json_str_list: {type(json_str_list)}, {json_str_list}")
                if json_str_list:
                    python_list = json.loads(json_str_list)
                    print(f"type(python_list): {type(python_list)}")
                    # print(f"python_list: {type(python_list)}, {python_list}")
                    cur_res_dict["checkset_test_results"] = python_list
                else:
                    cur_res_dict["checkset_test_results"] = []
            except Exception as error:
                log_text = (f"Redis json deserialization [ERROR]: "
                            f"error: {error}")
                print(log_text)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=log_text)
            checksets_results[orig_checkset_filename] = cur_res_dict

        getting_time = (datetime.now() - datetime_start).total_seconds()
        getting_time = round(getting_time, 1)

        json_response = JSONResponse(
            content={"message": "BERT train model tasks list [OK]",
                     "username": auth_data.username,
                     "model init": BERT_OPTIONS.BERT_MODEL_INIT,
                     "model name": BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED,
                     "model path": BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH,
                     "getting_time": getting_time,
                     "checksets_results": checksets_results},
            status_code=status.HTTP_200_OK)

        print(f"BERT response.body: contains 'checksets_results' key\n"
              # f"BERT response.body: {json_response.body}\n"  # Too long console log
              f"BERT response.status_code: {json_response.status_code}\n"
              f"username: {auth_data.username}\n"
              f"getting_time: {getting_time}\n"
              f"checksets_results: {type(checksets_results)}\n"
              f"checksets_results.keys(): {checksets_results.keys()}\n")
        return json_response
    except Exception as error:
        log_text = (f"BERT router get check-sets results [ERROR]: "
                    f"error: {error}")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
