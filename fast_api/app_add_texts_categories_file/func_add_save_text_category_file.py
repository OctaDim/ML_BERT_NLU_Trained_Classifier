# import asyncio
# from functools import partial
import copy
import os
import shutil
from datetime import datetime

from fastapi import HTTPException, status

from ML_BERT_classifier.class_bert import ClassifierBERT
from configs.settings import BERT_OPTIONS, ALCHEMY_OPTIONS, BASE_DIR
from db_postgres.postgres_queries_helpers.hpr_get_bert_model_data import (
    get_postgres_bert_model_data_hpr)
from fast_api.app_account_data.scheme_account_data import AccountDataBert
from utils_common.normalized_path import (
    get_full_file_normal_path)
from utils_specific.class_csv_direct_categories_texts import (
    CsvDirectCategoryText)
from utils_specific.class_csv_labels_categories import CsvLabelCategory
from utils_specific.class_csv_texts_labels import CsvTextLabel
from utils_specific.get_initial_dataset_dir_path import (
    get_initial_dataset_dir_path)
from utils_specific.get_last_saved_dataset_path import (
    get_last_saved_dataset_dir_path)
from utils_specific.new_dataset_dir_path import get_new_dataset_dir_path


async def add_save_multi_text_category_file(
        account_data: AccountDataBert,
        update_text_category_data: list,
        bert_model_inst: ClassifierBERT,
) -> dict:
    log_pgs_good_ops = ALCHEMY_OPTIONS.ALCHEMY_SESSION_OK_ACTIONS_LOGS

    if ALCHEMY_OPTIONS.USE_POSTGRES_DATABASE:
        pgs_bert_model_data = await get_postgres_bert_model_data_hpr()
        pgs_all_data_flag = pgs_bert_model_data["all_data_flag"]
    else:
        pgs_bert_model_data = None
        pgs_all_data_flag = False

    if not pgs_all_data_flag:
        if bert_model_inst.last_saved_dataset_dir:
            prev_dataset_dir_path = bert_model_inst.last_saved_dataset_dir
        else:
            last_saved_dataset_dir = get_last_saved_dataset_dir_path()
            if last_saved_dataset_dir:
                prev_dataset_dir_path = last_saved_dataset_dir
            else:
                initial_dataset_dir = get_initial_dataset_dir_path()
                if initial_dataset_dir:
                    prev_dataset_dir_path = initial_dataset_dir
                else:
                    prev_dataset_dir_path = ""

        print("Getting previous label-category csv path:")
        prev_lab_cat_csv_path = None
        try:
            prev_lab_cat_csv_path = get_full_file_normal_path(
                all_dir_str_parts=[prev_dataset_dir_path],
                file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)

            print("Getting previous label-category dictionary:")
            with open(file=prev_lab_cat_csv_path,
                      mode="r", encoding="utf-8") as prev_lab_cat_csv_f:
                csf_lab_cat = CsvLabelCategory(prev_lab_cat_csv_f)
                prev_lab_cat_csv_dict = csf_lab_cat.get_label_category_dict()
            print(f"prev_lab_cat_csv_dict: {prev_lab_cat_csv_dict}")  # Too long
            print(f"type(prev_lab_cat_csv_dict): {type(prev_lab_cat_csv_dict)}")
            print(f"len(prev_lab_cat_csv_dict): {len(prev_lab_cat_csv_dict)}")

            if not prev_lab_cat_csv_dict:
                error_log = (f"Empty or wrong label-category csv data [ERROR]:\n"
                             f"prev_lab_cat_csv_path: {prev_lab_cat_csv_path}\n"
                             f"prev_lab_cat_csv_dict: {prev_lab_cat_csv_dict}\n")
                print(error_log)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_log)
            prev_lab_cat_dict = prev_lab_cat_csv_dict
        except Exception as lab_cat_csv_file_error:
            error_log = (f"Getting label-category csv file data [ERROR]:\n"
                         f"error: {lab_cat_csv_file_error}\n"
                         f"prev_lab_cat_csv_path: {prev_lab_cat_csv_path}\n"
                         f"prev_lab_cat_csv_dict: {prev_lab_cat_csv_dict}\n")
            print(error_log)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_log)

        print("Getting previous text-label csv path:")
        prev_text_lab_csv_path = None
        try:
            prev_text_lab_csv_path = get_full_file_normal_path(
                all_dir_str_parts=[prev_dataset_dir_path],
                file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)

            print("Getting previous text-label dictionary:")
            with open(file=prev_text_lab_csv_path,
                      mode="r", encoding="utf-8") as prev_text_lab_csv_f:
                csf_text_lab = CsvTextLabel(prev_text_lab_csv_f)
                prev_text_lab_csv_dict = csf_text_lab.get_text_label_dict()
            # print(f"prev_lab_cat_csv_dict: {prev_lab_cat_csv_dict}")  # Too long
            print(f"type(prev_lab_cat_csv_dict): {type(prev_lab_cat_csv_dict)}")
            print(f"len(prev_lab_cat_csv_dict): {len(prev_lab_cat_csv_dict)}")

            if not prev_text_lab_csv_dict:
                error_log = (f"Empty or wrong text-label csv data [ERROR]:\n"
                             f"prev_text_lab_csv_path: {prev_text_lab_csv_path}\n"
                             f"prev_text_lab_csv_dict: {prev_text_lab_csv_dict}\n")
                print(error_log)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_log)
            prev_text_lab_dict = prev_text_lab_csv_dict
        except Exception as text_lab_csv_file_error:
            error_log = (f"Getting text-label csv file data [ERROR]:\n"
                         f"error: {text_lab_csv_file_error}\n"
                         f"prev_text_lab_csv_path: {prev_text_lab_csv_path}\n"
                         f"prev_text_lab_csv_dict: {prev_text_lab_csv_dict}\n")
            print(error_log)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_log)

        print("Getting previous direct category-text csv path:")
        prev_direct_cat_text_csv_path = None
        try:
            prev_direct_cat_text_csv_path = get_full_file_normal_path(
                all_dir_str_parts=[prev_dataset_dir_path],
                file_name_with_ext=BERT_OPTIONS.BERT_DIRECT_CATEGORY_LABEL_CSV_FILE_NAME)

            print("Getting previous category-text dicts list:")
            with open(file=prev_direct_cat_text_csv_path,
                      mode="r", encoding="utf-8") as prev_direct_cat_text_csv_f:
                csf_direct_cat_text = CsvDirectCategoryText(prev_text_lab_csv_f)
                prev_direct_cat_text_csv_list = csf_direct_cat_text.get_direct_categories_texts_list()
            # print(f"prev_direct_cat_text_csv_list: {prev_direct_cat_text_csv_list}")  # Too long
            print(f"type(prev_direct_cat_text_csv_list): {type(prev_direct_cat_text_csv_list)}")
            print(f"len(prev_direct_cat_text_csv_list): {len(prev_direct_cat_text_csv_list)}")

            if not prev_direct_cat_text_csv_list:
                error_log = (f"Empty or wrong direct category-text csv data [ERROR]:\n"
                             f"prev_direct_cat_text_csv_path: {prev_direct_cat_text_csv_path}\n"
                             f"prev_direct_cat_text_csv_list: {prev_direct_cat_text_csv_list}\n")
                print(error_log)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_log)
            prev_direct_cat_text_list = prev_direct_cat_text_csv_list
        except Exception as text_lab_csv_file_error:
            error_log = (
                f"Getting direct category-text csv file data [ERROR]:\n"
                f"error: {text_lab_csv_file_error}\n"
                f"prev_direct_cat_text_csv_path: {prev_direct_cat_text_csv_path}\n"
                f"prev_direct_cat_text_csv_list: {prev_direct_cat_text_csv_list}\n")
            print(error_log)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_log)
    else:  # All Postgres DB data exists (if pgs_all_data_flag:)
        prev_lab_cat_dict = pgs_bert_model_data["lab_cat_dict"]
        prev_text_lab_dict = pgs_bert_model_data["text_lab_dict"]
        # pgs_lab_text_dicts_list = pgs_bert_model_data["lab_text_dicts_list"]
        prev_dataset_dir = pgs_bert_model_data["dataset_dir"]

        prev_lab_cat_csv_path = get_full_file_normal_path(
            all_dir_str_parts=[prev_dataset_dir],
            file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)

        prev_text_lab_csv_path = get_full_file_normal_path(
            all_dir_str_parts=[prev_dataset_dir],
            file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)

        prev_direct_cat_text_csv_path = get_full_file_normal_path(
            all_dir_str_parts=[prev_dataset_dir],
            file_name_with_ext=BERT_OPTIONS.BERT_DIRECT_CATEGORY_LABEL_CSV_FILE_NAME)

    update_lab_cat_list = []
    update_text_lab_list = []
    update_direct_text_cat_list = []

    upd_lab_cat_dict = copy.copy(prev_lab_cat_dict)
    upd_text_lab_dict = copy.copy(prev_text_lab_dict)

    empty_error_skipped_rows = []
    new_categories_list = []
    new_texts_list = []
    result_list = []

    try:
        print("Group adding multi label-category file:")
        common_datetime_str = str(datetime.now())

        for cur_upd_text_cat in update_text_category_data:
            if len(cur_upd_text_cat) != 2:
                print(f"Current row skipped, not 2 fields number [ERROR]:\n"
                      f"cur_upd_text_cat: {cur_upd_text_cat}\n")
                empty_error_skipped_rows.append(cur_upd_text_cat)
                continue

            cur_update_text = cur_upd_text_cat[0].strip().lower()
            cur_update_category = cur_upd_text_cat[1].strip().lower()
            if not cur_update_text or not cur_update_category:
                print(f"Current row skipped, empty field value [ERROR]:\n"
                      f"cur_update_text: {cur_update_text}\n"
                      f"cur_update_category: {cur_update_category}\n")
                empty_error_skipped_rows.append(cur_upd_text_cat)
                continue

            category_exists_flag = cur_update_category in upd_lab_cat_dict.values()
            text_exists_flag = cur_update_text in upd_text_lab_dict.keys()
            print(f"category_exists_flag: {category_exists_flag}")
            print(f"text_exists_flag: {text_exists_flag}")

            if category_exists_flag and text_exists_flag:
                result_list.append([f"exists: {cur_update_category}",
                                    f"exists: {cur_update_text[:20]}"])  # Just return info
            elif not category_exists_flag and not text_exists_flag:
                new_categories_list.append(cur_update_category)  # Just return info
                new_texts_list.append(cur_update_text[:20])  # Just return info
                result_list.append([f"new: {cur_update_category}",
                                    f"new: {cur_update_text[:20]}"])  # Just return info

                print("Getting next label new index for new category:")
                next_label_new_index = max(prev_lab_cat_dict.keys()) + 1

                print("Updating label-category update list and dict with new category:")
                new_lab_cat_data = (common_datetime_str,
                                    next_label_new_index,
                                    cur_update_category)
                update_lab_cat_list.append(new_lab_cat_data)
                upd_lab_cat_dict[next_label_new_index] = cur_update_category

                print("Updating label-text update list and dict with new text:")
                new_lab_text_data = (common_datetime_str,
                                     next_label_new_index,
                                     cur_update_text)
                update_text_lab_list.append(new_lab_text_data)
                upd_text_lab_dict[cur_update_text] = next_label_new_index
            elif category_exists_flag and not text_exists_flag:
                new_texts_list.append(cur_update_text[:20])  # Just return info
                result_list.append([f"exists: {cur_update_category}",
                                    f"new: {cur_update_text[:20]}"])  # Just return info

                print("Getting existing label index of existing category:")
                existing_lab_cat_index = None
                for cur_exist_label, cur_exist_cat in upd_lab_cat_dict.items():
                    if cur_update_category == cur_exist_cat:
                        existing_lab_cat_index = cur_exist_label

                print("Updating label-text update list with new text:")
                new_lab_text_data = (common_datetime_str,
                                     existing_lab_cat_index,
                                     cur_update_text)
                upd_text_lab_dict[cur_update_text] = existing_lab_cat_index
                update_text_lab_list.append(new_lab_text_data)
            elif text_exists_flag and not category_exists_flag:
                new_categories_list.append(f"direct: {cur_update_category}")  # Just return info
                new_texts_list.append(f"direct: {cur_update_text[:20]}")  # Just return info
                result_list.append([f"direct: {cur_update_category}",
                                    f"direct: {cur_update_text[:20]}"])  # Just return info

                print("Updating category-text update list with new category-text:")
                cur_direct_category = cur_update_category
                cur_direct_text = cur_update_text
                new_direct_cat_text_data = (common_datetime_str,
                                            account_data.account_id,
                                            account_data.account_username,
                                            cur_direct_category,
                                            cur_direct_text)
                update_direct_text_cat_list.append(new_direct_cat_text_data)

        print("Creating new dataset directory path:")
        new_dataset_dir_path = get_new_dataset_dir_path()
        os.makedirs(name=new_dataset_dir_path, exist_ok=True)
        new_dataset_name = new_dataset_dir_path.split(os.path.sep)[-1]

        print("Group saving multi updated label-category csv file:")
        if update_lab_cat_list:  # New category or categories to add
            if not BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:
                new_lab_cat_csv_path = get_full_file_normal_path(
                    all_dir_str_parts=[new_dataset_dir_path],
                    file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)
                shutil.copy2(src=prev_lab_cat_csv_path,
                             dst=new_lab_cat_csv_path)
                with open(file=new_lab_cat_csv_path, mode="a",
                          encoding="utf-8", newline="") as new_lab_cat_csv_file:
                    csv_lab_cat = CsvLabelCategory(new_lab_cat_csv_file)
                    csv_lab_cat.add_multi_label_category_rows(
                        upd_label_category_data=update_lab_cat_list)
                lab_cat_csv_path = new_lab_cat_csv_path  # Return info
            else:
                with open(file=prev_lab_cat_csv_path, mode="a",
                          encoding="utf-8", newline="") as prev_lab_cat_csv_file:
                    csv_lab_cat = CsvLabelCategory(prev_lab_cat_csv_file)
                    csv_lab_cat.add_multi_label_category_rows(
                        upd_label_category_data=update_lab_cat_list)
                lab_cat_csv_path = prev_lab_cat_csv_path  # Return info
        else:
            new_lab_cat_csv_path = get_full_file_normal_path(
                all_dir_str_parts=[new_dataset_dir_path],
                file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)
            shutil.copy2(src=prev_lab_cat_csv_path,
                         dst=new_lab_cat_csv_path)
            lab_cat_csv_path = new_lab_cat_csv_path  # Return info

        print("Group saving multi updated text-label csv file:")
        if update_text_lab_list:
            if not BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:
                new_text_lab_csv_path = get_full_file_normal_path(
                    all_dir_str_parts=[new_dataset_dir_path],
                    file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)
                shutil.copy2(src=prev_text_lab_csv_path,
                             dst=new_text_lab_csv_path)
                with open(file=new_text_lab_csv_path, mode="a",
                          encoding="utf-8", newline="") as new_text_lab_csv_file:
                    csv_text_lab = CsvTextLabel(new_text_lab_csv_file)
                    csv_text_lab.add_multi_text_label_rows(
                        upd_text_label_data=update_text_lab_list)
                text_lab_csv_path = new_text_lab_csv_path  # Return info
            else:
                with open(file=prev_text_lab_csv_path, mode="a",
                          encoding="utf-8", newline="") as prev_text_lab_csv_file:
                    csv_text_lab = CsvTextLabel(prev_text_lab_csv_file)
                    csv_text_lab.add_multi_text_label_rows(
                        upd_text_label_data=update_text_lab_list)
                text_lab_csv_path = prev_text_lab_csv_path  # Return info
        else:
            new_text_lab_csv_path = get_full_file_normal_path(
                all_dir_str_parts=[new_dataset_dir_path],
                file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)
            shutil.copy2(src=prev_text_lab_csv_path,
                         dst=new_text_lab_csv_path)
            text_lab_csv_path = new_text_lab_csv_path  # Return info


        print("Group saving multi updated direct category-text csv file:")
        if update_direct_text_cat_list:
            if not BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:
                new_direct_cat_text_csv_path = get_full_file_normal_path(
                    all_dir_str_parts=[new_dataset_dir_path],
                    file_name_with_ext=BERT_OPTIONS.BERT_DIRECT_CATEGORY_LABEL_CSV_FILE_NAME)
                shutil.copy2(src=prev_direct_cat_text_csv_path,
                             dst=new_direct_cat_text_csv_path)
                with open(file=new_direct_cat_text_csv_path, mode="a",
                          encoding="utf-8", newline="") as new_direct_cat_txt_csvf:
                    csv_direct_cat_text = CsvDirectCategoryText(new_direct_cat_txt_csvf)
                    csv_direct_cat_text.add_multi_direct_cat_text_rows(
                        upd_direct_category_text_data=update_direct_text_cat_list)
                direct_cat_text_csv_path = new_direct_cat_text_csv_path
            else:
                with open(file=prev_direct_cat_text_csv_path, mode="a",
                          encoding="utf-8", newline="") as prev_direct_cat_text_csvf:
                    csv_direct_cat_text = CsvDirectCategoryText(prev_direct_cat_text_csvf)
                    csv_direct_cat_text.add_multi_direct_cat_text_rows(
                        upd_direct_category_text_data=update_direct_text_cat_list)
                direct_cat_text_csv_path = prev_direct_cat_text_csv_path
        else:
            new_direct_cat_text_csv_path = get_full_file_normal_path(
                all_dir_str_parts=[new_dataset_dir_path],
                file_name_with_ext=BERT_OPTIONS.BERT_DIRECT_CATEGORY_LABEL_CSV_FILE_NAME)
            shutil.copy2(src=prev_direct_cat_text_csv_path,
                         dst=new_direct_cat_text_csv_path)
            direct_cat_text_csv_path = new_direct_cat_text_csv_path

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

        print(f"new_categories_list: {new_categories_list}")
        print(f"new_texts_list: {new_texts_list}")
        print(f"result_list: {result_list}")
        print(f"update_lab_cat_list: {update_lab_cat_list}")
        print(f"update_text_lab_list: {update_text_lab_list}")
        print(f"update_direct_text_cat_list: {update_direct_text_cat_list}")

        bert_model_inst.last_saved_dataset_dir = new_dataset_dir_path

        new_csv_files_data = {
            "lab_cat_csv_path": lab_cat_csv_path,
            "text_lab_csv_path": text_lab_csv_path,
            "direct_cat_text_csv_path": direct_cat_text_csv_path,
            "last_saved_dataset_ini_fpath": last_saved_dataset_ini_fpath,
            "empty_error_skipped_rows": empty_error_skipped_rows,
            "new_categories_list": new_categories_list,
            "new_texts_list": new_texts_list,
            "result_list": result_list}
        return new_csv_files_data
    except Exception as error:
        error_log = (f"BERT add and save texts-categories file [ERROR]: "
                     f"error: {error}")
        print(error_log)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_log)

    # last_saved_dataset_ini_dir = ""
    # last_saved_dataset_ini_path = ""
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
    # if not os.path.isdir(prev_dataset_dir_path):
    #     log_text = (f"Data-set initial or saved dir path not found [ERROR]: "
    #                 f"prev_dataset_dir_path: {prev_dataset_dir_path}")
    #     print(log_text)
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail=log_text)

    # try:
    #     print("\nGetting previous label-category dictionary:")
    #     prev_lab_cat_csv_path = get_full_file_normal_path(
    #         all_dir_str_parts=[prev_dataset_dir_path],
    #         file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)
    #
    #     with open(file=prev_lab_cat_csv_path,
    #               mode="r", encoding="utf-8") as prev_lab_cat_csv_file:
    #         csf_lab_cat = CsvLabelCategory(prev_lab_cat_csv_file)
    #         prev_lab_cat_dict = csf_lab_cat.get_label_category_dict()
    #
    #     if not prev_lab_cat_dict:
    #         log_text = (f"Empty or wrong label-category csv data [ERROR]: "
    #                     f"prev_lab_cat_csv_path: {prev_lab_cat_csv_path}, "
    #                     f"prev_lab_cat_dict: {prev_lab_cat_dict}\n")
    #         print(log_text)
    #         raise HTTPException(
    #             status_code=status.HTTP_406_NOT_ACCEPTABLE,
    #             detail=log_text)
    #
    #     print("Getting previous text-label dictionary:")
    #     prev_text_lab_csv_path = get_full_file_normal_path(
    #         all_dir_str_parts=[prev_dataset_dir_path],
    #         file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)
    #
    #     with open(file=prev_text_lab_csv_path,
    #               mode="r", encoding="utf-8") as prev_text_lab_csv_file:
    #         csf_text_lab = CsvTextLabel(prev_text_lab_csv_file)
    #         prev_text_lab_dict = csf_text_lab.get_text_label_dict()
    #
    #     if not prev_text_lab_dict:
    #         log_text = (f"Empty or wrong text-label csv data [ERROR]: "
    #                     f"prev_text_lab_csv_path: {prev_text_lab_csv_path}, "
    #                     f"prev_text_lab_dict: {prev_text_lab_dict}\n")
    #         print(log_text)
    #         raise HTTPException(
    #             status_code=status.HTTP_406_NOT_ACCEPTABLE,
    #             detail=log_text)

