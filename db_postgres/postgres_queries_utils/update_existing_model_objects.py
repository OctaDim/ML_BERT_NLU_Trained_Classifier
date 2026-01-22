from typing import Dict, Type, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta

from db_postgres.postgres_init.declarative_base_model import Base
from db_postgres.postgres_queries_utils.get_model_records_flex_query import (
    get_model_rows_flex_query)
from db_postgres.postgres_queries_utils.merge_obj_ongoing_session import (
    merge_obj_to_ongoing_session)


async def update_existing_model_objs_qry(
        ModelClassORM: Type[Base] | DeclarativeMeta,
        ongoing_session: AsyncSession,
        fields_values_filter: Dict[str, Union[any, bool, list, tuple]],
        update_data: Dict[str, any]
) -> bool | None:
    try:
        existing_model_objs = await get_model_rows_flex_query(
            orm_model_class=ModelClassORM,
            ongoing_session=ongoing_session,
            selected_fields=None,
            fields_values_filter=fields_values_filter,
            order_by_fields=None,
            return_scalars=True)

        if existing_model_objs:
            for cur_model_obj in existing_model_objs:
                await merge_obj_to_ongoing_session(
                    object_to_merge=cur_model_obj,
                    ongoing_session=ongoing_session,
                    new_update_data=update_data)
            print(f"DB Postgres updating existing model obj data [OK]")
            return True
    except Exception as error:
        error_log = (f"DB Postgres updating existing model obj data [ERROR]: "
                     f"error: {error}\n"
                     f"ModelClassORM: {ModelClassORM}\n"
                     f"fields_values_filter: {fields_values_filter}\n"
                     f"new_data: {update_data}\n")
        print(error_log)
        raise
