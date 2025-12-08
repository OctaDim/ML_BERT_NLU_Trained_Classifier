# import asyncio
# from functools import partial
import os
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from ML_BERT_classifier.class_bert import ClassifierBERT
from configs.console_colors import CONSOLE_COLORS
from configs.settings import (
    BERT_MODEL_NAMES, BERT_OPTIONS, ALCHEMY_OPTIONS)
from db_postgres.postgres_conn.pgs_connection import (
    PgsAsyncConnection)
from db_postgres.postgres_conn.postgres_session import (
    PgsAsyncSession)
from fast_api.fast_api_dependencies.dep_get_bert_model_instance import (
    get_bert_model_instance_dep)
from db_postgres.postgres_queries.qry_get_last_dataset_name_and_dir import (
    get_last_dataset_name_and_dir_qry)
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from fast_api.app_auth.scheme_auth import AuthDataBert
from utils_specific.get_initial_dataset_dir_path import (
    get_initial_dataset_dir_path)
from utils_specific.get_last_saved_dataset_path import (
    get_last_saved_dataset_dir_path)

bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_bert_last_dataset_name = APIRouter(prefix=f"/{bert_base_url_name}",
                                          tags=["BERT"])


@router_bert_last_dataset_name.post(path="/bert_get_last_dataset_name/",
                                    # TODO: Describe responses here
                                    response_model=None)
async def bert_get_last_dataset_name(
        auth_data: AuthDataBert,
        bert_model_inst: Annotated[
            ClassifierBERT, Depends(get_bert_model_instance_dep)]
) -> JSONResponse:
    verify_prod_username_password(username=auth_data.username,
                                  password=auth_data.password)

    log_pgs_good_ops = ALCHEMY_OPTIONS.ALCHEMY_SESSION_OK_ACTIONS_LOGS

    try:
        print("Getting last saved dataset directory name:")
        datetime_start = datetime.now()

        print("Postgres DB Getting last saved dataset dir and dataset name:")
        pgs_conn = PgsAsyncConnection()
        async with PgsAsyncSession(engine=pgs_conn.engine,
                                   log_good_ops=log_pgs_good_ops
                                   ) as pgs_session:
            pgs_last_dataset_data = await get_last_dataset_name_and_dir_qry(
                ongoing_session=pgs_session)
        if pgs_last_dataset_data:
            # last_dataset_dir = pgs_last_dataset_data[1]
            last_saved_dataset_name = pgs_last_dataset_data[0]
        else:
            print("Getting csv last saved dataset directory and dataset name:")
            inst_last_saved_dataset_path = bert_model_inst.last_saved_dataset_dir
            last_saved_dataset_dir_path, initial_dataset_dir_path = None, None
            if inst_last_saved_dataset_path:
                last_dataset_dir = inst_last_saved_dataset_path
            else:
                last_saved_dataset_dir_path = get_last_saved_dataset_dir_path()
                if last_saved_dataset_dir_path:
                    last_dataset_dir = last_saved_dataset_dir_path
                else:
                    initial_dataset_dir_path = get_initial_dataset_dir_path()
                    if initial_dataset_dir_path:
                        last_dataset_dir = initial_dataset_dir_path
                    else:
                        last_dataset_dir = ""
            if not last_dataset_dir:
                log_text = (
                    f"BERT Last dataset directory or files not found [ERROR]:\n"
                    f"inst_last_saved_dataset_path: {inst_last_saved_dataset_path}\n"
                    f"last_saved_dataset_dir_path: {last_saved_dataset_dir_path}\n"
                    f"initial_dataset_dir_path: {initial_dataset_dir_path}\n"
                    f"last_dataset_dir: {last_dataset_dir}\n")
                print(log_text)
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail=log_text)

            dataset_path_dirs = last_dataset_dir.split(os.sep)
            last_saved_dataset_name = dataset_path_dirs[-1]  # As dataset files dir name
        getting_time = (datetime.now() - datetime_start).total_seconds()
        getting_time = round(getting_time, 1)

        json_response = JSONResponse(
            content={
                "message": "BERT last saved dataset dir name [OK]",
                "username": auth_data.username,
                "model init": BERT_OPTIONS.BERT_MODEL_INIT,
                "model name": BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED,
                "model path": BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH,
                "getting time": getting_time,
                "last_saved_dataset_name": last_saved_dataset_name},
            status_code=status.HTTP_200_OK)

        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        reset_color = CONSOLE_COLORS.RESET
        print(f"BERT response.body: {json_response.body}\n"
              f"BERT response.status_code: {json_response.status_code}\n"
              f"username: {auth_data.username}\n"
              f"getting_time: {getting_time}\n"
              f"last_saved_dataset_name: {blue_color}{last_saved_dataset_name}{reset_color}\n")
        return json_response
    except Exception as error:
        log_text = (f"BERT router last saved dataset dir name [ERROR]: "
                    f"error: {error}")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
