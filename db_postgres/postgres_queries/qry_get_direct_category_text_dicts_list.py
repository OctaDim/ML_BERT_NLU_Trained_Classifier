from typing import Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from db_postgres.postgres_models.direct_predict_model import (
    DirectPredictModel)
from db_postgres.postgres_queries_utils.get_model_records_flex_query import (
    get_model_rows_flex_query)


async def get_direct_cat_text_dicts_list_qry(
        ongoing_session: AsyncSession,
) -> List[Dict[str, str]] | None:
    """Returns list of dicts with direct_category (str) and direct_text (str)"""
    filter_fields = {"active": True}
    pgs_direct_cat_text_objs = await get_model_rows_flex_query(
        orm_model_class=DirectPredictModel,
        ongoing_session=ongoing_session,
        selected_fields=None,
        fields_values_filter=filter_fields,
        order_by_fields=None,
        return_scalars=True)
    # print(f"####### pgs_direct_cat_text_objs: {pgs_direct_cat_text_objs}")  # Too long
    print(f"####### type(pgs_direct_cat_text_objs): {type(pgs_direct_cat_text_objs)}")
    print(f"####### len(pgs_direct_cat_text_objs): {len(pgs_direct_cat_text_objs)}")

    pgs_direct_cat_text_dicts_list = []
    for cur_record in pgs_direct_cat_text_objs:
        cur_direct_cat_text_dict = {
            "account_id": cur_record.account_id,
            "account_username": cur_record.account_username,
            "direct_category": cur_record.direct_category,
            "direct_text": cur_record.direct_text,
            "creation_reason": cur_record.creation_reason}
        pgs_direct_cat_text_dicts_list.append(cur_direct_cat_text_dict)
    return pgs_direct_cat_text_dicts_list
