import copy

from fastapi import HTTPException, status

from ML_BERT_classifier.class_bert import ClassifierBERT
from configs.enums import DRAFT_STATUS
from configs.settings import (
    BERT_OPTIONS, ALCHEMY_OPTIONS)
from db_postgres.postgres_conn.pgs_connection import (
    PgsAsyncConnection)
from db_postgres.postgres_conn.postgres_session import (
    PgsAsyncSession)
from db_postgres.postgres_queries.qry_find_create_customer import (
    find_create_customer_qry)
from db_postgres.postgres_queries.qry_get_draft_category_text_dicts_list import (
    get_draft_cat_text_dicts_list_qry)
from db_postgres.postgres_queries.qry_get_label_category_dict import (
    get_label_category_dict_qry)
from db_postgres.postgres_queries.qry_get_label_text_dict import (
    get_label_text_dict_qry)
from db_postgres.postgres_queries.qry_get_renamed_classes_by_customer_list import (
    get_renamed_classes_by_customer)
from db_postgres.postgres_queries.qry_save_draft_categ_text_dicts_list import (
    save_draft_cat_text_dicts_list_qry)
from fast_api.app_account_data.scheme_account_data import (
    AccountDataBert)
from utils_common.normalized_path import get_full_file_normal_path
from utils_specific.class_csv_labels_categories import (
    CsvLabelCategory)
from utils_specific.class_csv_texts_labels import CsvTextLabel
from utils_specific.get_initial_dataset_dir_path import (
    get_initial_dataset_dir_path)
from utils_specific.get_last_saved_dataset_path import (
    get_last_saved_dataset_dir_path)


