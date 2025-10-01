from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db_postgres.postgres_async_conn.pgs_async_connection import Base
from db_postgres.postgres_models.active_create_upd_mixins import (
    ActiveMixin, CreateUpdateMixin)


class LabelTextModel(Base, ActiveMixin, CreateUpdateMixin):
    __tablename__ = "label_text"

    id: Mapped[int] = mapped_column(primary_key=True)
    # dataset_id: Mapped[Optional[int]] = mapped_column(ForeignKey("dataset.id"))
    label_category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("label_category.id"))

    label_index_hint: Mapped[Optional[int]] = mapped_column()
    text: Mapped[str] = mapped_column()
    creation_reason: Mapped[Optional[str]] = mapped_column()

    # rel_label_category: Mapped["LabelCategoryModel"] = relationship(
    #     argument="LabelCategoryModel",
    #     # order_by='LabelCategoryModel.category_name',
    #     back_populates="rel_labels_texts")
