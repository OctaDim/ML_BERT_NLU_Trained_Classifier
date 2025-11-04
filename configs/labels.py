from dataclasses import dataclass


@dataclass(frozen=True)
class LABELS:
    ADMIN_PANEL = "Панель администратора"
    DRAFT_CATEGORY_TEXT = "ЧЕРНОВИК: КЛАСС-ТЕКСТ"
    DRAFTS_CATEGORY_TEXT = "ЧЕРНОВИКИ: КЛАСС-ТЕКСТ"
    ICON = "ℹ️"
    ID = "ID"
    ACCOUNT_ID = "Aкаунт-ID"
    ACCOUNT_USERNAME = "Aкаунт-Username"
    EXISTING_CATEGORY = "Категория в датасете"
    EXISTING_TEXT = "Текст в датасете"
    DRAFT_CATEGORY = "Категория в черновике"
    DRAFT_TEXT = "Текст в черновике"
    DRAFT_STATUS = "Статус черновика"
    CREATED = "Создано"
    UPDATED = "Обновлено"
