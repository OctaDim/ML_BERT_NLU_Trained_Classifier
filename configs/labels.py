from dataclasses import dataclass


@dataclass(frozen=True)
class LABELS:
    ADMIN_PANEL = "АДМИН-ПАНЕЛЬ"
    DRAFT_CATEGORY_TEXT = "ЧЕРНОВИК:"
    DRAFTS_CATEGORY_TEXT = "ЧЕРНОВИКИ:"
    ICON = "ℹ️"
    ID = "ID"
    ACCOUNT_DATA = "АККАУНТ"
    ACCOUNT_ID = "AККАУНТ ID"
    ACCOUNT_USERNAME = "AККАУНТ USERNAME"
    EXISTING_CATEGORY = "КЛАСС В ДАТАСЕТЕ"
    EXISTING_TEXT = "ТЕКСТ В ДАТАСЕТЕ"
    DRAFT_CATEGORY = "КЛАСС В ЧЕРНОВИКЕ"
    DRAFT_TEXT = "ТЕКСТ В ЧЕРНОВИКЕ"
    DRAFT_STATUS = "СТАТУС ЧЕРНОВИКА"
    ACTIVE_STATUS = "АКТИВНЫЙ"
    CREATED = "СОЗДАНО"
    UPDATED = "ОБНОВЛЕНО"