#     print("Group adding multi label-category pairs:")
#     new_dataset_dir_path = get_new_dataset_dir_path()
#     new_lab_cat_csv_path = None
#
#     common_datetime_str = str(datetime.now())
#
#     update_lab_cat_csv_list = []
#     update_text_lab_csv_list = []
#     empty_error_skipped_rows = []
#     new_categories_list = []
#     existing_categories_list = []
#
#     for cur_upd_text_cat in update_text_category_data:
#         if len(cur_upd_text_cat) != 2:
#             print(f"Current row skipped, not 2 fields number [ERROR]:\n"
#                   f"cur_upd_text_cat: {cur_upd_text_cat}\n")
#             empty_error_skipped_rows.append(cur_upd_text_cat)
#             continue
#
#         cur_update_text = cur_upd_text_cat[0].strip().lower()
#         cur_update_category = cur_upd_text_cat[1].strip().lower()
#         if not cur_update_text or not cur_update_category:
#             print(f"Current row skipped, empty field value [ERROR]:\n"
#                   f"cur_update_text: {cur_update_text}\n"
#                   f"cur_update_category: {cur_update_category}\n")
#             empty_error_skipped_rows.append(cur_upd_text_cat)
#             continue
#
#         # print("\nAdding new multi label-category pair:")
#         if cur_update_category not in prev_lab_cat_dict.values():
#             next_label_flag_value = max(prev_lab_cat_dict.keys()) + 1
#             prev_lab_cat_dict[next_label_flag_value] = cur_update_category
#             update_lab_cat_csv_list.append(
#                 [common_datetime_str, next_label_flag_value, cur_update_category])
#             new_categories_list.append(cur_update_category)
#         else:
#             next_label_flag_value = None
#
#         # print("Adding new multi text-label pair:")
#         update_label = None
#         if not next_label_flag_value:  # Old category and label
#             for cur_csv_label, cur_csv_category in prev_lab_cat_dict.items():
#                 if cur_update_category == cur_csv_category:
#                     update_label = cur_csv_label
#                     break
#         else:  # New category and new label
#             update_label = next_label_flag_value
#
#         update_text_lab_csv_list.append(
#             [common_datetime_str, update_label, cur_update_text])
#
#     print("Group saving multi updated label-category csv file:")
#     if update_lab_cat_csv_list:  # New category or categories to add
#         if BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:
#             new_lab_cat_csv_path = prev_lab_cat_csv_path
#             with open(file=new_lab_cat_csv_path, mode="a",
#                       encoding="utf-8", newline="") as prev_lab_cat_csv_file:
#                 csv_lab_cat = CsvLabelCategory(prev_lab_cat_csv_file)
#                 csv_lab_cat.add_multi_label_category_rows(
#                     upd_label_category_data=update_lab_cat_csv_list)
#         else:
#             os.makedirs(name=new_dataset_dir_path, exist_ok=True)
#             new_lab_cat_csv_path = get_full_file_normal_path(
#                 all_dir_str_parts=[new_dataset_dir_path],
#                 file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)
#             shutil.copy2(src=prev_lab_cat_csv_path,
#                          dst=new_lab_cat_csv_path)
#
#             with open(file=new_lab_cat_csv_path, mode="a",
#                       encoding="utf-8", newline="") as new_lab_cat_csv_file:
#                 csv_lab_cat = CsvLabelCategory(new_lab_cat_csv_file)
#                 csv_lab_cat.add_multi_label_category_rows(
#                     upd_label_category_data=update_lab_cat_csv_list)
#     else:
#         if not BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:
#             os.makedirs(new_dataset_dir_path, exist_ok=True)
#             new_lab_cat_csv_path = get_full_file_normal_path(
#                 all_dir_str_parts=[new_dataset_dir_path],
#                 file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)
#             shutil.copy2(src=prev_lab_cat_csv_path,
#                          dst=new_lab_cat_csv_path)
#
#     print("Group saving multi updated text-label csv file:")
#     if BERT_OPTIONS.BERT_OVERWRITE_PREV_CSV_DATASET:
#         new_text_lab_csv_path = prev_text_lab_csv_path
#         with open(file=prev_text_lab_csv_path, mode="a",
#                   encoding="utf-8", newline="") as prev_text_lab_csv_file:
#             csv_text_lab = CsvTextLabel(prev_text_lab_csv_file)
#             csv_text_lab.add_multi_text_label_rows(
#                 upd_text_label_data=update_text_lab_csv_list)
#     else:
#         os.makedirs(name=new_dataset_dir_path, exist_ok=True)
#         new_text_lab_csv_path = get_full_file_normal_path(
#             all_dir_str_parts=[new_dataset_dir_path],
#             file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)
#         shutil.copy2(src=prev_text_lab_csv_path,
#                      dst=new_text_lab_csv_path)
#
#         with open(file=new_text_lab_csv_path, mode="a",
#                   encoding="utf-8", newline="") as new_text_lab_csv_file:
#             csv_text_lab = CsvTextLabel(new_text_lab_csv_file)
#             csv_text_lab.add_multi_text_label_rows(
#                 upd_text_label_data=update_text_lab_csv_list)
#
#     bert_model_inst.last_saved_dataset_dir = new_dataset_dir_path
#
#     print("Saving updated dataset ini file path:\n")
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
#     new_csv_files_data = {
#         "lab_cat_csv_path": new_lab_cat_csv_path,
#         "text_lab_csv_path": new_text_lab_csv_path,
#         "last_saved_dataset_ini_fpath": last_saved_dataset_ini_fpath,
#         "empty_error_skipped_rows": empty_error_skipped_rows,
#         "new_categories_list": new_categories_list,
#         "new_texts_list": new_texts_list,
#         "existing_categories_list": existing_categories_list,
#         "existing_categories_list": existing_categories_list}
#     return new_csv_files_data
#
# except Exception as error:
# log_text = (f"BERT add and save single text-category [ERROR]: "
#             f"error: {error}")
# print(log_text)
# raise HTTPException(
#     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#     detail=log_text)
