# import asyncio
# from functools import partial
import os
import shutil
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from ML_BERT_classifier.init_bert import bert_model_inst
from configs.console_colors import CONSOLE_COLORS
from configs.settings import (
    BASE_DIR, BERT_OPTIONS)
from fast_api.app_add_text_category.scheme_add_text_category import (
    TextCategoryDataBert)
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from fast_api.app_auth.scheme_auth import AuthDataBert
from utils_common.normalized_path import (
    get_full_dir_normal_path, get_full_file_normal_path)
from utils_specific.class_csv_labels_categories import CsvLabelCategory
from utils_specific.class_csv_texts_labels import CsvTextLabel
from utils_specific.new_dataset_dir_path import get_new_dataset_dir_path


bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_bert_add_text_category = APIRouter(prefix=f"/{bert_base_url_name}",
                                          tags=["BERT"])


@router_bert_add_text_category.post(path="/bert_add_text_category/",
                                    # TODO: Describe responses here
                                    response_model=None)
async def bert_add_text_category(auth_data: AuthDataBert,
                                 text_category_data: TextCategoryDataBert):
    verify_prod_username_password(username=auth_data.username,
                                  password=auth_data.password)

    update_text = text_category_data.update_text
    update_category = text_category_data.update_category

    if not update_text or not update_category:
        log_text = (f"Empty text or category [ERROR]: "
                    f"text_category_data.update_text: {update_text}, "
                    f"text_category_data.update_category: {update_category}\n")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=log_text)

    update_text = update_text.strip().lower()
    update_category = update_category.strip().lower()

    if bert_model_inst.last_saved_dataset_dir:
        prev_dataset_dir_path = bert_model_inst.last_saved_dataset_dir
    else:
        initial_dataset_dir = BERT_OPTIONS.BERT_INITIAL_DATASET_CSV_PATH
        prev_dataset_dir_path = get_full_dir_normal_path(
            [BASE_DIR, initial_dataset_dir])

    try:
        print("\nAdding new text-category pair:")
        datetime_start = datetime.now()
        prev_lab_cat_csv_path = get_full_file_normal_path(
            all_dir_str_parts=[prev_dataset_dir_path],
            file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_NAME)

        with open(file=prev_lab_cat_csv_path,
                  mode="r", encoding="utf-8") as prev_csv1_file:
            csf_lab_cat = CsvLabelCategory(prev_csv1_file)
            lab_cat_dict = csf_lab_cat.get_label_category_dict()

        if not lab_cat_dict:
            log_text = (f"Empty or wrong label-category csv data [ERROR]: "
                        f"prev_lab_cat_csv_path: {prev_lab_cat_csv_path}, "
                        f"lab_cat_dict: {lab_cat_dict}\n")
            print(log_text)
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=log_text)

        next_label_value = None
        new_lab_cat_csv_path = None
        new_dataset_dir_path = get_new_dataset_dir_path()

        if update_category not in lab_cat_dict.values():
            next_label_value = max(lab_cat_dict.keys()) + 1
            lab_cat_dict[next_label_value] = update_category

            if BERT_OPTIONS.BERT_OVERWRITE_DATASET_CSV:
                new_lab_cat_csv_path = prev_lab_cat_csv_path
                with open(file=new_lab_cat_csv_path, mode="a",
                          encoding="utf-8", newline="") as prev_csv1_file:
                    csv_lab_cat = CsvLabelCategory(prev_csv1_file)
                    csv_lab_cat.add_new_label_category_row(
                        new_label=next_label_value,
                        new_category=update_category)
            else:
                os.makedirs(name=new_dataset_dir_path, exist_ok=True)
                new_lab_cat_csv_path = get_full_file_normal_path(
                    all_dir_str_parts=[new_dataset_dir_path],
                    file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_NAME)
                shutil.copy2(src=prev_lab_cat_csv_path,
                             dst=new_lab_cat_csv_path)
                with open(file=new_lab_cat_csv_path, mode="a",
                          encoding="utf-8", newline="") as new_csv1_file:
                    csv_lab_cat = CsvLabelCategory(new_csv1_file)
                    csv_lab_cat.add_new_label_category_row(
                        new_label=next_label_value,
                        new_category=update_category)
        else:
            if not BERT_OPTIONS.BERT_OVERWRITE_DATASET_CSV:
                os.makedirs(new_dataset_dir_path)
                new_lab_cat_csv_path = get_full_file_normal_path(
                    all_dir_str_parts=[new_dataset_dir_path],
                    file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_NAME)
                shutil.copy2(src=prev_lab_cat_csv_path,
                             dst=new_lab_cat_csv_path)

        print("\nAdding new text-label pair:")
        prev_text_lab_csv_path = get_full_file_normal_path(
            all_dir_str_parts=[prev_dataset_dir_path],
            file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_NAME)

        with open(file=prev_text_lab_csv_path,
                  mode="r", encoding="utf-8") as prev_csv2_file:
            csf_text_lab = CsvTextLabel(prev_csv2_file)
            text_lab_dict = csf_text_lab.get_text_label_dict()

        if not text_lab_dict:
            log_text = (f"Empty or wrong text-label csv data [ERROR]: "
                        f"prev_text_lab_csv_path: {prev_text_lab_csv_path}, "
                        f"text_lab_dict: {text_lab_dict}\n")
            print(log_text)
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=log_text)

        cur_label = None
        if not next_label_value:
            for label, category in lab_cat_dict.items():
                if category == update_category:
                    cur_label = label
                    break
        else:
            cur_label = next_label_value

        if BERT_OPTIONS.BERT_OVERWRITE_DATASET_CSV:
            new_text_lab_csv_path = prev_text_lab_csv_path
            with open(file=prev_text_lab_csv_path, mode="a",
                      encoding="utf-8", newline="") as prev_csv2_file:
                csv_text_lab = CsvTextLabel(prev_csv2_file)
                csv_text_lab.add_new_text_label_row(
                    new_text=update_text,
                    new_label=cur_label)
        else:
            os.makedirs(name=new_dataset_dir_path, exist_ok=True)
            new_text_lab_csv_path = get_full_file_normal_path(
                all_dir_str_parts=[new_dataset_dir_path],
                file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_NAME)

            shutil.copy2(src=prev_text_lab_csv_path,
                         dst=new_text_lab_csv_path)

            with open(file=new_text_lab_csv_path, mode="a",
                      encoding="utf-8", newline="") as new_csv2_file:
                csv_text_lab = CsvTextLabel(new_csv2_file)
                csv_text_lab.add_new_text_label_row(
                    new_text=update_text,
                    new_label=cur_label)
            bert_model_inst.last_saved_dataset_dir = new_dataset_dir_path

        adding_time = (datetime.now() - datetime_start).total_seconds()
        adding_time = round(adding_time, 1)

        json_response = JSONResponse(
            content={"message": "BERT text-category csv added [OK]",
                     "username": auth_data.username,
                     "dataset init": BERT_OPTIONS.BERT_INITIAL_DATASET_CSV_PATH,
                     "csv label-category path": new_lab_cat_csv_path,
                     "csv text-label path:": new_text_lab_csv_path,
                     "adding time": adding_time,
                     "added text": update_text,
                     "added category": update_category},
            status_code=status.HTTP_200_OK)

        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        reset_color = CONSOLE_COLORS.RESET
        print(f"BERT response.body: {json_response.body}\n"
              f"BERT response.status_code: {json_response.status_code}\n"
              f"username: {auth_data.username}\n"
              f"csv label-category path: {new_lab_cat_csv_path}\n"
              f"csv text-label path: {new_text_lab_csv_path}\n"
              f"added text: {blue_color}{update_text}{reset_color}\n"
              f"added category: {blue_color}{update_category}{reset_color}\n")
        return json_response
    except Exception as error:
        log_text = f"BERT router [ERROR]: error: {error}"
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
