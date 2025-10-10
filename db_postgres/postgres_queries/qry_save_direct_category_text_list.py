import copy
from typing import Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from db_postgres.postgres_models.direct_predict_model import (
    DirectPredictModel)
from db_postgres.postgres_queries.qry_get_direct_category_text_dicts_list import (
    get_direct_cat_text_dicts_list_qry)
from db_postgres.postgres_queries_utils.merge_obj_ongoing_session import (
    merge_obj_to_ongoing_session)


async def save_direct_cat_text_list_qry(
        ongoing_session: AsyncSession,
        direct_cat_text_dicts_list: List[Dict[str, str]],
        creation_reason: str = None,
        save_only_unique: bool = True
) -> None:
    account_id, account_username = None, None
    direct_cat_text_update_list = None

    try:
        if save_only_unique:
            old_direct_cat_text_list = await get_direct_cat_text_dicts_list_qry(
                ongoing_session=ongoing_session)
            ext_direct_cat_text_list = copy.copy(old_direct_cat_text_list)
            unique_direct_cat_text_list = []
            for cur_cat_text_dict in direct_cat_text_dicts_list:
                cur_cat_text_dict["creation_reason"] = creation_reason
                if not cur_cat_text_dict in ext_direct_cat_text_list:
                    unique_direct_cat_text_list.append(cur_cat_text_dict)
                    ext_direct_cat_text_list.append(cur_cat_text_dict)
            direct_cat_text_update_list = unique_direct_cat_text_list
        else:
            direct_cat_text_update_list = direct_cat_text_dicts_list
        # print(f"direct_cat_text_update_list: {direct_cat_text_update_list}")  # Too long
        print(f"len(direct_cat_text_update_list): {len(direct_cat_text_update_list)}")

        new_direct_cat_text_model_obj = DirectPredictModel()
        for cur_cat_text_dict in direct_cat_text_update_list:
            account_id = cur_cat_text_dict.get("account_id")
            account_username = cur_cat_text_dict.get("account_username")
            direct_category = cur_cat_text_dict.get("direct_category")
            direct_text = cur_cat_text_dict.get("direct_text")

            direct_cat_text_new_data = {
                "account_id": account_id,
                "account_username": account_username,
                "direct_category": direct_category,
                "direct_text": direct_text,
                "creation_reason": creation_reason}
            await merge_obj_to_ongoing_session(
                object_to_merge=new_direct_cat_text_model_obj,
                ongoing_session=ongoing_session,
                new_update_data=direct_cat_text_new_data)
        print(f"DB Postgres saving direct cat-text dicts list data [OK]")
    except Exception as error:
        error_log = (f"DB Postgres saving direct cat-text dicts list data [ERROR]: "
                     f"error: {error}\n"
                     f"account_id: {account_id}\n"
                     f"account_username: {account_username}\n"
                     f"direct_category: {account_id}\n"
                     f"direct_text: {account_username}\n"
                     f"direct_cat_text_dicts_list: {direct_cat_text_dicts_list}\n"
                     f"direct_cat_text_update_list: {direct_cat_text_update_list}\n")
        print(error_log)
        raise
