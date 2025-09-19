from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db_postgres.postgres_async_conn.pgs_async_connection import Base
from db_postgres.postgres_models.active_create_upd_mixins import (
    ActiveMixin, CreateUpdateMixin)


class LabelTextModel(Base, ActiveMixin, CreateUpdateMixin):
    __tablename__ = "label_text"

    id: Mapped[int] = mapped_column(primary_key=True)
    # dataset_id: Mapped[Optional[int]] = mapped_column(ForeignKey("dataset.id"))
    label_category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("label_category.id"))

    text: Mapped[str] = mapped_column()

    # category_services: Mapped['Service'] = relationship(
    #     argument='Service',
    #     order_by='Service.name',
    #     back_populates="service_categories")
    #
    # category_masters: Mapped['Master'] = relationship(
    #     argument='Master',
    #     order_by='Master.full_name',
    #     back_populates="master_categories")
