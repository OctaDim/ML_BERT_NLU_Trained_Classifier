from typing import Dict

from sqlalchemy.ext.asyncio import AsyncSession

from db_postgres.postgres_models.label_category_model import (
    LabelCategoryModel)
from db_postgres.postgres_models.label_text_model import LabelTextModel
from db_postgres.postgres_queries.qry_get_text_label_dict import get_text_label_dict_qry
from db_postgres.postgres_utils.get_model_records_flex_query import (
    get_model_rows_flex_query)
from db_postgres.postgres_utils.merge_obj_ongoing_session import (
    merge_obj_to_ongoing_session)


async def save_text_label_dict_qry(
        ongoing_session: AsyncSession,
        text_label_dict: Dict[int, str]
) -> None:
    label_category_obj_id, cur_label_index, cur_text = None, None, None
    try:
        old_text_lab_dict = await get_text_label_dict_qry(
            ongoing_session=ongoing_session)
        unique_keys = text_label_dict.keys() - old_text_lab_dict.keys()
        unique_text_lab_dict = {key: text_label_dict[key] for key in unique_keys}
        print(f"unique_lab_cat_dict: {unique_text_lab_dict}")

        new_lab_text_model_obj = LabelTextModel()  # Not in loop to save memory
        for cur_text, cur_label_index in unique_text_lab_dict.items():
            label_category_objs = await get_model_rows_flex_query(
                orm_model_class=LabelCategoryModel,
                ongoing_session=ongoing_session,
                selected_fields=None,
                fields_values_filter={"label_index": cur_label_index},
                order_by_fields=None,
                return_scalars=True)
            label_category_obj_id = label_category_objs[0].id

            label_text_new_data = {
                "label_category_id": label_category_obj_id,
                "label_index_hint": cur_label_index,
                "text": cur_text}
            await merge_obj_to_ongoing_session(
                object_to_merge=new_lab_text_model_obj,
                ongoing_session=ongoing_session,
                new_update_data=label_text_new_data)
        print(f"DB Postgres saving label-text data [OK]")
    except Exception as error:
        error_log = (f"DB Postgres saving label-text data [ERROR]: "
                     f"error: {error}\n"
                     f"label_category_obj_id: {label_category_obj_id}\n"
                     f"cur_label_index: {cur_label_index}\n"
                     f"cur_text: {cur_text}\n"
                     f"text_label_dict: {text_label_dict}\n")
        print(error_log)
        raise
