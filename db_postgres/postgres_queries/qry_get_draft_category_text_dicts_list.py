from typing import Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from db_postgres.postgres_models.draft_category_text_model import (
    DraftCategoryTextModel)
from db_postgres.postgres_queries_utils.get_model_records_flex_query import (
    get_model_rows_flex_query)


async def get_draft_cat_text_dicts_list_qry(
        ongoing_session: AsyncSession,
) -> List[Dict[str, str]] | None:
    """Returns list of dicts with draft category (str) and draft text (str)"""
    filter_fields = {"active": True}

    pgs_draft_cat_text_objs = await get_model_rows_flex_query(
        orm_model_class=DraftCategoryTextModel,
        ongoing_session=ongoing_session,
        selected_fields=["draft_category", "draft_text"],
        fields_values_filter=filter_fields,
        order_by_fields=None,
        return_scalars=False)
    # print(f"####### pgs_draft_cat_text_objs: {pgs_draft_cat_text_objs}")  # Too long
    print(f"####### type(pgs_draft_cat_text_objs): {type(pgs_draft_cat_text_objs)}")
    print(f"####### len(pgs_draft_cat_text_objs): {len(pgs_draft_cat_text_objs)}")

    pgs_draft_cat_text_dicts_list = []
    for cur_record in pgs_draft_cat_text_objs:
        cur_direct_cat_text_dict = {
            "draft_category": cur_record.draft_category,
            "draft_text": cur_record.draft_text}
        pgs_draft_cat_text_dicts_list.append(cur_direct_cat_text_dict)
    return pgs_draft_cat_text_dicts_list
