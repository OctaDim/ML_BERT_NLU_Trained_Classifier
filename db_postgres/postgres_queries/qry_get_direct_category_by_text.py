from sqlalchemy.ext.asyncio import AsyncSession

from db_postgres.postgres_models.direct_predict_model import (
    DirectPredictModel)
from db_postgres.postgres_queries_utils.get_model_records_flex_query import (
    get_model_rows_flex_query)


async def get_direct_category_by_text(
        ongoing_session: AsyncSession,
        account_id: str,
        account_username: str,
        direct_text: str
) -> str | None:
    filter_fields = {"account_id": account_id,
                     "account_username": account_username,
                     "direct_text": direct_text,
                     "active": True}
    direct_predict_objs = await get_model_rows_flex_query(
        orm_model_class=DirectPredictModel,
        ongoing_session=ongoing_session,
        selected_fields=["direct_category"],
        fields_values_filter=filter_fields,
        order_by_fields=DirectPredictModel.created_at.desc(),
        return_scalars=False)
    print(f"####### direct_predict_objs: {direct_predict_objs}")
    print(f"####### type(direct_predict_objs): {type(direct_predict_objs)}")
    print(f"####### len(direct_predict_objs): {len(direct_predict_objs)}")

    if not direct_predict_objs:
        return None

    direct_category = direct_predict_objs[0].direct_category  # Latest direct category
    print(f"direct_category: {direct_category}")
    return direct_category
