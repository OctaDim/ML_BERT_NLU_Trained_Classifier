# import asyncio
# from functools import partial
import os
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from configs.console_colors import CONSOLE_COLORS
from configs.settings import BERT_MODEL_NAMES, BERT_OPTIONS
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from fast_api.app_auth.scheme_auth import AuthDataBert
from utils_specific.get_last_saved_dataset_path import get_last_saved_dataset_dir_path

bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_bert_last_dataset_name = APIRouter(prefix=f"/{bert_base_url_name}",
                                          tags=["BERT"])


@router_bert_last_dataset_name.post(path="/bert_get_last_dataset_name/",
                                    # TODO: Describe responses here
                                    response_model=None)
async def bert_get_last_dataset_name(auth_data: AuthDataBert):
    verify_prod_username_password(username=auth_data.username,
                                  password=auth_data.password)
    try:
        print("\nGetting last saved dataset directory name:")
        datetime_start = datetime.now()
        last_saved_dataset_dir = get_last_saved_dataset_dir_path()
        dataset_path_dirs = last_saved_dataset_dir.split(os.sep)
        dataset_name = dataset_path_dirs[-1]  # As dataset files directory name
        getting_time = (datetime.now() - datetime_start).total_seconds()
        getting_time = round(getting_time, 1)

        json_response = JSONResponse(
            content={"message": "BERT last saved dataset dir name [OK]",
                     "username": auth_data.username,
                     "model init": BERT_OPTIONS.BERT_MODEL_INIT,
                     "model name": BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED,
                     "model path": BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH,
                     "getting time": getting_time,
                     "dataset_name": dataset_name},
            status_code=status.HTTP_200_OK)

        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        reset_color = CONSOLE_COLORS.RESET
        print(f"BERT response.body: {json_response.body}\n"
              f"BERT response.status_code: {json_response.status_code}\n"
              f"username: {auth_data.username}\n"
              f"getting_time: {getting_time}\n"
              f"dataset_name: {blue_color}{dataset_name}{reset_color}\n")
        return json_response
    except Exception as error:
        log_text = (f"BERT router last saved dataset dir name [ERROR]: "
                    f"error: {error}")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
