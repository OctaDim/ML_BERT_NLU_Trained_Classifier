# import asyncio
# from functools import partial
import os
import uuid
from datetime import timedelta
from typing import Annotated

from fastapi import (APIRouter, File, Form, HTTPException, UploadFile,
                     status, BackgroundTasks)
from fastapi.responses import JSONResponse

from configs.console_colors import CONSOLE_COLORS
from configs.settings import (
    BERT_OPTIONS, REDIS_OPTIONS, STATUSES, BERT_MODEL_NAMES)
from db_redis.func_redis_save_key_mapping import redis_save_key_mapping_dict
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from fast_api.app_auth.scheme_auth import AuthDataBert
from fast_api.app_checkset_model_test.func_checkset_model_test_background import (
    background_checkset_test_model)
from utils_common.class_file_validate_read import FileValidateRead

bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_bert_checkset_model_test = APIRouter(prefix=f"/{bert_base_url_name}",
                                            tags=["BERT"])


@router_bert_checkset_model_test.post(path="/bert_checkset_test_model/",
                                      # TODO: Describe responses here
                                      response_model=None)
async def bert_start_checkset_model_test(
        upload_file: Annotated[UploadFile, File(description="file .xls, .xlsx, or .txt")],
        username: Annotated[str, Form()],
        password: Annotated[str, Form()],
        background_tasks: BackgroundTasks  # FastAPI Class for background tasks
):
    verify_prod_username_password(username=username,
                                  password=password)

    print("\nBERT Model check-set start test:")
    REDIS_KEY_EXPIRE_TIME = timedelta(days=REDIS_OPTIONS.CHECKSET_TESTS_EXPIRY_DAYS)

    ALLOWED_FILE_MIME_TYPES = (
        "application/vnd.ms-excel",  # xls, old excel
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # xlsx, new excel
        "text/csv", "application/csv",  # csv
        "text/plain",)  # txt

    if not upload_file:
        log_text = (f"File (.xlsx, .xls, .csv or .txt) not passed [ERROR]: "
                    f"text_category_data.upload_file: {upload_file}")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=log_text)

    if upload_file.content_type not in ALLOWED_FILE_MIME_TYPES:
        log_text = (f"Unsupported file MIME content type [ERROR]: "
                    f"upload_file.content_type: {upload_file.content_type}, "
                    f"allowed MIME types: {ALLOWED_FILE_MIME_TYPES}")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=log_text)

    allowed_extensions = BERT_OPTIONS.BERT_TRAIN_DATASET_FILE_EXTENSIONS
    checkset_file_name = os.path.basename(upload_file.filename)
    checkset_redis_prefix = BERT_OPTIONS.BERT_CHECKSET_NAME_REDIS_PREFIX
    checkset_redis_name = f"{checkset_redis_prefix}_{checkset_file_name}"
    _, file_extension = os.path.splitext(checkset_file_name)
    file_extension = file_extension.lower()

    checkset_task_uuid = str(uuid.uuid4())
    redis_update = {
        "checkset_status": STATUSES.STATUS_CHECKSET_TEST_PENDING_EN,
        "checkset_complete_status": "",
        "checkset_task_uuid": checkset_task_uuid,
        "checkset_file_name": checkset_file_name,
        "checkset_redis_name": checkset_redis_name,
        "step_t1_model_checkset_testing_start": "[OK]", }
    redis_error = await redis_save_key_mapping_dict(
        key_name=checkset_redis_name,
        mapping_dict=redis_update,
        expiry_seconds=REDIS_KEY_EXPIRE_TIME)
    if redis_error:
        print(redis_error)

    if not checkset_file_name.lower().endswith(allowed_extensions):
        log_text = (f"File extension not xls, xlsx, csv or txt [ERROR]:\n"
                    f"upload_file.filename: {upload_file.filename}\n"
                    f"file extension: {file_extension}\n"
                    f"allowed extensions: {allowed_extensions}\n")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=log_text)

    file_valid_read = FileValidateRead(file=upload_file)
    checkset_data_list = []
    error_flag_text = ""
    if file_extension.endswith((".xlsx", ".xls")):
        if await file_valid_read.validate_content_excel():
            checkset_data_list = await file_valid_read.read_file_excel()
        else:
            error_flag_text = "File excel content [ERROR]"
    elif file_extension.endswith("txt"):
        if await file_valid_read.validate_content_txt():
            checkset_data_list = await file_valid_read.read_file_txt()
        else:
            error_flag_text = "File txt content [ERROR]"
    elif file_extension.endswith("csv"):
        if await file_valid_read.validate_content_csv():
            checkset_data_list = await file_valid_read.read_file_csv()
        else:
            error_flag_text = "File csv content [ERROR]"

    if error_flag_text:
        log_text = (f"{error_flag_text}:\n"
                    f"upload_file.filename: {upload_file.filename}\n"
                    f"upload_file.content_type: {upload_file.content_type}\n"
                    f"file_extension: {file_extension}\n"
                    f"checkset_data_list: {checkset_data_list}")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=log_text)

    if not checkset_data_list:
        log_text = (f"Empty upload file [ERROR]:\n"
                    f"upload_file.filename: {upload_file.filename}\n"
                    f"upload_file.content_type: {upload_file.content_type}\n"
                    f"file_extension: {file_extension}\n"
                    f"checkset_data_list: {checkset_data_list}")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=log_text)

    redis_update = {
        "checkset_status": STATUSES.STATUS_CHECKSET_TEST_START_EN,
        "step_t2_model_checkset_testing_start": "[OK]", }
    redis_error = await redis_save_key_mapping_dict(
        key_name=checkset_redis_name,
        mapping_dict=redis_update,
        expiry_seconds=REDIS_KEY_EXPIRE_TIME)
    if redis_error:
        print(redis_error)

    try:
        print("####### BEFORE BACKGROUND CHECK-SET MODEL TEST")
        auth_data = AuthDataBert(username=username, password=password)
        background_tasks.add_task(background_checkset_test_model,
                                  auth_data,
                                  checkset_data_list,
                                  checkset_file_name,
                                  checkset_redis_name)
        print("####### AFTER BACKGROUND CHECK-SET MODEL TEST")

        json_response = JSONResponse(
            content={
                "message": "BERT model check-set testing start [OK]",
                "username": auth_data.username,
                "model init": BERT_OPTIONS.BERT_MODEL_INIT,
                "model name": BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED,
                "model path": BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH,
                "checkset_file_name": checkset_file_name,
                "checkset_redis_name": checkset_redis_name,
                "current status": STATUSES.STATUS_CHECKSET_TEST_START_EN,
                "checkset_data_list": checkset_data_list,
            },
            status_code=status.HTTP_202_ACCEPTED)

        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        reset_color = CONSOLE_COLORS.RESET
        print(f"message: BERT model check-set testing start [OK]\n"
              f"BERT response.body: {json_response.body}\n"
              f"BERT response.status_code: {json_response.status_code}\n"
              f"username: {auth_data.username}\n"
              f"model init: {BERT_OPTIONS.BERT_MODEL_INIT}\n"
              f"model name: {BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED}\n"
              f"model path: {BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH}\n"
              f"checkset_file_name: {blue_color}{checkset_file_name}{reset_color}\n",
              f"checkset_redis_name: {blue_color}{checkset_redis_name}{reset_color}\n"
              f"checkset_data_list: {checkset_data_list}\n")
        print("####### PRELIMINARY 202 RESPONSE AFTER BACKGROUND CHECKSET TEST START")
        return json_response
    except Exception as error:
        log_text = f"BERT router check-set test model [ERROR]: error: {error}"
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
