from typing import Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from db_postgres.postgres_models.draft_category_text_model import (
    DraftCategoryTextModel)
from db_postgres.postgres_queries_utils.merge_obj_ongoing_session import (
    merge_obj_to_ongoing_session)


async def save_draft_cat_text_dicts_list_qry(
        ongoing_session: AsyncSession,
        draft_cat_text_dicts_list: List[Dict[str, str]],
        customer_id: int,
        account_id: str,
        account_username: str,
        creation_reason: str = None,
) -> None:
    draft_category = None
    draft_text = None

    try:
        new_draft_cat_text_obj = DraftCategoryTextModel()
        for cur_draft_cat_text in draft_cat_text_dicts_list:
            ds_existing_category = cur_draft_cat_text.get("ds_existing_category")
            draft_category = cur_draft_cat_text.get("draft_category")
            ds_existing_text = cur_draft_cat_text.get("ds_existing_text")
            draft_text = cur_draft_cat_text.get("draft_text")
            current_status = cur_draft_cat_text.get("current_status")
            active = cur_draft_cat_text.get("active")

            draft_cat_text_new_data = {
                "customer_id": customer_id,
                "account_id": account_id,
                "account_username": account_username,
                "ds_existing_category": ds_existing_category,
                "draft_category": draft_category,
                "ds_existing_text": ds_existing_text,
                "draft_text": draft_text,
                "current_status": current_status,
                "active": active,
                "creation_reason": creation_reason}

            await merge_obj_to_ongoing_session(
                object_to_merge=new_draft_cat_text_obj,
                ongoing_session=ongoing_session,
                new_update_data=draft_cat_text_new_data)
        print(f"DB Postgres saving draft cat-text dicts list data [OK]")
    except Exception as error:
        error_log = (f"DB Postgres saving draft cat-text dicts list data [ERROR]: "
                     f"error: {error}\n"
                     f"customer_id: {customer_id}\n"
                     f"account_id: {account_id}\n"
                     f"account_username: {account_username}\n"
                     f"draft_category: {draft_category}\n"
                     f"draft_text: {draft_text}\n"
                     f"draft_cat_text_dicts_list: {draft_cat_text_dicts_list}\n")
        print(error_log)
        raise
