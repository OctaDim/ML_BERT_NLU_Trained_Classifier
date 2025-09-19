from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db_postgres.postgres_async_conn.pgs_async_connection import Base
from db_postgres.postgres_models.active_create_upd_mixins import (
    ActiveMixin, CreateUpdateMixin, StatusMixin)


class TrainedBertModel(Base, ActiveMixin, CreateUpdateMixin, StatusMixin):
    __tablename__ = "trained_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[Optional[int]] = mapped_column(ForeignKey("dataset.id"))

    model_directory: Mapped[str] = mapped_column()
    creation_reason: Mapped[Optional[str]] = mapped_column()
    # dataset_name: Mapped[Optional[str]] = mapped_column()

    # category_services: Mapped['Service'] = relationship(
    #     argument='Service',
    #     order_by='Service.name',
    #     back_populates="service_categories")
    #
    # category_masters: Mapped['Master'] = relationship(
    #     argument='Master',
    #     order_by='Master.full_name',
    #     back_populates="master_categories")
