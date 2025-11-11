from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db_postgres.postgres_conn_async.pgs_async_connection import Base
from db_postgres.postgres_models.orm_models_fields_mixins import (
    ActiveMix, CreateUpdateMix, StatusMix, CreateReasonMix)


class TrainedBertModel(Base, CreateReasonMix, ActiveMix, CreateUpdateMix):
    __tablename__ = "trained_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[Optional[int]] = mapped_column(ForeignKey("dataset.id"))
    dataset_name: Mapped[Optional[str]] = mapped_column()
    model_directory: Mapped[str] = mapped_column()

    # category_services: Mapped['Service'] = relationship(
    #     argument='Service',
    #     order_by='Service.name',
    #     back_populates="service_categories")
    #
    # category_masters: Mapped['Master'] = relationship(
    #     argument='Master',
    #     order_by='Master.full_name',
    #     back_populates="master_categories")
