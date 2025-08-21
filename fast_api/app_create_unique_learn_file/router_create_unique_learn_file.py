# import asyncio
# from functools import partial
import os
import random
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from configs.console_colors import CONSOLE_COLORS
from configs.settings import (
    BERT_OPTIONS, BASE_DIR)
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from utils_common.class_file_validate_read import FileValidateRead
from utils_common.get_file_name_extra_part import get_file_name_with_extra_part
from utils_common.normalized_path import get_full_file_normal_path

bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_bert_create_unique_learn_file = APIRouter(prefix=f"/{bert_base_url_name}",
                                                 tags=["BERT"])


@router_bert_create_unique_learn_file.post(path="/bert_create_unique_learn_file/",
                                           # TODO: Describe responses here
                                           response_model=None)
async def bert_create_unique_learn_file(
        upload_file: Annotated[UploadFile, File(description="file .xls, .xlsx, or .txt")],
        username: Annotated[str, Form()],
        password: Annotated[str, Form()],
):
    verify_prod_username_password(username=username,
                                  password=password)

    ALLOWED_FILE_MIME_TYPES = (
        "application/vnd.ms-excel",  # xls, old excel
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # xlsx, new excel
        "text/csv", "application/csv",  # csv
        "text/plain",  # txt
    )

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
    file_name = os.path.basename(upload_file.filename)
    filename_no_ext, file_extension = os.path.splitext(file_name)
    file_extension = file_extension.lower()
    if not file_name.lower().endswith(allowed_extensions):
        log_text = (f"File extension not xls, xlsx, csv or txt [ERROR]:\n"
                    f"upload_file.filename: {upload_file.filename}\n"
                    f"file extension: {file_extension}\n"
                    f"allowed extensions: {allowed_extensions}\n")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=log_text)

    file_valid_read = FileValidateRead(file=upload_file)
    learn_data_list = []
    error_flag_text = ""
    if file_extension.endswith((".xlsx", ".xls")):
        if await file_valid_read.validate_content_excel():
            learn_data_list = await file_valid_read.read_file_excel()
        else:
            error_flag_text = "File excel content [ERROR]"
    elif file_extension.endswith("txt"):
        if await file_valid_read.validate_content_txt():
            learn_data_list = await file_valid_read.read_file_txt()
        else:
            error_flag_text = "File txt content [ERROR]"
    elif file_extension.endswith("csv"):
        if await file_valid_read.validate_content_csv():
            learn_data_list = await file_valid_read.read_file_csv()
        else:
            error_flag_text = "File csv content [ERROR]"

    if error_flag_text:
        log_text = (f"{error_flag_text}:\n"
                    f"upload_file.filename: {upload_file.filename}\n"
                    f"upload_file.content_type: {upload_file.content_type}\n"
                    f"file_extension: {file_extension}\n"
                    f"learn_data_list: {learn_data_list}")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=log_text)

    if not learn_data_list:
        log_text = (f"Empty upload file [ERROR]:\n"
                    f"upload_file.filename: {upload_file.filename}\n"
                    f"upload_file.content_type: {upload_file.content_type}\n"
                    f"file_extension: {file_extension}\n"
                    f"learn_data_list: {learn_data_list}")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=log_text)

    try:
        print("\nBERT Creating new learn filename full path with extra part:")
        datetime_start = datetime.now()
        datetime_str = datetime.now().strftime("%d_%m_%Y_%H_%M_%S_%f")
        random_str = str(random.randint(10000, 99999))
        learn_file_prefix = BERT_OPTIONS.BERT_UNIQUE_LEARNING_FILE_PREFIX
        new_learn_file_name = (f"{filename_no_ext}_{learn_file_prefix}_"
                               f"{datetime_str}_{random_str}.csv")

        learn_files_dir_name = BERT_OPTIONS.BERT_UNIQUE_LEARNING_FILES_PATH
        learn_file_save_path = get_full_file_normal_path(
            all_dir_str_parts=[BASE_DIR, learn_files_dir_name],
            file_name_with_ext=new_learn_file_name)
        print("###########################################################")
        print("@@@@@@@ file_name:", file_name)
        print("@@@@@@@ new_learn_file_name:", new_learn_file_name)
        print("@@@@@@@ learn_file_save_path:", learn_file_save_path)

        print("@@@@@@@ len(learn_data_list):", len(learn_data_list))
        learn_data_tuples_list = [tuple(cur_list) for cur_list in learn_data_list]
        unique_learn_data = list(set(learn_data_tuples_list))

        print("@@@@@@@ len(unique_learn_data):", len(unique_learn_data))
        print("###########################################################")
        # unique_learn_data = unify_save_inque_learn_file(learn_data_list)
        creating_time = (datetime.now() - datetime_start).total_seconds()
        creating_time = round(creating_time, 1)

        print("\nBERT Creating new learn filename full path with extra part:")

        json_response = JSONResponse(
            content={"message": "BERT text-category csv added [OK]",
                     "username": username,
                     "dataset init": BERT_OPTIONS.BERT_INITIAL_DATASET_CSV_PATH,
                     # "csv label-category path": new_lab_cat_csv_path,
                     # "csv text-label path:": new_text_lab_csv_path,
                     # "dataset ini file path": dataset_ini_file_path,
                     "creating_time": creating_time,
                     # "learn_data_list": learn_data_list,
                     # "empty error skipped rows": empty_error_skipped_rows,
                     # "new categories": new_categories_list,
                     },
            status_code=status.HTTP_200_OK)

        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        # yellow_color = CONSOLE_COLORS.BRIGHT_YELLOW
        reset_color = CONSOLE_COLORS.RESET
        print(f"BERT response.body: {json_response.body}\n"
              f"BERT response.status_code: {json_response.status_code}\n"
              f"username: {username}\n"
              # f"new_lab_cat_csv_path: {new_lab_cat_csv_path}\n"
              # f"new_text_lab_csv_path: {new_text_lab_csv_path}\n"
              # f"dataset_ini_file_path: {dataset_ini_file_path}\n"
              # f"learn_data_list: {blue_color}{learn_data_list}{reset_color}\n"
              # f"empty_error_skipped_rows: {yellow_color}{empty_error_skipped_rows}{reset_color}\n"
              # f"new_categories_list: {blue_color}{new_categories_list}{reset_color}\n"
              )
        return json_response
    except Exception as error:
        log_text = f"BERT router [ERROR]: error: {error}"
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
