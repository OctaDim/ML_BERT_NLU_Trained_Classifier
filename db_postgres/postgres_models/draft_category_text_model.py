from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from configs.enums import DRAFT_STATUS
from db_postgres.postgres_async_conn.pgs_async_connection import Base
from db_postgres.postgres_models.orm_models_fields_mixins import (
    ActiveMix, CreateUpdateMix)


class DraftCategoryTextModel(Base, ActiveMix, CreateUpdateMix):
    __tablename__ = "draft_category_text"

    id: Mapped[int] = mapped_column(primary_key=True)

    account_id: Mapped[str] = mapped_column()
    account_username: Mapped[str] = mapped_column()

    existing_category: Mapped[str] = mapped_column()
    draft_category: Mapped[str] = mapped_column()
    draft_text: Mapped[str] = mapped_column()

    current_status: Mapped[Optional[DRAFT_STATUS]] = mapped_column(
        default=DRAFT_STATUS.DRAFT)
