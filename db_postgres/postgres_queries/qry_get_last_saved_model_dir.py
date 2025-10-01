from sqlalchemy.ext.asyncio import AsyncSession

from db_postgres.postgres_models.trained_bert_model import (
    TrainedBertModel)
from db_postgres.postgres_queries_utils.get_model_records_flex_query import (
    get_model_rows_flex_query)


async def get_last_saved_model_dir_qry(
        ongoing_session: AsyncSession,
) -> str | None:
    pgs_trained_model_objs = await get_model_rows_flex_query(
        orm_model_class=TrainedBertModel,
        ongoing_session=ongoing_session,
        selected_fields=("model_directory", "created_at"),
        fields_values_filter=None,
        order_by_fields=TrainedBertModel.created_at.desc(),
        return_scalars=False)
    # print(f"####### pgs_trained_model_objs: {pgs_trained_model_objs}")
    print(f"####### type(pgs_trained_model_objs): {type(pgs_trained_model_objs)}")
    print(f"####### len(pgs_trained_model_objs): {len(pgs_trained_model_objs)}")

    if not pgs_trained_model_objs:
        return None

    pgs_model_dir_path = pgs_trained_model_objs[0].model_directory  # Newest model path
    print(f"model_directory: {pgs_model_dir_path}")
    print(f"created_at: {pgs_trained_model_objs[0].created_at}")
    return pgs_model_dir_path
