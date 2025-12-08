from fastapi import HTTPException, status

from ML_BERT_classifier.class_bert import ClassifierBERT
from configs.enums import DRAFT_STATUS
from configs.settings import (
    BERT_OPTIONS, ALCHEMY_OPTIONS)
from db_postgres.postgres_conn.pgs_connection import (
    PgsAsyncConnection)
from db_postgres.postgres_conn.postgres_session import (
    PgsAsyncSession)
from db_postgres.postgres_models.draft_category_text_model import (
    DraftCategoryTextModel)
from db_postgres.postgres_queries.qry_find_create_customer import (
    find_create_customer_qry)
from db_postgres.postgres_queries.qry_get_draft_category_text_dicts_list import (
    get_draft_cat_text_dicts_list_qry)
from db_postgres.postgres_queries.qry_get_label_category_dict import (
    get_label_category_dict_qry)
from db_postgres.postgres_queries.qry_get_label_text_dict import (
    get_label_text_dict_qry)
from db_postgres.postgres_queries_utils.save_new_model_data import (
    save_new_model_data_qry)
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


async def add_draft_text_category_pair(
        account_data: AccountDataBert,
        update_text: str,
        update_category: str,
        bert_model_inst: ClassifierBERT
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

    try:
        print("Checking update text already exists in dataset:")
        ds_text_exists_flag = update_text in cur_text_lab_dict
        print(f"ds_text_exists_flag: {ds_text_exists_flag}")

        print("Checking update category already exists in dataset by text:")
        dataset_label_by_text = cur_text_lab_dict.get(update_text)
        dataset_cat_by_text = cur_lab_cat_dict.get(dataset_label_by_text)
        ds_cat_by_text_exists_flag = dataset_cat_by_text == update_category
        print(f"dataset_label_by_text: {dataset_label_by_text}")
        print(f"dataset_cat_by_text: {dataset_cat_by_text}")
        print(f"ds_cat_by_text_exists_flag: {ds_cat_by_text_exists_flag}")

        print("Getting dataset category if already exists in all dataset:")
        all_ds_cat_exists_flag = update_category in cur_lab_cat_dict.values()
        all_ds_existing_cat = update_category if all_ds_cat_exists_flag else None

        print("DB Postgres Getting current draft categories list:")
        pgs_conn = PgsAsyncConnection()
        async with PgsAsyncSession(engine=pgs_conn.engine,
                                   log_good_ops=log_pgs_good_ops
                                   ) as pgs_session:
            draft_cat_text_list = await get_draft_cat_text_dicts_list_qry(
                ongoing_session=pgs_session)

        category_text_dict = {"draft_category": update_category,
                              "draft_text": update_text}
        draft_cat_text_exists_flag = category_text_dict in draft_cat_text_list
        print(f"draft_cat_text_exists_flag: {draft_cat_text_exists_flag}")

        if ds_text_exists_flag and ds_cat_by_text_exists_flag:
            dataset_existing_cat = all_ds_existing_cat
            dataset_existing_text = update_text
            new_draft_cat_info = f"draft category exists in dataset: {update_category}"  # Just return info
            new_draft_text_info = f"draft text exists in dataset: {update_text}"  # Just return info
            current_status = DRAFT_STATUS.DATASET_EXISTS
            active_val = False
            creation_reason = (
                f"cat-text pair: {update_category}-{update_text[:15]}, "
                f"active: {active_val}, "
                f"new_draft_cat_info: {new_draft_cat_info},"
                f"new_draft_text_info: {new_draft_text_info}")
        elif ds_text_exists_flag:  # and not ds_cat_by_text_exists_flag
            if draft_cat_text_exists_flag:
                dataset_existing_cat = all_ds_existing_cat
                dataset_existing_text = update_text
                new_draft_cat_info = f"draft category exists in drafts: {update_category}"  # Just return info
                new_draft_text_info = f"draft text exists in drafts: {update_text}"  # Just return info
                current_status = DRAFT_STATUS.DRAFT_EXISTS
                active_val = False
                creation_reason = (
                    f"cat-text pair: {update_category}-{update_text[:15]}, "
                    f"active: {active_val}, "
                    f"new_draft_cat_info: {new_draft_cat_info},"
                    f"new_draft_text_info: {new_draft_text_info}")
            else:
                dataset_existing_cat = all_ds_existing_cat
                dataset_existing_text = update_text
                new_draft_cat_info = f"new draft category: {update_category}"  # Just return info
                new_draft_text_info = f"draft text exists in dataset: {update_text}"  # Just return info
                current_status = DRAFT_STATUS.OVERRIDING_DRAFT_ADDED
                active_val = False  # Not allowed draft with overriding existing dataset category/class (tech task)
                # active_val = True
                creation_reason = (
                    f"cat-text pair: {update_category}-{update_text[:15]}, "
                    f"active: {active_val}, "
                    f"new_draft_cat_info: {new_draft_cat_info},"
                    f"new_draft_text_info: {new_draft_text_info}")
        elif ds_cat_by_text_exists_flag:  # and not ds_text_exists_flag
            if draft_cat_text_exists_flag:
                dataset_existing_cat = update_category
                dataset_existing_text = None
                new_draft_cat_info = f"draft category exists in drafts: {update_category}"  # Just return info
                new_draft_text_info = f"draft text exists in drafts: {update_text}"  # Just return info
                current_status = DRAFT_STATUS.DRAFT_EXISTS
                active_val = False
                creation_reason = (
                    f"cat-text pair: {update_category}-{update_text[:15]}, "
                    f"active: {active_val}, "
                    f"new_draft_cat_info: {new_draft_cat_info},"
                    f"new_draft_text_info: {new_draft_text_info}")
            else:
                dataset_existing_cat = update_category
                dataset_existing_text = None
                new_draft_cat_info = f"draft category exists in dataset: {update_category}"  # Just return info
                new_draft_text_info = f"new draft text: {update_text}"  # Just return info
                current_status = DRAFT_STATUS.NEW_TEXT_DRAFT_ADDED
                active_val = True
                creation_reason = (
                    f"cat-text pair: {update_category}-{update_text[:15]}, "
                    f"active: {active_val}, "
                    f"new_draft_cat_info: {new_draft_cat_info},"
                    f"new_draft_text_info: {new_draft_text_info}")
        else:  # if not ds_text_exists_flag and not ds_cat_by_text_exists_flag
            if draft_cat_text_exists_flag:
                dataset_existing_cat = all_ds_existing_cat
                dataset_existing_text = None
                new_draft_cat_info = f"draft category exists in drafts: {update_category}"  # Just return info
                new_draft_text_info = f"draft text: text exists in drafts: {update_text}"  # Just return info
                current_status = DRAFT_STATUS.DRAFT_EXISTS
                active_val = False
                creation_reason = (
                    f"cat-text pair: {update_category}-{update_text[:15]}, "
                    f"active: {active_val}, "
                    f"new_draft_cat_info: {new_draft_cat_info},"
                    f"new_draft_text_info: {new_draft_text_info}")
            else:
                dataset_existing_cat = all_ds_existing_cat
                dataset_existing_text = None
                new_draft_cat_info = f"new draft category: {update_category}"  # Just return info
                new_draft_text_info = f"new draft text: {update_text}"  # Just return info
                if dataset_existing_cat:
                    current_status = DRAFT_STATUS.NEW_TEXT_DRAFT_ADDED
                    active_val = True
                else:
                    current_status = DRAFT_STATUS.NEW_TEXT_CLASS_DRAFT_ADDED
                    active_val = False  # Not allowed new text - new cat/class, only existing cat/class (tech task)
                # active_val = True
                creation_reason = (
                    f"cat-text pair: {update_category}-{update_text[:15]}, "
                    f"active: {active_val}, "
                    f"new_draft_cat_info: {new_draft_cat_info},"
                    f"new_draft_text_info: {new_draft_text_info}")

        print("Postgres DB Saving single category to draft db data:")
        pgs_conn = PgsAsyncConnection()
        async with PgsAsyncSession(engine=pgs_conn.engine,
                                   log_good_ops=log_pgs_good_ops
                                   ) as pgs_session:
            customer_id = await find_create_customer_qry(
                ongoing_session=pgs_session,
                account_username=account_data.account_username,
                account_id=account_data.account_id,
                creation_reason=creation_reason)

            new_draft_data = {
                "customer_id": customer_id,
                "account_id": account_data.account_id,
                "account_username": account_data.account_username,
                "ds_existing_category": dataset_existing_cat,
                "draft_category": update_category,
                "ds_existing_text": dataset_existing_text,
                "draft_text": update_text,
                "current_status": current_status,
                "active": active_val,
                "creation_reason": creation_reason}

            await save_new_model_data_qry(
                ModelClassORM=DraftCategoryTextModel,
                ongoing_session=pgs_session,
                new_data=new_draft_data)
            print(f"Postgres DB category-text pair saved as draft [OK]:\n"
                  f"new_draft_cat_info: {new_draft_cat_info}\n"
                  f"new_draft_text_info: {new_draft_text_info}\n")

        common_csv_f_note = "db draft table used instead of dataset"
        new_csv_files_data = {
            "lab_cat_csv_path": common_csv_f_note,
            "text_lab_csv_path": common_csv_f_note,
            "direct_cat_text_csv_path": common_csv_f_note,
            "last_saved_dataset_ini_fpath": common_csv_f_note,
            "new_category": new_draft_cat_info,
            "new_text": new_draft_text_info}
        return new_csv_files_data
    except Exception as error:
        error_log = (f"BERT save category-text pair as db draft [ERROR]: "
                     f"error: {error}")
        print(error_log)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_log)
