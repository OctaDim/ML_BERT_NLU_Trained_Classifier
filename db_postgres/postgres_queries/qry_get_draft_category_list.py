from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from db_postgres.postgres_models.draft_category_text_model import (
    DraftCategoryTextModel)
from db_postgres.postgres_queries_utils.get_model_records_flex_query import (
    get_model_rows_flex_query)


async def get_draft_category_list_qry(
        ongoing_session: AsyncSession
) -> List[str]:
    fields_filter = {"active": True}

    draft_cat_text_objs = await get_model_rows_flex_query(
        orm_model_class=DraftCategoryTextModel,
        ongoing_session=ongoing_session,
        selected_fields=["draft_category"],
        fields_values_filter=fields_filter,
        order_by_fields=DraftCategoryTextModel.draft_category,
        return_scalars=True)
    print(f"####### type(draft_cat_text_objs): {type(draft_cat_text_objs)}")
    print(f"####### len(draft_cat_text_objs): {len(draft_cat_text_objs)}")
    # print(f"####### draft_cat_text_objs: {draft_cat_text_objs}")  # Too long

    draft_categories_list = [str(row) for row in draft_cat_text_objs]
    print(f"####### type(draft_categories_list): {type(draft_categories_list)}")
    print(f"####### len(draft_categories_list): {len(draft_categories_list)}")
    # print(f"####### draft_categories_list: {draft_categories_list}")  # Too long
    return draft_categories_list
