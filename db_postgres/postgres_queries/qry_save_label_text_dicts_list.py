from typing import Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from db_postgres.postgres_models.label_text_model import LabelTextModel
from db_postgres.postgres_queries.qry_get_lab_idx_and_id_dict import (
    get_label_idx_and_id_dict_qry)
from db_postgres.postgres_queries.qry_get_label_text_dicts_list import (
    get_label_text_dicts_list_qry)
from db_postgres.postgres_queries_utils.merge_obj_ongoing_session import (
    merge_obj_to_ongoing_session)


async def save_label_text_dicts_list_qry(
        ongoing_session: AsyncSession,
        label_text_dicts_list: List[Dict[str, int | str]],
        creation_reason: str = None,
        save_only_unique: bool = True
) -> None:
    lab_cat_obj_id, cur_lab_index, cur_text = None, None, None
    lab_dicts_update_list = None
    try:
        if save_only_unique:
            old_lab_text_list = await get_label_text_dicts_list_qry(
                ongoing_session=ongoing_session)
            unique_lab_text_list = []
            for cur_lab_text_dict in label_text_dicts_list:
                if not cur_lab_text_dict in old_lab_text_list:
                    unique_lab_text_list.append(cur_lab_text_dict)
            lab_dicts_update_list = unique_lab_text_list
            # print(f"unique_lab_text_list: {unique_lab_text_list}")  # Too long
            print(f"len(unique_lab_text_list): {len(unique_lab_text_list)}")
        else:
            lab_dicts_update_list = label_text_dicts_list

        pgs_lab_idx_and_id_dict = await get_label_idx_and_id_dict_qry(
            ongoing_session=ongoing_session)

        new_lab_text_model_obj = LabelTextModel()  # Not in loop to save memory
        for cur_lab_text_dict in lab_dicts_update_list:
            cur_lab_index = cur_lab_text_dict.get("label_index")
            cur_text = cur_lab_text_dict.get("text")
            lab_cat_obj_id = pgs_lab_idx_and_id_dict.get(int(cur_lab_index))  # Fast search

            label_text_new_data = {
                "label_category_id": lab_cat_obj_id,
                "label_index_hint": cur_lab_index,
                "text": cur_text,
                "creation_reason": creation_reason}
            await merge_obj_to_ongoing_session(
                object_to_merge=new_lab_text_model_obj,
                ongoing_session=ongoing_session,
                new_update_data=label_text_new_data)
        print(f"DB Postgres saving label-text dicts list data [OK]")
    except Exception as error:
        error_log = (f"DB Postgres saving label-text dicts list data [ERROR]: "
                     f"error: {error}\n"
                     f"lab_cat_obj_id: {lab_cat_obj_id}\n"
                     f"cur_lab_index: {cur_lab_index}\n"
                     f"cur_text: {cur_text}\n"
                     f"label_text_dicts_list: {label_text_dicts_list}\n"
                     f"lab_dicts_update_list: {lab_dicts_update_list}\n")
        print(error_log)
        raise
