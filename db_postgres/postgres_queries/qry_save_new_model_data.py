from typing import Dict, Type

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta

from db_postgres.postgres_async_conn.pgs_async_connection import (
    Base)
from db_postgres.postgres_utils.merge_obj_ongoing_session import (
    merge_obj_to_ongoing_session)


async def save_new_model_data_qry(
        ModelClassORM: Type[Base] | DeclarativeMeta,
        ongoing_session: AsyncSession,
        new_data: Dict[str, any]) -> None:
    try:
        new_model_obj = ModelClassORM()
        await merge_obj_to_ongoing_session(
            object_to_merge=new_model_obj,
            ongoing_session=ongoing_session,
            new_update_data=new_data)
        print(f"DB Postgres saving new model data [OK]")
    except Exception as error:
        error_log = (f"DB Postgres saving new model data [ERROR]: "
                     f"error: {error}\n"
                     f"ModelClassORM: {ModelClassORM}\n"
                     f"new_data: {new_data}\n")
        print(error_log)
        raise
