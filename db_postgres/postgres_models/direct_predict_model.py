from typing import Optional, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db_postgres.postgres_async_conn.pgs_async_connection import Base
from db_postgres.postgres_models.orm_models_fields_mixins import (
    ActiveMix, CreateUpdateMix, CreateReasonMix)


class DirectPredictModel(Base, CreateReasonMix, ActiveMix, CreateUpdateMix):
    __tablename__ = "direct_predict"

    id: Mapped[int] = mapped_column(primary_key=True)

    account_id: Mapped[str] = mapped_column()
    account_username: Mapped[str] = mapped_column()

    direct_category: Mapped[str] = mapped_column()
    direct_text: Mapped[str] = mapped_column()
