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
from utils_specific.class_csv_texts_labels import CsvTextLabel
from utils_specific.new_dataset_dir_path import get_new_dataset_dir_path


def add_save_test_category(update_text: str,
                           update_category: str) -> dict:
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
        print("\nAdding new text-category pair:")
        prev_lab_cat_csv_path = get_full_file_normal_path(
            all_dir_str_parts=[prev_dataset_dir_path],
            file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)

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

            if BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:
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
                    file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)
                shutil.copy2(src=prev_lab_cat_csv_path,
                             dst=new_lab_cat_csv_path)
                with open(file=new_lab_cat_csv_path, mode="a",
                          encoding="utf-8", newline="") as new_csv1_file:
                    csv_lab_cat = CsvLabelCategory(new_csv1_file)
                    csv_lab_cat.add_new_label_category_row(
                        new_label=next_label_value,
                        new_category=update_category)
        else:
            if not BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:
                os.makedirs(new_dataset_dir_path)
                new_lab_cat_csv_path = get_full_file_normal_path(
                    all_dir_str_parts=[new_dataset_dir_path],
                    file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)
                shutil.copy2(src=prev_lab_cat_csv_path,
                             dst=new_lab_cat_csv_path)

        print("\nAdding new text-label pair:")
        prev_text_lab_csv_path = get_full_file_normal_path(
            all_dir_str_parts=[prev_dataset_dir_path],
            file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)

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

        if BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:
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
                file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)

            shutil.copy2(src=prev_text_lab_csv_path,
                         dst=new_text_lab_csv_path)

            with open(file=new_text_lab_csv_path, mode="a",
                      encoding="utf-8", newline="") as new_csv2_file:
                csv_text_lab = CsvTextLabel(new_csv2_file)
                csv_text_lab.add_new_text_label_row(
                    new_text=update_text,
                    new_label=cur_label)
            bert_model_inst.last_saved_dataset_dir = new_dataset_dir_path

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
            "text_lab_csv_path": new_text_lab_csv_path}
        return new_csv_files_paths

    except Exception as error:
        log_text = (f"BERT add and save single text-category [ERROR]: "
                    f"error: {error}")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