async def add_draft_multi_text_category_file(
        account_data: AccountDataBert,
        update_text_category_data: list,
        bert_model_inst: ClassifierBERT,
        file_name: str = None,
) -> dict:
    log_pgs_good_ops = ALCHEMY_OPTIONS.ALCHEMY_SESSION_OK_ACTIONS_LOGS

    pgs_conn = PgsAsyncConnection()
    async with PgsAsyncSession(engine=pgs_conn.engine,
                               log_good_ops=log_pgs_good_ops
                               ) as pgs_session:
        print("DB Postgres Getting current label-category dictionary:")
        pgs_lab_cat_dict = await get_label_category_dict_qry(
            ongoing_session=pgs_session,
            reversed_category_label_dict=False)

        print("DB Postgres Getting texts-labels dict data:")
        pgs_text_lab_dict = await get_label_text_dict_qry(
            ongoing_session=pgs_session,
            reversed_text_label_dict=True)
        print(f"pgs_text_lab_dict: {pgs_text_lab_dict}")  # Too long
        print(f"len(pgs_text_lab_dict): {len(pgs_text_lab_dict)}")

    if not pgs_lab_cat_dict or not pgs_text_lab_dict:
        if bert_model_inst.last_saved_dataset_dir:
            cur_dataset_dir_path = bert_model_inst.last_saved_dataset_dir
        else:
            last_saved_dataset_dir = get_last_saved_dataset_dir_path()
            if last_saved_dataset_dir:
                cur_dataset_dir_path = last_saved_dataset_dir
            else:
                initial_dataset_dir = get_initial_dataset_dir_path()
                if initial_dataset_dir:
                    cur_dataset_dir_path = initial_dataset_dir
                else:
                    cur_dataset_dir_path = ""

        print("Getting current label-category csv path:")
        cur_lab_cat_csv_path = None
        try:
            cur_lab_cat_csv_path = get_full_file_normal_path(
                all_dir_str_parts=[cur_dataset_dir_path],
                file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)

            print("Getting current label-category dictionary from csv file:")
            with open(file=cur_lab_cat_csv_path,
                      mode="r", encoding="utf-8") as prev_lab_cat_csv_f:
                csf_lab_cat = CsvLabelCategory(prev_lab_cat_csv_f)
                cur_lab_cat_csv_dict = csf_lab_cat.get_label_category_dict(
                    reversed_category_label=False)
            print(f"cur_lab_cat_csv_dict: {cur_lab_cat_csv_dict}")  # Too long
            print(f"type(cur_lab_cat_csv_dict): {type(cur_lab_cat_csv_dict)}")
            print(f"len(cur_lab_cat_csv_dict): {len(cur_lab_cat_csv_dict)}")

            if not cur_lab_cat_csv_dict:
                error_log = (
                    f"Empty or wrong label-category csv data [ERROR]:\n"
                    f"cur_lab_cat_csv_path: {cur_lab_cat_csv_path}\n"
                    f"cur_lab_cat_csv_dict: {cur_lab_cat_csv_dict}\n")
                print(error_log)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_log)
            cur_lab_cat_dict = cur_lab_cat_csv_dict
        except Exception as lab_cat_csv_file_error:
            error_log = (
                f"Getting label-category csv file data [ERROR]:\n"
                f"error: {lab_cat_csv_file_error}\n"
                f"cur_lab_cat_csv_path: {cur_lab_cat_csv_path}\n"
                f"cur_lab_cat_csv_dict: {cur_lab_cat_csv_dict}\n")
            print(error_log)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_log)

        print("Getting previous text-label csv path:")
        cur_text_lab_csv_path = None
        try:
            cur_text_lab_csv_path = get_full_file_normal_path(
                all_dir_str_parts=[cur_dataset_dir_path],
                file_name_with_ext=BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME)

            print("Getting previous csv text-label dictionary:")
            with open(file=cur_text_lab_csv_path,
                      mode="r", encoding="utf-8") as prev_text_lab_csv_f:
                csf_text_lab = CsvTextLabel(prev_text_lab_csv_f)
                cur_text_lab_csv_dict = csf_text_lab.get_text_label_dict()
            # print(f"cur_text_lab_csv_dict: {cur_text_lab_csv_dict}")  # Too long
            print(f"type(cur_text_lab_csv_dict): {type(cur_text_lab_csv_dict)}")
            print(f"len(cur_text_lab_csv_dict): {len(cur_text_lab_csv_dict)}")

            if not cur_text_lab_csv_dict:
                error_log = (
                    f"Empty or wrong text-label csv data [ERROR]:\n"
                    f"cur_text_lab_csv_path: {cur_text_lab_csv_path}\n"
                    f"cur_text_lab_csv_dict: {cur_text_lab_csv_dict}\n")
                print(error_log)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_log)
            cur_text_lab_dict = cur_text_lab_csv_dict
        except Exception as text_lab_csv_file_error:
            error_log = (
                f"Getting text-label csv file data [ERROR]:\n"
                f"error: {text_lab_csv_file_error}\n"
                f"cur_text_lab_csv_path: {cur_text_lab_csv_path}\n"
                f"cur_text_lab_csv_dict: {cur_text_lab_csv_dict}\n")
            print(error_log)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_log)
    else:  # if pgs_cat_lab_dict and pgs_text_lab_dict: Postgres DB cat-lab and text-lab data exists
        cur_lab_cat_dict = pgs_lab_cat_dict
        cur_text_lab_dict = pgs_text_lab_dict

    print("DB Postgres Getting customer id and current draft categories list:")
    pgs_conn = PgsAsyncConnection()
    async with PgsAsyncSession(engine=pgs_conn.engine,
                               log_good_ops=log_pgs_good_ops
                               ) as pgs_session:
        customer_creation_reason = (
            f"uploaded file: {file_name}, "
            f"new draft: db draft table used instead of dataset")

        customer_id = await find_create_customer_qry(
            ongoing_session=pgs_session,
            account_username=account_data.account_username,
            account_id=account_data.account_id,
            creation_reason=customer_creation_reason)

        draft_cat_text_list = await get_draft_cat_text_dicts_list_qry(
            ongoing_session=pgs_session)
    ext_draft_cat_text_list = copy.copy(draft_cat_text_list)

    upd_draft_cat_text_list = []

    empty_error_skipped_rows = []  # Just return info
    new_categories_list = []  # Just return info
    new_texts_list = []  # Just return info
    result_list = []  # Just return info

    try:
        print("Group adding multi text-category file to drafts:")
        draft_creation_reason = None

        for cur_upd_text_cat in update_text_category_data:
            if len(cur_upd_text_cat) != 2:
                print(f"Current row skipped, not 2 fields number [ERROR]:\n"
                      f"cur_upd_text_cat: {cur_upd_text_cat}\n")
                empty_error_skipped_rows.append(cur_upd_text_cat)
                continue

            cur_upd_text = cur_upd_text_cat[0].strip().lower()
            cur_upd_cat = cur_upd_text_cat[1].strip().lower()
            if not cur_upd_text or not cur_upd_cat:
                print(f"Current row skipped, empty field value [ERROR]:\n"
                      f"cur_upd_text: {cur_upd_text}\n"
                      f"cur_upd_cat: {cur_upd_cat}\n")
                empty_error_skipped_rows.append(cur_upd_text_cat)
                continue

            print("Checking update text already exists in dataset:")
            ds_text_exists_flag = cur_upd_text in cur_text_lab_dict
            print(f"ds_text_exists_flag: {ds_text_exists_flag}")

            if BERT_OPTIONS.REPLACE_ORIG_CATEGORY_WITH_RENAMED_CLASS:
                print("Postgres DB Getting origin-renamed customer classes list:")
                orig_renamed_classes_list = await get_renamed_classes_by_customer(
                    ongoing_session=pgs_session,
                    customer_id=customer_id)

                print("Replacing file category with original model category"
                      "in cur_upd_cat (if class was renamed by customer):")
                for cur_classes in orig_renamed_classes_list:
                    cur_original_class = cur_classes["model_class_name"].strip().lower()
                    cur_renamed_class = cur_classes["renamed_class_name"].strip().lower()
                    orig_upd_cat = cur_upd_cat
                    if cur_upd_cat == cur_renamed_class:
                        cur_upd_cat = cur_original_class
                        print(f"orig_upd_cat: {orig_upd_cat}")
                        print(f"cur_renamed_class: {cur_renamed_class}")
                        print(f"cur_original_class: {cur_original_class}")
                        print(f"cur_upd_cat: {cur_upd_cat}")

            print("Checking update category already exists in dataset by text:")
            dataset_label_by_text = cur_text_lab_dict.get(cur_upd_text)
            dataset_cat_by_text = cur_lab_cat_dict.get(dataset_label_by_text)
            ds_cat_by_text_exists_flag = dataset_cat_by_text == cur_upd_cat
            print(f"dataset_label_by_text: {dataset_label_by_text}")
            print(f"dataset_cat_by_text: {dataset_cat_by_text}")
            print(f"ds_cat_by_text_exists_flag: {ds_cat_by_text_exists_flag}")

            print("Getting dataset category if already exists in all dataset:")
            all_ds_cat_exists_flag = cur_upd_cat in cur_lab_cat_dict.values()
            all_ds_existing_cat = cur_upd_cat if all_ds_cat_exists_flag else None

            cur_cat_text_dict = {"draft_category": cur_upd_cat,
                                 "draft_text": cur_upd_text}
            draft_cat_text_exists_flag = cur_cat_text_dict in ext_draft_cat_text_list
            print(f"draft_cat_text_exists_flag: {draft_cat_text_exists_flag}")

            if ds_text_exists_flag and ds_cat_by_text_exists_flag:
                dataset_existing_cat = all_ds_existing_cat
                dataset_existing_text = cur_upd_text
                new_draft_cat_info = f"draft category exists in dataset: {cur_upd_cat}"  # Just return info
                new_draft_text_info = f"draft text exists in dataset: {cur_upd_text}"  # Just return info
                current_status = DRAFT_STATUS.DATASET_EXISTS
                active_val = False
                draft_creation_reason = (
                    f"cat-text file: {cur_upd_cat}-{cur_upd_text[:15]}, "
                    f"active: {active_val}, "
                    f"new_draft_cat_info: {new_draft_cat_info},"
                    f"new_draft_text_info: {new_draft_text_info}")
            elif ds_text_exists_flag:  # and not ds_cat_by_text_exists_flag
                if draft_cat_text_exists_flag:
                    dataset_existing_cat = all_ds_existing_cat
                    dataset_existing_text = cur_upd_text
                    new_draft_cat_info = f"draft category exists in drafts: {cur_upd_cat}"  # Just return info
                    new_draft_text_info = f"draft text exists in drafts: {cur_upd_text}"  # Just return info
                    current_status = DRAFT_STATUS.DRAFT_EXISTS
                    active_val = False
                    draft_creation_reason = (
                        f"cat-text file: {cur_upd_cat}-{cur_upd_text[:15]}, "
                        f"active: {active_val}, "
                        f"new_draft_cat_info: {new_draft_cat_info},"
                        f"new_draft_text_info: {new_draft_text_info}")
                else:
                    dataset_existing_cat = all_ds_existing_cat
                    dataset_existing_text = cur_upd_text
                    new_draft_cat_info = f"new draft category: {cur_upd_cat}"  # Just return info
                    new_draft_text_info = f"draft text exists in dataset: {cur_upd_text}"  # Just return info
                    current_status = DRAFT_STATUS.OVERRIDING_DRAFT_ADDED
                    active_val = False  # Not allowed draft with overriding existing dataset category/class (tech task)
                    # active_val = True
                    draft_creation_reason = (
                        f"cat-text file: {cur_upd_cat}-{cur_upd_text[:15]}, "
                        f"active: {active_val}, "
                        f"new_draft_cat_info: {new_draft_cat_info},"
                        f"new_draft_text_info: {new_draft_text_info}")
            elif ds_cat_by_text_exists_flag:  # and not ds_text_exists_flag
                if draft_cat_text_exists_flag:
                    dataset_existing_cat = cur_upd_cat
                    dataset_existing_text = None
                    new_draft_cat_info = f"draft category exists in drafts: {cur_upd_cat}"  # Just return info
                    new_draft_text_info = f"draft text exists in drafts: {cur_upd_text}"  # Just return info
                    current_status = DRAFT_STATUS.DRAFT_EXISTS
                    active_val = False
                    draft_creation_reason = (
                        f"cat-text file: {cur_upd_cat}-{cur_upd_text[:15]}, "
                        f"active: {active_val}, "
                        f"new_draft_cat_info: {new_draft_cat_info},"
                        f"new_draft_text_info: {new_draft_text_info}")
                else:
                    dataset_existing_cat = cur_upd_cat
                    dataset_existing_text = None
                    new_draft_cat_info = f"draft category exists in dataset: {cur_upd_cat}"  # Just return info
                    new_draft_text_info = f"new draft text: {cur_upd_text}"  # Just return info
                    current_status = DRAFT_STATUS.NEW_TEXT_DRAFT_ADDED
                    active_val = True
                    draft_creation_reason = (
                        f"cat-text file: {cur_upd_cat}-{cur_upd_text[:15]}, "
                        f"active: {active_val}, "
                        f"new_draft_cat_info: {new_draft_cat_info},"
                        f"new_draft_text_info: {new_draft_text_info}")
            else:  # if not ds_text_exists_flag and not ds_cat_by_text_exists_flag
                if draft_cat_text_exists_flag:
                    dataset_existing_cat = all_ds_existing_cat
                    dataset_existing_text = None
                    new_draft_cat_info = f"draft category exists in drafts {cur_upd_cat}"  # Just return info
                    new_draft_text_info = f"draft text exists in drafts {cur_upd_text}"  # Just return info
                    current_status = DRAFT_STATUS.DRAFT_EXISTS
                    active_val = False
                    draft_creation_reason = (
                        f"cat-text file: {cur_upd_cat}-{cur_upd_text[:15]}, "
                        f"active: {active_val}, "
                        f"new_draft_cat_info: {new_draft_cat_info},"
                        f"new_draft_text_info: {new_draft_text_info}")
                else:
                    dataset_existing_cat = all_ds_existing_cat
                    dataset_existing_text = None
                    new_draft_cat_info = f"new draft category: {cur_upd_cat}"  # Just return info
                    new_draft_text_info = f"new draft text: {cur_upd_text}"  # Just return info
                    if dataset_existing_cat:
                        active_val = True
                        current_status = DRAFT_STATUS.NEW_TEXT_DRAFT_ADDED
                    else:
                        current_status = DRAFT_STATUS.NEW_TEXT_CLASS_DRAFT_ADDED
                        active_val = False  # Not allowed new text - new cat/class, only existing cat/class (tech task)
                    # active_val = True
                    draft_creation_reason = (
                        f"cat-text file: {cur_upd_cat}-{cur_upd_text[:15]}, "
                        f"active: {active_val}, "
                        f"new_draft_cat_info: {new_draft_cat_info},"
                        f"new_draft_text_info: {new_draft_text_info}")

            # Extending draft list to check existing draft cat-text in previous and new draft cat-text data
            ext_draft_cat_text_list.append(cur_cat_text_dict)

            new_categories_list.append(new_draft_cat_info)  # Just return info
            new_texts_list.append(new_draft_text_info)  # Just return info
            result_list.append(draft_creation_reason)  # Just return info

            cur_draft_cat_text_data = {
                "ds_existing_category": dataset_existing_cat,
                "draft_category": cur_upd_cat,
                "ds_existing_text": dataset_existing_text,
                "draft_text": cur_upd_text,
                "current_status": current_status,
                "active": active_val}
            upd_draft_cat_text_list.append(cur_draft_cat_text_data)

        print("Postgres DB Saving single category to draft db data:")
        pgs_conn = PgsAsyncConnection()
        async with PgsAsyncSession(engine=pgs_conn.engine,
                                   log_good_ops=log_pgs_good_ops
                                   ) as pgs_session:
            await save_draft_cat_text_dicts_list_qry(
                ongoing_session=pgs_session,
                draft_cat_text_dicts_list=upd_draft_cat_text_list,
                customer_id=customer_id,
                account_id=account_data.account_id,
                account_username=account_data.account_username,
                creation_reason=draft_creation_reason)
            print(f"Postgres DB multi category-text file saved as draft [OK]:\n"
                  f"upd_draft_cat_text_list: {upd_draft_cat_text_list[:2]}.....\n")

            common_csv_f_note = "db draft table used instead of dataset"
            new_csv_files_data = {
                "lab_cat_csv_path": common_csv_f_note,
                "text_lab_csv_path": common_csv_f_note,
                "direct_cat_text_csv_path": common_csv_f_note,
                "last_saved_dataset_ini_fpath": common_csv_f_note,
                "empty_error_skipped_rows": empty_error_skipped_rows,
                "new_categories_list": new_categories_list,
                "new_texts_list": new_texts_list,
                "result_list": result_list}
            return new_csv_files_data
    except Exception as error:
        error_log = (f"BERT save multi category-text file as db draft [ERROR]: "
                     f"error: {error}")
        print(error_log)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_log)
