# import asyncio
# from functools import partial
import os
import shutil

from fastapi import HTTPException, status

from ML_BERT_classifier.init_bert import bert_model_inst
from configs.settings import (
    BASE_DIR, BERT_OPTIONS)
from utils_common.normalized_path import (
    get_full_dir_normal_path, get_full_file_normal_path)
from utils_specific.class_csv_labels_categories import CsvLabelCategory
from utils_specific.new_dataset_dir_path import get_new_dataset_dir_path


def add_save_single_category(update_category: str) -> dict:
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

    if not os.path.isdir(prev_dataset_dir_path):
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
                  mode="r", encoding="utf-8") as prev_lab_cat_csv_f:
            csf_lab_cat = CsvLabelCategory(prev_lab_cat_csv_f)
            prev_lab_cat_dict = csf_lab_cat.get_label_category_dict()

        if not prev_lab_cat_dict:
            log_text = (f"Empty or wrong label-category csv data [ERROR]: "
                        f"prev_lab_cat_csv_path: {prev_lab_cat_csv_path}, "
                        f"prev_lab_cat_dict: {prev_lab_cat_dict}\n")
            print(log_text)
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=log_text)

        print("Getting previous text-label csv path:")
        prev_text_lab_csv_path = get_full_file_normal_path(
            all_dir_str_parts=[prev_dataset_dir_path],
            file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)

        new_dataset_dir_path = get_new_dataset_dir_path()

        print("Single adding one label-category pair for single category:")
        new_lab_cat_csv_path = None

        if update_category not in prev_lab_cat_dict.values():
            next_label_flag_value = max(prev_lab_cat_dict.keys()) + 1
            prev_lab_cat_dict[next_label_flag_value] = update_category
            new_category = update_category
        else:
            next_label_flag_value = None
            new_category = ""

        print("Single adding one single text-label pair for single category:")
        cur_label = None
        if not next_label_flag_value:  # Old category and label
            for label, category in prev_lab_cat_dict.items():
                if category == update_category:
                    cur_label = label
                    break
        else:  # New category and new label
            cur_label = next_label_flag_value

        print("Single saving one label-category pair updated csv file for single category:")
        if next_label_flag_value:  # New category to add added
            if BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:
                new_lab_cat_csv_path = prev_lab_cat_csv_path
                with open(file=new_lab_cat_csv_path, mode="a",
                          encoding="utf-8", newline="") as prev_lab_cat_csv_f:
                    csv_lab_cat = CsvLabelCategory(prev_lab_cat_csv_f)
                    csv_lab_cat.add_single_label_category_row(
                        new_label=cur_label,
                        new_category=update_category)
            else:
                os.makedirs(name=new_dataset_dir_path, exist_ok=True)
                new_lab_cat_csv_path = get_full_file_normal_path(
                    all_dir_str_parts=[new_dataset_dir_path],
                    file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)
                shutil.copy2(src=prev_lab_cat_csv_path,
                             dst=new_lab_cat_csv_path)
                with open(file=new_lab_cat_csv_path, mode="a",
                          encoding="utf-8", newline="") as new_lab_cat_csv_f:
                    csv_lab_cat = CsvLabelCategory(new_lab_cat_csv_f)
                    csv_lab_cat.add_single_label_category_row(
                        new_label=cur_label,
                        new_category=update_category)
        else:
            if not BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:
                os.makedirs(new_dataset_dir_path, exist_ok=True)
                new_lab_cat_csv_path = get_full_file_normal_path(
                    all_dir_str_parts=[new_dataset_dir_path],
                    file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)
                shutil.copy2(src=prev_lab_cat_csv_path,
                             dst=new_lab_cat_csv_path)

        print("Single saving one text-label pair updated csv file:")
        if BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:
            new_text_lab_csv_path = prev_text_lab_csv_path
            shutil.copy2(src=prev_text_lab_csv_path,
                         dst=new_text_lab_csv_path)
        else:
            os.makedirs(name=new_dataset_dir_path, exist_ok=True)
            new_text_lab_csv_path = get_full_file_normal_path(
                all_dir_str_parts=[new_dataset_dir_path],
                file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)
            shutil.copy2(src=prev_text_lab_csv_path,
                         dst=new_text_lab_csv_path)

        bert_model_inst.last_saved_dataset_dir = new_dataset_dir_path

        print("Saving updated dataset ini file path:\n")
        last_saved_dataset_ini_fpath = get_full_file_normal_path(
            all_dir_str_parts=[BASE_DIR],
            file_name_with_ext=BERT_OPTIONS.BERT_LAST_SAVED_DATASET_INI_FILE_PATH)
        last_saved_dataset_ini_dir = os.path.dirname(
            last_saved_dataset_ini_fpath)
        os.makedirs(name=last_saved_dataset_ini_dir, exist_ok=True)

        with open(file=last_saved_dataset_ini_fpath,
                  mode="w", encoding="utf-8") as dataset_ini_file:
            dataset_ini_file.write(new_dataset_dir_path)

        new_csv_files_data = {
            "lab_cat_csv_path": new_lab_cat_csv_path,
            "text_lab_csv_path": new_text_lab_csv_path,
            "last_saved_dataset_ini_fpath": last_saved_dataset_ini_fpath,
            "new_category": new_category}
        return new_csv_files_data

    except Exception as error:
        log_text = (f"BERT add and save single category for single category [ERROR]: "
                    f"error: {error}")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
