import os

from db_postgres.postgres_async_conn.pgs_async_connection import PostgresConnection
from db_postgres.postgres_async_conn.postgres_async_session import PostgresSession
from db_postgres.postgres_models.trained_bert_model import TrainedBertModel
from db_postgres.postgres_utils.get_model_records_flex_query import get_model_rows_flex_query


async def get_last_saved_model_dir_qry() -> str | None:
    pgs_conn = PostgresConnection()
    async with PostgresSession(async_engine=pgs_conn.engine) as pgs_session:
        pgs_trained_model_recs = await get_model_rows_flex_query(
            orm_model_class=TrainedBertModel,
            ongoing_session=pgs_session,
            selected_fields=("model_directory", "created_at"),
            fields_values_filter=None,
            order_by_fields=TrainedBertModel.created_at.desc(),
            return_scalars=False)
        print(f"####### type(pgs_trained_model_recs): {type(pgs_trained_model_recs)}")
        print(f"####### len(pgs_trained_model_recs): {len(pgs_trained_model_recs)}")
        print(f"####### pgs_trained_model_recs: {pgs_trained_model_recs}")

    if pgs_trained_model_recs:  # DB last saved model path exists
        pgs_model_dir_path = pgs_trained_model_recs[0].model_directory  # Newest model path
        print(f"model_directory: {pgs_trained_model_recs[0].model_directory}")
        print(f"created_at: {pgs_trained_model_recs[0].created_at}")
        if pgs_model_dir_path and os.path.isdir(pgs_model_dir_path):
            return pgs_model_dir_path
        else:  # Last saved model path from DB not found
            print(f"DB last saved model directory not found [ERROR]:\n"
                  f"pgs_model_dir_path: {pgs_model_dir_path}\n")
            pgs_model_dir_path = None
    else:  # No last saved model path in DB
        pgs_model_dir_path = None
    return pgs_model_dir_path
