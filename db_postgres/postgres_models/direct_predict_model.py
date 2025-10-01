from typing import Optional, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db_postgres.postgres_async_conn.pgs_async_connection import Base
from db_postgres.postgres_models.active_create_upd_mixins import (
    ActiveMixin, CreateUpdateMixin)


class DirectPredictModel(Base, ActiveMixin, CreateUpdateMixin):
    __tablename__ = "direct_predict"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[Optional[int]] = mapped_column(ForeignKey("dataset.id"))
    customer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("customer.id"))

    direct_text: Mapped[int] = mapped_column()
    direct_category: Mapped[int] = mapped_column()
