from typing import Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from db_postgres.postgres_models.draft_category_text_model import (
    DraftCategoryTextModel)
from db_postgres.postgres_queries_utils.get_model_records_flex_query import (
    get_model_rows_flex_query)


async def get_id_draft_dict_by_ids_list_qry(
        ongoing_session: AsyncSession,
        drafts_ids_list: List[int],
) -> Dict[int, Dict[str, any]] | None:
    """Returns list of dicts with drafts data"""
    filter_fields = {"id": [drafts_ids_list]}
    pgs_drafts_objs = await get_model_rows_flex_query(
        orm_model_class=DraftCategoryTextModel,
        ongoing_session=ongoing_session,
        selected_fields=None,
        fields_values_filter=filter_fields,
        order_by_fields=None,
        return_scalars=True)
    # print(f"####### pgs_drafts_objs: {pgs_drafts_objs}")  # Too long
    print(f"####### type(pgs_drafts_objs): {type(pgs_drafts_objs)}")
    print(f"####### len(pgs_drafts_objs): {len(pgs_drafts_objs)}")

    pgs_id_draft_dicts = {}
    for cur_record in pgs_drafts_objs:
        pgs_id_draft_dicts[cur_record.id] = {
            "account_id": cur_record.account_id,
            "account_username": cur_record.account_username,
            "ds_existing_category": cur_record.ds_existing_category,
            "draft_category": cur_record.draft_category,
            "ds_existing_text": cur_record.ds_existing_text,
            "draft_text": cur_record.draft_text,
            "current_status": cur_record.current_status,
            "active": cur_record.active, }
    return pgs_id_draft_dicts
