from typing import Type

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta

from db_postgres.postgres_async_conn.pgs_async_connection import Base


async def deactivate_all_model_records_qry(
        ongoing_session: AsyncSession,
        ModelClassORM: Type[Base] | DeclarativeMeta
) -> None:
    orm_query = update(ModelClassORM).values(active=False)
    await ongoing_session.execute(orm_query)
