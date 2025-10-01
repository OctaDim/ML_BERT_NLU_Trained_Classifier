from typing import Optional, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db_postgres.postgres_async_conn.pgs_async_connection import Base
from db_postgres.postgres_models.active_create_upd_mixins import (
    ActiveMixin, CreateUpdateMixin)


class LabelCategoryModel(Base, ActiveMixin, CreateUpdateMixin):
    __tablename__ = "label_category"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[Optional[int]] = mapped_column(ForeignKey("dataset.id"))

    label_index: Mapped[int] = mapped_column(unique=True)
    category_name: Mapped[str] = mapped_column(unique=True)
    creation_reason: Mapped[Optional[str]] = mapped_column()

    # rel_labels_texts: Mapped[List["LabelTextModel"]] = relationship(
    #     argument="LabelTextModel",
    #     # order_by="LabelTextModel.label_index_hint",
    #     back_populates="rel_label_category")
