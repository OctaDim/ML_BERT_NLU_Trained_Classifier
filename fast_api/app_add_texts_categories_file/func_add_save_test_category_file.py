# import asyncio
# from functools import partial
import os
import shutil
from datetime import datetime

from fastapi import HTTPException, status

from ML_BERT_classifier.init_bert import bert_model_inst
from configs.settings import (
    BASE_DIR, BERT_OPTIONS)
from utils_common.normalized_path import (
    get_full_dir_normal_path, get_full_file_normal_path)
from utils_specific.class_csv_labels_categories import CsvLabelCategory
from utils_specific.class_csv_texts_labels import CsvTextLabel
from utils_specific.new_dataset_dir_path import get_new_dataset_dir_path


def add_save_multi_text_category_file(update_text_category_data: list) -> dict:
    last_saved_dataset_ini_dir = ""
    last_saved_dataset_ini_path = ""

    try:
        last_saved_dataset_ini_path = get_full_file_normal_path(
            all_dir_str_parts=[BASE_DIR],
            file_name_with_ext=BERT_OPTIONS.BERT_LAST_SAVED_DATASET_INI_FILE_PATH)

        if os.path.isfile(last_saved_dataset_ini_path):
            with open(file=last_saved_dataset_ini_path,
                      mode="r", encoding="utf-8") as dataset_ini_file:
                dataset_ini_file.seek(0)
                dataset_file_saved_path = dataset_ini_file.read()
        else:
            dataset_file_saved_path = ""
    except Exception as error:
        dataset_file_saved_path = ""  # not necessary, for reliability
        print(f"Read last model saved ini file [ERROR]: error: {error}, "
              f"last_saved_dataset_ini_dir: {last_saved_dataset_ini_dir}, "
              f"last_saved_dataset_ini_path: {last_saved_dataset_ini_path}")

    if bert_model_inst.last_saved_dataset_dir:
        prev_dataset_dir_path = bert_model_inst.last_saved_dataset_dir
    elif dataset_file_saved_path:
        prev_dataset_dir_path = dataset_file_saved_path
    else:
        initial_dataset_dir = BERT_OPTIONS.BERT_INITIAL_DATASET_CSV_PATH
        prev_dataset_dir_path = get_full_dir_normal_path(
            [BASE_DIR, initial_dataset_dir])

    if not all([os.path.exists(prev_dataset_dir_path),
                os.path.isdir(prev_dataset_dir_path)]):
        log_text = (f"Data-set initial or saved dir path not found [ERROR]: "
                    f"prev_dataset_dir_path: {prev_dataset_dir_path}")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)

    try:
        print("\nGetting previous label-category dictionary:")
        prev_lab_cat_csv_path = get_full_file_normal_path(
            all_dir_str_parts=[prev_dataset_dir_path],
            file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)

        with open(file=prev_lab_cat_csv_path,
                  mode="r", encoding="utf-8") as prev_lab_cat_csv_file:
            csf_lab_cat = CsvLabelCategory(prev_lab_cat_csv_file)
            prev_lab_cat_dict = csf_lab_cat.get_label_category_dict()

        if not prev_lab_cat_dict:
            log_text = (f"Empty or wrong label-category csv data [ERROR]: "
                        f"prev_lab_cat_csv_path: {prev_lab_cat_csv_path}, "
                        f"prev_lab_cat_dict: {prev_lab_cat_dict}\n")
            print(log_text)
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=log_text)

        print("\nGetting previous text-label dictionary:")
        prev_text_lab_csv_path = get_full_file_normal_path(
            all_dir_str_parts=[prev_dataset_dir_path],
            file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)

        with open(file=prev_text_lab_csv_path,
                  mode="r", encoding="utf-8") as prev_text_lab_csv_file:
            csf_text_lab = CsvTextLabel(prev_text_lab_csv_file)
            prev_text_lab_dict = csf_text_lab.get_text_label_dict()

        if not prev_text_lab_dict:
            log_text = (f"Empty or wrong text-label csv data [ERROR]: "
                        f"prev_text_lab_csv_path: {prev_text_lab_csv_path}, "
                        f"prev_text_lab_dict: {prev_text_lab_dict}\n")
            print(log_text)
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=log_text)

        new_dataset_dir_path = get_new_dataset_dir_path()
        common_datetime_str = str(datetime.now())

        update_lab_cat_csv_list = []
        update_text_lab_csv_list = []
        empty_error_skipped_rows = []

        new_lab_cat_csv_path = None

        for cur_text_cat_pair in update_text_category_data:
            cur_update_text = cur_text_cat_pair[0].strip().lower()
            cur_update_category = cur_text_cat_pair[1].strip().lower()
            if not cur_update_text or not cur_update_category:
                print(f"Current row skipped, empty field value [ERROR]:\n"
                      f"cur_update_text: {cur_update_text}\n"
                      f"cur_update_category: {cur_update_category}\n")
                empty_error_skipped_rows.append(cur_text_cat_pair)
                continue

            print("\nAdding new label-category pair:")
            next_label_value = None
            if cur_update_category not in prev_lab_cat_dict.values():
                next_label_value = max(prev_lab_cat_dict.keys()) + 1
                prev_lab_cat_dict[next_label_value] = cur_update_category
                update_lab_cat_csv_list.append(
                    [common_datetime_str, next_label_value, cur_update_category])

            print("Adding new text-label pair:")
            cur_label = None
            if not next_label_value:  # Find existing category label
                for label, category in prev_lab_cat_dict.items():
                    if category == cur_update_category:
                        cur_label = label
                        break
            else:  # Use created category new label
                cur_label = next_label_value
            update_text_lab_csv_list.append(
                [common_datetime_str, cur_label, cur_update_text])

        print("\nSaving updated label-category csv file:")
        if update_lab_cat_csv_list:
            if BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:
                new_lab_cat_csv_path = prev_lab_cat_csv_path
                with open(file=new_lab_cat_csv_path, mode="a",
                          encoding="utf-8", newline="") as prev_lab_cat_csv_file:
                    csv_lab_cat = CsvLabelCategory(prev_lab_cat_csv_file)
                    csv_lab_cat.add_multi_label_category_rows(
                        update_label_category_data=update_lab_cat_csv_list)
            else:
                os.makedirs(name=new_dataset_dir_path, exist_ok=True)
                new_lab_cat_csv_path = get_full_file_normal_path(
                    all_dir_str_parts=[new_dataset_dir_path],
                    file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)
                shutil.copy2(src=prev_lab_cat_csv_path,
                             dst=new_lab_cat_csv_path)

                with open(file=new_lab_cat_csv_path, mode="a",
                          encoding="utf-8", newline="") as new_lab_cat_csv_file:
                    csv_lab_cat = CsvLabelCategory(new_lab_cat_csv_file)
                    csv_lab_cat.add_multi_label_category_rows(
                        update_label_category_data=update_lab_cat_csv_list)
        else:
            if not BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:
                os.makedirs(new_dataset_dir_path)
                new_lab_cat_csv_path = get_full_file_normal_path(
                    all_dir_str_parts=[new_dataset_dir_path],
                    file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)
                shutil.copy2(src=prev_lab_cat_csv_path,
                             dst=new_lab_cat_csv_path)

        print("\nSaving updated text-label csv file:")
        if BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:
            new_text_lab_csv_path = prev_text_lab_csv_path
            with open(file=prev_text_lab_csv_path, mode="a",
                      encoding="utf-8", newline="") as prev_text_lab_csv_file:
                csv_text_lab = CsvTextLabel(prev_text_lab_csv_file)
                csv_text_lab.add_multi_text_label_rows(
                    update_text_label_data=update_text_lab_csv_list)
        else:
            os.makedirs(name=new_dataset_dir_path, exist_ok=True)
            new_text_lab_csv_path = get_full_file_normal_path(
                all_dir_str_parts=[new_dataset_dir_path],
                file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)

            shutil.copy2(src=prev_text_lab_csv_path,
                         dst=new_text_lab_csv_path)

            with open(file=new_text_lab_csv_path, mode="a",
                      encoding="utf-8", newline="") as new_text_lab_csv_file:
                csv_text_lab = CsvTextLabel(new_text_lab_csv_file)
                csv_text_lab.add_multi_text_label_rows(
                    update_text_label_data=update_text_lab_csv_list)

        bert_model_inst.last_saved_dataset_dir = new_dataset_dir_path

        print("\nSaving updated dataset ini file path:")
        last_saved_dataset_ini_fpath = get_full_file_normal_path(
            all_dir_str_parts=[BASE_DIR],
            file_name_with_ext=BERT_OPTIONS.BERT_LAST_SAVED_DATASET_INI_FILE_PATH)
        last_saved_dataset_ini_dir = os.path.dirname(
            last_saved_dataset_ini_fpath)
        os.makedirs(name=last_saved_dataset_ini_dir, exist_ok=True)

        with open(file=last_saved_dataset_ini_fpath,
                  mode="w", encoding="utf-8") as dataset_ini_file:
            dataset_ini_file.write(new_dataset_dir_path)

        new_csv_files_paths = {
            "lab_cat_csv_path": new_lab_cat_csv_path,
            "text_lab_csv_path": new_text_lab_csv_path,
            "last_saved_dataset_ini_fpath": last_saved_dataset_ini_fpath,
            "empty_error_skipped_rows": empty_error_skipped_rows,
        }
        return new_csv_files_paths

    except Exception as error:
        log_text = (f"BERT add and save single text-category [ERROR]: "
                    f"error: {error}")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
