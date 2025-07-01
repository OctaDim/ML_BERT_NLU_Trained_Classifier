# import asyncio
# from functools import partial
import os
import re

import pandas
import shutil
from datetime import datetime
from typing import Annotated, Tuple

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from ML_BERT_classifier.init_bert import bert_model_inst
from configs.console_colors import CONSOLE_COLORS
from configs.settings import (
    BASE_DIR, BERT_OPTIONS)
from fast_api.app_add_texts_categories_file.scheme_add_texts_cetegories_file import (
    TextCategoryFileData)
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from fast_api.app_auth.scheme_auth import AuthDataBert
from utils_common.normalized_path import (
    get_full_dir_normal_path, get_full_file_normal_path)
from utils_common.class_file_validate_read import FileValidateRead
from utils_specific.class_csv_labels_categories import CsvLabelCategory
from utils_specific.class_csv_texts_labels import CsvTextLabel
from utils_specific.new_dataset_dir_path import get_new_dataset_dir_path


bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_bert_add_text_category_file = APIRouter(prefix=f"/{bert_base_url_name}",
                                               tags=["BERT"])


@router_bert_add_text_category_file.post(path="/bert_add_text_category_file/",
                                         # TODO: Describe responses here
                                         response_model=None)
async def bert_add_text_category_file(
        upload_file: Annotated[UploadFile, File(description="file .xls, .xlsx, or .txt")],
        username: Annotated[str, Form()] = "temp_zxc",
        password: Annotated[str, Form()] = "temp_123",
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
    data_list = []
    error_flag_text = ""
    if file_extension.endswith((".xlsx", ".xls")):
        if await file_valid_read.validate_content_excel():
            data_list = await file_valid_read.read_file_excel()
        else:
            error_flag_text = "File excel content [ERROR]:\n"
    elif file_extension.endswith("txt"):
        if await file_valid_read.validate_content_txt():
            data_list = await file_valid_read.read_file_txt()
        else:
            error_flag_text = "File txt content [ERROR]:\n"
    elif file_extension.endswith("csv"):
        if await file_valid_read.validate_content_csv():
            data_list = await file_valid_read.read_file_csv()
        else:
            error_flag_text = "File csv content [ERROR]:\n"

    if error_flag_text:
        log_text = (f"{error_flag_text}"
                    f"upload_file.filename: {upload_file.filename}\n"
                    f"upload_file.content_type: {upload_file.content_type}\n"
                    f"file extension: {file_extension}\n")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=log_text)

    print(type(data_list), "#########", data_list)
    print()
    for elem in data_list:
        print(type(elem), "#########", elem)
    print()

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=data_list)

    # update_text = update_text.strip().lower()
    # update_category = update_category.strip().lower()
    #
    # last_saved_dataset_ini_dir = ""
    # last_saved_dataset_ini_path = ""
    #
    # try:
    #     last_saved_dataset_ini_path = get_full_file_normal_path(
    #         all_dir_str_parts=[BASE_DIR],
    #         file_name_with_ext=BERT_OPTIONS.BERT_LAST_SAVED_DATASET_INI_FILE_PATH)
    #
    #     if os.path.isfile(last_saved_dataset_ini_path):
    #         with open(file=last_saved_dataset_ini_path,
    #                   mode="r", encoding="utf-8") as dataset_ini_file:
    #             dataset_ini_file.seek(0)
    #             dataset_file_saved_path = dataset_ini_file.read()
    #     else:
    #         dataset_file_saved_path = ""
    # except Exception as error:
    #     dataset_file_saved_path = ""  # not necessary, for reliability
    #     print(f"Read last model saved ini file [ERROR]: error: {error}, "
    #           f"last_saved_dataset_ini_dir: {last_saved_dataset_ini_dir}, "
    #           f"last_saved_dataset_ini_path: {last_saved_dataset_ini_path}")
    #
    # if bert_model_inst.last_saved_dataset_dir:
    #     prev_dataset_dir_path = bert_model_inst.last_saved_dataset_dir
    # elif dataset_file_saved_path:
    #     prev_dataset_dir_path = dataset_file_saved_path
    # else:
    #     initial_dataset_dir = BERT_OPTIONS.BERT_INITIAL_DATASET_CSV_PATH
    #     prev_dataset_dir_path = get_full_dir_normal_path(
    #         [BASE_DIR, initial_dataset_dir])
    #
    # if not all([os.path.exists(prev_dataset_dir_path),
    #             os.path.isdir(prev_dataset_dir_path)]):
    #     log_text = (f"Data-set initial or saved dir path not found [ERROR]: "
    #                 f"prev_dataset_dir_path: {prev_dataset_dir_path}")
    #     print(log_text)
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail=log_text)
    #
    # try:
    #     print("\nAdding new text-category pair:")
    #     datetime_start = datetime.now()
    #     prev_lab_cat_csv_path = get_full_file_normal_path(
    #         all_dir_str_parts=[prev_dataset_dir_path],
    #         file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)
    #
    #     with open(file=prev_lab_cat_csv_path,
    #               mode="r", encoding="utf-8") as prev_csv1_file:
    #         csf_lab_cat = CsvLabelCategory(prev_csv1_file)
    #         lab_cat_dict = csf_lab_cat.get_label_category_dict()
    #
    #     if not lab_cat_dict:
    #         log_text = (f"Empty or wrong label-category csv data [ERROR]: "
    #                     f"prev_lab_cat_csv_path: {prev_lab_cat_csv_path}, "
    #                     f"lab_cat_dict: {lab_cat_dict}\n")
    #         print(log_text)
    #         raise HTTPException(
    #             status_code=status.HTTP_406_NOT_ACCEPTABLE,
    #             detail=log_text)
    #
    #     next_label_value = None
    #     new_lab_cat_csv_path = None
    #     new_dataset_dir_path = get_new_dataset_dir_path()
    #
    #     if update_category not in lab_cat_dict.values():
    #         next_label_value = max(lab_cat_dict.keys()) + 1
    #         lab_cat_dict[next_label_value] = update_category
    #
    #         if BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:
    #             new_lab_cat_csv_path = prev_lab_cat_csv_path
    #             with open(file=new_lab_cat_csv_path, mode="a",
    #                       encoding="utf-8", newline="") as prev_csv1_file:
    #                 csv_lab_cat = CsvLabelCategory(prev_csv1_file)
    #                 csv_lab_cat.add_new_label_category_row(
    #                     new_label=next_label_value,
    #                     new_category=update_category)
    #         else:
    #             os.makedirs(name=new_dataset_dir_path, exist_ok=True)
    #             new_lab_cat_csv_path = get_full_file_normal_path(
    #                 all_dir_str_parts=[new_dataset_dir_path],
    #                 file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)
    #             shutil.copy2(src=prev_lab_cat_csv_path,
    #                          dst=new_lab_cat_csv_path)
    #             with open(file=new_lab_cat_csv_path, mode="a",
    #                       encoding="utf-8", newline="") as new_csv1_file:
    #                 csv_lab_cat = CsvLabelCategory(new_csv1_file)
    #                 csv_lab_cat.add_new_label_category_row(
    #                     new_label=next_label_value,
    #                     new_category=update_category)
    #     else:
    #         if not BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:
    #             os.makedirs(new_dataset_dir_path)
    #             new_lab_cat_csv_path = get_full_file_normal_path(
    #                 all_dir_str_parts=[new_dataset_dir_path],
    #                 file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)
    #             shutil.copy2(src=prev_lab_cat_csv_path,
    #                          dst=new_lab_cat_csv_path)
    #
    #     print("\nAdding new text-label pair:")
    #     prev_text_lab_csv_path = get_full_file_normal_path(
    #         all_dir_str_parts=[prev_dataset_dir_path],
    #         file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)
    #
    #     with open(file=prev_text_lab_csv_path,
    #               mode="r", encoding="utf-8") as prev_csv2_file:
    #         csf_text_lab = CsvTextLabel(prev_csv2_file)
    #         text_lab_dict = csf_text_lab.get_text_label_dict()
    #
    #     if not text_lab_dict:
    #         log_text = (f"Empty or wrong text-label csv data [ERROR]: "
    #                     f"prev_text_lab_csv_path: {prev_text_lab_csv_path}, "
    #                     f"text_lab_dict: {text_lab_dict}\n")
    #         print(log_text)
    #         raise HTTPException(
    #             status_code=status.HTTP_406_NOT_ACCEPTABLE,
    #             detail=log_text)
    #
    #     cur_label = None
    #     if not next_label_value:
    #         for label, category in lab_cat_dict.items():
    #             if category == update_category:
    #                 cur_label = label
    #                 break
    #     else:
    #         cur_label = next_label_value
    #
    #     if BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:
    #         new_text_lab_csv_path = prev_text_lab_csv_path
    #         with open(file=prev_text_lab_csv_path, mode="a",
    #                   encoding="utf-8", newline="") as prev_csv2_file:
    #             csv_text_lab = CsvTextLabel(prev_csv2_file)
    #             csv_text_lab.add_new_text_label_row(
    #                 new_text=update_text,
    #                 new_label=cur_label)
    #     else:
    #         os.makedirs(name=new_dataset_dir_path, exist_ok=True)
    #         new_text_lab_csv_path = get_full_file_normal_path(
    #             all_dir_str_parts=[new_dataset_dir_path],
    #             file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)
    #
    #         shutil.copy2(src=prev_text_lab_csv_path,
    #                      dst=new_text_lab_csv_path)
    #
    #         with open(file=new_text_lab_csv_path, mode="a",
    #                   encoding="utf-8", newline="") as new_csv2_file:
    #             csv_text_lab = CsvTextLabel(new_csv2_file)
    #             csv_text_lab.add_new_text_label_row(
    #                 new_text=update_text,
    #                 new_label=cur_label)
    #         bert_model_inst.last_saved_dataset_dir = new_dataset_dir_path
    #
    #     last_saved_dataset_ini_fpath = get_full_file_normal_path(
    #         all_dir_str_parts=[BASE_DIR],
    #         file_name_with_ext=BERT_OPTIONS.BERT_LAST_SAVED_DATASET_INI_FILE_PATH)
    #     last_saved_dataset_ini_dir = os.path.dirname(
    #         last_saved_dataset_ini_fpath)
    #     os.makedirs(name=last_saved_dataset_ini_dir, exist_ok=True)
    #
    #     with open(file=last_saved_dataset_ini_fpath,
    #               mode="w", encoding="utf-8") as dataset_ini_file:
    #         dataset_ini_file.write(new_dataset_dir_path)
    #
    #     adding_time = (datetime.now() - datetime_start).total_seconds()
    #     adding_time = round(adding_time, 1)
    #
    #     json_response = JSONResponse(
    #         content={"message": "BERT text-category csv added [OK]",
    #                  "username": auth_data.username,
    #                  "dataset init": BERT_OPTIONS.BERT_INITIAL_DATASET_CSV_PATH,
    #                  "csv label-category path": new_lab_cat_csv_path,
    #                  "csv text-label path:": new_text_lab_csv_path,
    #                  "adding time": adding_time,
    #                  "added text": update_text,
    #                  "added category": update_category},
    #         status_code=status.HTTP_200_OK)
    #
    #     blue_color = CONSOLE_COLORS.BRIGHT_BLUE
    #     reset_color = CONSOLE_COLORS.RESET
    #     print(f"BERT response.body: {json_response.body}\n"
    #           f"BERT response.status_code: {json_response.status_code}\n"
    #           f"username: {auth_data.username}\n"
    #           f"csv label-category path: {new_lab_cat_csv_path}\n"
    #           f"csv text-label path: {new_text_lab_csv_path}\n"
    #           f"added text: {blue_color}{update_text}{reset_color}\n"
    #           f"added category: {blue_color}{update_category}{reset_color}\n")
    #     return json_response
    # except Exception as error:
    #     log_text = f"BERT router [ERROR]: error: {error}"
    #     print(log_text)
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail=log_text)
