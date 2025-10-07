# import asyncio
# from functools import partial
import os
from datetime import datetime
from typing import Annotated

from fastapi import (
    APIRouter, File, Form, HTTPException, UploadFile, status, Depends)
from fastapi.responses import JSONResponse

from ML_BERT_classifier.class_bert import ClassifierBERT
from configs.console_colors import CONSOLE_COLORS
from configs.settings import (
    BERT_OPTIONS)
from db_postgres.postgres_dependencies.dep_get_bert_model_instance import (
    get_bert_model_instance_dep)
from fast_api.app_account_data.scheme_account_data import AccountDataBert
from fast_api.app_add_texts_categories_file.func_add_save_text_category_file import (
    add_save_multi_text_category_file)
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from utils_common.class_file_validate_read import FileValidateRead

bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_bert_add_text_category_file = APIRouter(prefix=f"/{bert_base_url_name}",
                                               tags=["BERT"])


@router_bert_add_text_category_file.post(path="/bert_add_text_category_file/",
                                         # TODO: Describe responses here
                                         response_model=None)
async def bert_add_text_category_file(
        upload_file: Annotated[UploadFile, File(description="file .xls, .xlsx, or .txt")],
        username: Annotated[str, Form()],
        password: Annotated[str, Form()],
        account_id: Annotated[str, Form()],
        account_username: Annotated[str, Form()],
        bert_model_inst: Annotated[
            ClassifierBERT, Depends(get_bert_model_instance_dep)],
) -> JSONResponse:
    verify_prod_username_password(username=username,
                                  password=password)

    account_data = AccountDataBert(account_id=account_id,
                                   account_username=account_username)

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
    _, file_extension = os.path.splitext(file_name)
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
    update_data_list = []
    error_flag_text = ""
    if file_extension.endswith((".xlsx", ".xls")):
        if await file_valid_read.validate_content_excel():
            update_data_list = await file_valid_read.read_file_excel()
        else:
            error_flag_text = "File excel content [ERROR]"
    elif file_extension.endswith("txt"):
        if await file_valid_read.validate_content_txt():
            update_data_list = await file_valid_read.read_file_txt()
        else:
            error_flag_text = "File txt content [ERROR]"
    elif file_extension.endswith("csv"):
        if await file_valid_read.validate_content_csv():
            update_data_list = await file_valid_read.read_file_csv()
        else:
            error_flag_text = "File csv content [ERROR]"

    if error_flag_text:
        log_text = (f"{error_flag_text}:\n"
                    f"upload_file.filename: {upload_file.filename}\n"
                    f"upload_file.content_type: {upload_file.content_type}\n"
                    f"file_extension: {file_extension}\n"
                    f"update_data_list: {update_data_list}")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=log_text)

    if not update_data_list:
        log_text = (f"Empty upload file [ERROR]:\n"
                    f"upload_file.filename: {upload_file.filename}\n"
                    f"upload_file.content_type: {upload_file.content_type}\n"
                    f"file_extension: {file_extension}\n"
                    f"update_data_list: {update_data_list}")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=log_text)

    try:
        datetime_start = datetime.now()
        new_csv_files_data = await add_save_multi_text_category_file(
            account_data=account_data,
            update_text_category_data=update_data_list,
            bert_model_inst=bert_model_inst)
        adding_time = (datetime.now() - datetime_start).total_seconds()
        adding_time = round(adding_time, 1)

        new_lab_cat_csv_path = new_csv_files_data.get("lab_cat_csv_path")
        new_text_lab_csv_path = new_csv_files_data.get("text_lab_csv_path")
        dataset_ini_file_path = new_csv_files_data.get("last_saved_dataset_ini_fpath")
        empty_error_skipped_rows = new_csv_files_data.get("empty_error_skipped_rows")
        new_categories_list = new_csv_files_data.get("new_categories_list")

        json_content = {
            "message": "BERT text-category csv added [OK]",
            "username": username,
            "dataset init": BERT_OPTIONS.BERT_INITIAL_DATASET_CSV_PATH,
            "csv label-category path": new_lab_cat_csv_path,
            "csv text-label path:": new_text_lab_csv_path,
            "dataset ini file path": dataset_ini_file_path,
            "adding time": adding_time,
            "update data list": update_data_list,
            "empty error skipped rows": empty_error_skipped_rows,
            "new categories": new_categories_list}

        json_response = JSONResponse(
            content=json_content,
            status_code=status.HTTP_200_OK)

        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        yellow_color = CONSOLE_COLORS.BRIGHT_YELLOW
        reset_color = CONSOLE_COLORS.RESET
        print(f"BERT response message: {json_content.get('message')}\n"
              f"BERT response.body keys: {json_content.keys()}\n"
              # f"BERT response.body: {json_response.body}\n"  # Long to log
              f"BERT response.status_code: {json_response.status_code}\n"
              f"username: {username}\n"
              f"new_lab_cat_csv_path: {new_lab_cat_csv_path}\n"
              f"new_text_lab_csv_path: {new_text_lab_csv_path}\n"
              f"dataset_ini_file_path: {dataset_ini_file_path}\n"
              f"update_data_list: {blue_color}{update_data_list}{reset_color}\n"
              f"empty_error_skipped_rows: {yellow_color}{empty_error_skipped_rows}{reset_color}\n"
              f"new_categories_list: {blue_color}{new_categories_list}{reset_color}\n")
        return json_response
    except Exception as error:
        log_text = f"BERT router [ERROR]: error: {error}"
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
