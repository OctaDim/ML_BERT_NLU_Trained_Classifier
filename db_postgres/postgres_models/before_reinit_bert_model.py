from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db_postgres.postgres_async_conn.pgs_async_connection import Base
from db_postgres.postgres_models.active_create_upd_mixins import (
    CreateUpdateMixin, StatusMixin)


class BeforeReinitBertModel(Base, CreateUpdateMixin, StatusMixin):
    __tablename__ = "before_reinit_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("customer.id"))

    temp_model_dir: Mapped[str] = mapped_column()
    dataset_name: Mapped[Optional[str]] = mapped_column()
    labels_before: Mapped[Optional[int]] = mapped_column()
    labels_after: Mapped[Optional[int]] = mapped_column()
