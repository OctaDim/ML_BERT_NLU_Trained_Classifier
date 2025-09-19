# import asyncio
# from functools import partial
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from ML_BERT_classifier.init_bert import bert_model_inst
from configs.console_colors import CONSOLE_COLORS
from configs.settings import BERT_MODEL_NAMES, BERT_OPTIONS
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from fast_api.app_auth.scheme_auth import AuthDataBert
from utils_common.normalized_path import get_full_file_normal_path
from utils_specific.class_csv_labels_categories import CsvLabelCategory
from utils_specific.class_csv_texts_labels import CsvTextLabel
from utils_specific.get_initial_dataset_dir_path import (
    get_initial_dataset_dir_path)
from utils_specific.get_last_saved_dataset_path import (
    get_last_saved_dataset_dir_path)

bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_bert_get_all_categories_texts = APIRouter(prefix=f"/{bert_base_url_name}",
                                                 tags=["BERT"])


@router_bert_get_all_categories_texts.post(path="/bert_get_categories_texts_dict/",
                                           # TODO: Describe responses here
                                           response_model=None)
async def bert_get_categories_texts_dict(auth_data: AuthDataBert):
    verify_prod_username_password(username=auth_data.username,
                                  password=auth_data.password)
    try:
        datetime_start = datetime.now()
        print("\nGetting last saved dataset directory name:")
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

        print("\nGetting non-titled categories list:")
        lab_cat_file_name = BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME
        csv_lab_cat_file_path = get_full_file_normal_path(
            all_dir_str_parts=[last_dataset_dir],
            file_name_with_ext=lab_cat_file_name)

        with open(file=csv_lab_cat_file_path,
                  mode="r", encoding="utf-8") as csv_lab_cat_file:
            csf_lab_cat = CsvLabelCategory(csv_file_obj=csv_lab_cat_file)
            dataset_lab_cat_dict = csf_lab_cat.get_label_category_dict()
        # print(f"dataset_lab_cat_dict => {dataset_lab_cat_dict}")  # Too long
        print(f"len(dataset_lab_cat_dict) => {len(dataset_lab_cat_dict)}")

        lab_txt_file_name = BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME
        csv_lab_txt_file_path = get_full_file_normal_path(
            all_dir_str_parts=[last_dataset_dir],
            file_name_with_ext=lab_txt_file_name)

        with open(file=csv_lab_txt_file_path,
                  mode="r", encoding="utf-8") as csv_lab_txt_file:
            csf_lab_txt = CsvTextLabel(csv_file_obj=csv_lab_txt_file)
            dataset_lab_txt_dict = csf_lab_txt.get_text_label_dict()
        # print(f"dataset_lab_txt_dict => {dataset_lab_txt_dict}")  # Too long
        print(f"len(dataset_lab_txt_dict) => {len(dataset_lab_txt_dict)}")

        # Single loop
        category_texts_dict = {}
        for cur_text, cur_text_label in dataset_lab_txt_dict.items():
            category_name = dataset_lab_cat_dict[cur_text_label]
            cur_category_texts_list = category_texts_dict.setdefault(category_name, [])
            cur_category_texts_list.append(cur_text)
            category_texts_dict[category_name] = cur_category_texts_list

        # Double loop
        # category_texts_dict = {}
        # for cur_category_label, cur_category in dataset_lab_cat_dict.items():
        #     cur_category_texts = []
        #     for cur_text, cur_text_label in dataset_lab_txt_dict.items():
        #         if cur_text_label == cur_category_label:
        #             cur_category_texts.append(cur_text)
        #     category_texts_dict[cur_category] = cur_category_texts

        getting_time = (datetime.now() - datetime_start).total_seconds()
        getting_time = round(getting_time, 1)

        json_response = JSONResponse(
            content={"message": "BERT text-phrase categorised [OK]",
                     "username": auth_data.username,
                     "model init": BERT_OPTIONS.BERT_MODEL_INIT,
                     "model name": BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED,
                     "model path": BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH,
                     "getting time": getting_time,
                     # "dataset_lab_cat_dict": dataset_lab_cat_dict,
                     # "dataset_lab_txt_dict": dataset_lab_txt_dict,
                     "category_texts_dict": category_texts_dict
                     },
            status_code=status.HTTP_200_OK)

        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        reset_color = CONSOLE_COLORS.RESET
        print(f"BERT response.body: {json_response.body}\n"
              f"BERT response.status_code: {json_response.status_code}\n"
              f"username: {auth_data.username}\n"
              f"len(category_texts_dict): {len(category_texts_dict)}\n"
              # f"category_texts_dict: {category_texts_dict}\n"  # Too long
              # f"dataset_lab_cat_dict: {dataset_lab_cat_dict}\n"
              # f"dataset_lab_txt_dict: {dataset_lab_txt_dict}\n"
              f"getting_time: {getting_time}\n")
        return json_response
    except Exception as error:
        log_text = f"BERT router [ERROR]: error: {error}"
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
