from typing import Tuple, Any

from sqlalchemy import Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from db_postgres.postgres_queries_utils.model_object_attrs_update import (
    update_model_obj_no_commit)


async def merge_obj_to_ongoing_session(
        ongoing_session: AsyncSession,
        object_to_merge: DeclarativeBase | Row[Tuple[Any, ...]] |
                         Row | RowMapping,
        new_update_data: dict,
) -> None:
    update_model_obj_no_commit(orm_model_object=object_to_merge,
                               new_update_data=new_update_data)
    try:
        await ongoing_session.merge(object_to_merge)
    except Exception as error:
        log_error = (f"DB Merging object to ongoing session [ERROR]: \n"
                     f"error: {error}\n"
                     f"object_to_merge: {object_to_merge}\n"
                     f"model_class: {object_to_merge.__class__.__name__}\n"
                     f"new_update_data: {new_update_data}\n"
                     f"ongoing_session: {ongoing_session}\n")
        print(log_error)
        raise type(error)(log_error) from error
