from typing import Optional

from sqlalchemy import ForeignKey, Enum
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

from configs.enums import DRAFT_STATUS, NEW_STATUS
from db_postgres.postgres_init.declarative_base_model import Base
from db_postgres.postgres_models.orm_models_fields_mixins import (
    ActiveMix, CreateUpdateMix, CreateReasonMix)


class DraftCategoryTextModel(Base, ActiveMix,
                             CreateReasonMix, CreateUpdateMix):
    __tablename__ = "draft_category_text"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("customer.id"))

    account_id: Mapped[str] = mapped_column()
    account_username: Mapped[str] = mapped_column()

    ds_existing_category: Mapped[Optional[str]] = mapped_column()
    draft_category: Mapped[str] = mapped_column()
    ds_existing_text: Mapped[Optional[str]] = mapped_column()
    draft_text: Mapped[Optional[str]] = mapped_column()

    current_status: Mapped[DRAFT_STATUS] = mapped_column(
        Enum(DRAFT_STATUS, values_callable=lambda obj: [e.value for e in obj]),
        default=DRAFT_STATUS.NEW_TEXT_DRAFT_ADDED)
    # current_status: Mapped[DRAFT_STATUS] = mapped_column(
    #     default=DRAFT_STATUS.NEW_TEXT_DRAFT_ADDED)

    # new_category: Mapped[Optional[NEW_STATUS]] = mapped_column(
    #     Enum(NEW_STATUS, values_callable=lambda obj: [e.value for e in obj]),
    #     default=NEW_STATUS.NEW_RECORD)
    #
    # new_text: Mapped[Optional[NEW_STATUS]] = mapped_column(
    #     Enum(NEW_STATUS, values_callable=lambda obj: [e.value for e in obj]),
    #     default=NEW_STATUS.NEW_RECORD)

    @hybrid_property
    def account_data(self):
        username_str = self.account_username or "_____"
        id_str = self.account_id or "___"
        field_value = f"{username_str} / {id_str}"
        return field_value
