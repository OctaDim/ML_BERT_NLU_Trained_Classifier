from typing import Dict

from sqlalchemy.ext.asyncio import AsyncSession

from db_postgres.postgres_models.label_category_model import (
    LabelCategoryModel)
from db_postgres.postgres_queries.qry_get_label_category_dict import (
    get_label_category_dict_qry)
from db_postgres.postgres_queries_utils.merge_obj_ongoing_session import (
    merge_obj_to_ongoing_session)
from db_postgres.postgres_queries_utils.model_object_attrs_update import (
    update_model_obj_no_commit)


async def cache_unique_lab_cat_dict_qry(
        ongoing_session: AsyncSession,
        dataset_id: int,
        label_category_dict: Dict[int, str],
        creation_reason: str = None,
        save_only_unique: bool = True
) -> Dict[int, int]:
    cur_label_idx, cur_category_name, lab_cat_dict_update = None, None, None
    try:
        if save_only_unique:
            old_lab_cat_dict = await get_label_category_dict_qry(
                ongoing_session=ongoing_session,
                reversed_category_label_dict=False)
            unique_lab_cat_dict = {}
            for cur_lab_index, cur_category_name in label_category_dict.items():
                if cur_category_name not in old_lab_cat_dict.values():
                    unique_lab_cat_dict[cur_lab_index] = cur_category_name
            lab_cat_dict_update = unique_lab_cat_dict
            print(f"lab_cat_dict_update: {lab_cat_dict_update}")  # Too long
            print(f"len(lab_cat_dict_update): {len(lab_cat_dict_update)}")
        else:
            lab_cat_dict_update = label_category_dict

        cached_lab_index_id_dict = {}
        for cur_label_idx, cur_category_name in lab_cat_dict_update.items():
            cur_new_lab_cat_obj = LabelCategoryModel()
            lab_cat_new_data = {
                "label_index": cur_label_idx,
                "dataset_id": dataset_id,
                "category_name": cur_category_name,
                "creation_reason": creation_reason}

            update_model_obj_no_commit(
                orm_model_object=cur_new_lab_cat_obj,
                new_update_data=lab_cat_new_data)
            ongoing_session.add(cur_new_lab_cat_obj)
            await ongoing_session.flush()
            new_lab_cat_obj_id = cur_new_lab_cat_obj.id
            cached_lab_index_id_dict[cur_label_idx] = new_lab_cat_obj_id
        print(f"cached_lab_index_id_dict: {cached_lab_index_id_dict}")
        print(f"DB Postgres caching label-category data with getting ids [OK]")
        return cached_lab_index_id_dict
    except Exception as error:
        error_log = (f"DB Postgres caching label-category with getting ids [ERROR]: "
                     f"error: {error}\n"
                     f"dataset_id: {dataset_id}\n"
                     f"cur_label_idx: {cur_label_idx}\n"
                     f"cur_category_name: {cur_category_name}\n"
                     f"label_category_dict: {label_category_dict}\n"
                     f"lab_cat_dict_update: {lab_cat_dict_update}\n")
        print(error_log)
        raise


async def save_unique_lab_cat_dict_qry(
        ongoing_session: AsyncSession,
        dataset_id: int,
        label_category_dict: Dict[int, str]
) -> None:
    cur_label, cur_category = None, None
    try:
        old_lab_cat_dict = await get_label_category_dict_qry(
            ongoing_session=ongoing_session,
            reversed_category_label_dict=False)
        unique_lab_cat_dict = {}
        for cur_lab_index, cur_cat_name in label_category_dict.items():
            if cur_cat_name not in old_lab_cat_dict.values():
                unique_lab_cat_dict[cur_lab_index] = cur_cat_name
        print(f"unique_lab_cat_dict: {unique_lab_cat_dict}")

        new_lab_cat_model_obj = LabelCategoryModel()
        for cur_label, cur_category in unique_lab_cat_dict.items():
            lab_cat_new_data = {
                "label_index": cur_label,
                "dataset_id": dataset_id,
                "category_name": cur_category}
            await merge_obj_to_ongoing_session(
                object_to_merge=new_lab_cat_model_obj,
                ongoing_session=ongoing_session,
                new_update_data=lab_cat_new_data)
        print(f"DB Postgres saving label-category data [OK]")
    except Exception as error:
        error_log = (f"DB Postgres saving label-category data [ERROR]: "
                     f"error: {error}\n"
                     f"dataset_id: {dataset_id}\n"
                     f"cur_label: {cur_label}\n"
                     f"cur_category: {cur_category}\n"
                     f"label_category_dict: {label_category_dict}\n")
        print(error_log)
        raise
