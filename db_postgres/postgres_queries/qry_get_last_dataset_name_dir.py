from typing import Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from db_postgres.postgres_async_conn.pgs_async_connection import (
    PostgresConnection)
from db_postgres.postgres_async_conn.postgres_async_session import (
    PostgresSession)
from db_postgres.postgres_models.dataset_model import DatasetModel
from db_postgres.postgres_utils.get_model_records_flex_query import (
    get_model_rows_flex_query)


async def get_last_dataset_name_dir_qry(
        ongoing_session: AsyncSession
) -> Tuple[str, str] | None:
    pgs_dataset_model_objs = await get_model_rows_flex_query(
        orm_model_class=DatasetModel,
        ongoing_session=ongoing_session,
        selected_fields=None,
        fields_values_filter=None,
        order_by_fields=DatasetModel.created_at.desc(),
        return_scalars=True)
    # print(f"####### pgs_dataset_model_objs: {pgs_dataset_model_objs}")
    print(f"####### type(pgs_dataset_model_objs): {type(pgs_dataset_model_objs)}")
    print(f"####### len(pgs_dataset_model_objs): {len(pgs_dataset_model_objs)}")

    if pgs_dataset_model_objs:  # DB last saved model path exists
        pgs_last_dataset_name = pgs_dataset_model_objs[0].dataset_name  # Newest dataset name
        pgs_last_dataset_dir = pgs_dataset_model_objs[0].dataset_csv_dir  # Newest dataset csv dir

        print(f"dataset_name: {pgs_last_dataset_name}")
        print(f"csv_dataset_dir: {pgs_last_dataset_dir}")
        print(f"created_at: {pgs_dataset_model_objs[0].created_at}")
        return pgs_last_dataset_name, pgs_last_dataset_dir


if __name__ == "__main__":
    import asyncio


    async def test_get_last_dataset_name_dir_qry():
        pgs_conn = PostgresConnection()
        async with PostgresSession(async_engine=pgs_conn.engine) as pgs_session:
            await get_last_dataset_name_dir_qry(ongoing_session=pgs_session)


    asyncio.run(main=test_get_last_dataset_name_dir_qry(),
                debug=True)
