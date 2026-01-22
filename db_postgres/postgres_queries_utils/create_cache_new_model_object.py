from typing import Type

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta
from starlette import status

from db_postgres.postgres_init.declarative_base_model import Base
from db_postgres.postgres_queries_utils.model_object_attrs_update import (
    update_model_obj_no_commit)


async def create_cache_new_model_obj_qry(
        ModelClassORM: Type[Base] | DeclarativeMeta,
        ongoing_session: AsyncSession,
        new_data: dict,
        log_new_data: bool = False
) -> None:
    if not new_data:
        return None

    try:
        new_model_obj = ModelClassORM()
        update_model_obj_no_commit(orm_model_object=new_model_obj,
                                   new_update_data=new_data,
                                   log_update_data=log_new_data)
        ongoing_session.add(new_model_obj)
        await ongoing_session.flush()
        return new_model_obj
    except Exception as error:
        log_text = (f"Creating-caching new model object [ERROR]:\n"
                    f"error: {error}\n"
                    f"ModelClassORM: {ModelClassORM}\n"
                    f"new_object_data: {new_data}\n")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
