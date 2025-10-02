from typing import Dict

from sqlalchemy.ext.asyncio import AsyncSession

from db_postgres.postgres_models.label_text_model import LabelTextModel
from db_postgres.postgres_queries.qry_get_lab_idx_and_id_dict import (
    get_label_idx_and_id_dict_qry)
from db_postgres.postgres_queries.qry_get_label_text_dicts_list import (
    get_label_text_dicts_list_qry)
from db_postgres.postgres_queries_utils.merge_obj_ongoing_session import (
    merge_obj_to_ongoing_session)


async def save_unique_text_lab_dict_qry(
        ongoing_session: AsyncSession,
        text_label_dict: Dict[int, str],
        creation_reason: str = None,
        save_only_unique: bool = True
) -> None:
    lab_cat_obj_id, cur_lab_index, cur_text = None, None, None

    text_lab_dict_update = None
    try:
        if save_only_unique:
            old_lab_text_list = await get_label_text_dicts_list_qry(
                ongoing_session=ongoing_session)
            unique_text_lab_dict = {}
            for cur_text, cur_lab_index in text_label_dict.items():
                lab_text_dict_to_find = {"label_index": cur_lab_index,
                                         "text": cur_text}
                if not lab_text_dict_to_find in old_lab_text_list:
                    unique_text_lab_dict[cur_text] = cur_lab_index
            text_lab_dict_update = unique_text_lab_dict
            # print(f"text_lab_dict_update: {text_lab_dict_update}")  # Too long
            print(f"len(text_lab_dict_update): {len(text_lab_dict_update)}")
        else:
            text_lab_dict_update = text_label_dict

        new_lab_text_model_obj = LabelTextModel()  # Not in loop to save memory

        pgs_lab_idx_and_id_dict = await get_label_idx_and_id_dict_qry(
            ongoing_session=ongoing_session)

        for cur_text, cur_lab_index in text_lab_dict_update.items():
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
        print(f"DB Postgres saving text-label dictionary data [OK]")
    except Exception as error:
        error_log = (f"DB Postgres saving text-label dictionary data [ERROR]: "
                     f"error: {error}\n"
                     f"lab_cat_obj_id: {lab_cat_obj_id}\n"
                     f"cur_lab_index: {cur_lab_index}\n"
                     f"cur_text: {cur_text}\n"
                     f"text_label_dict: {text_label_dict}\n"
                     f"text_lab_dict_update: {text_lab_dict_update}\n")
        print(error_log)
        raise
