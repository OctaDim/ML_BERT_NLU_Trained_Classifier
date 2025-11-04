from dataclasses import dataclass


@dataclass(frozen=True)
class LABELS:
    ADMIN_PANEL = "Панель администратора"
    DRAFT_CATEGORY_TEXT = "ЧЕРНОВИК: КЛАСС-ТЕКСТ"
    DRAFTS_CATEGORY_TEXT = "ЧЕРНОВИКИ: КЛАСС-ТЕКСТ"
    ICON = "ℹ️"
    ID = "ID"
    ACCOUNT_DATA = "Акаунт"
    ACCOUNT_ID = "Aкаунт ID"
    ACCOUNT_USERNAME = "Aкаунт Username"
    EXISTING_CATEGORY = "Класс в датасете"
    EXISTING_TEXT = "Текст в датасете"
    DRAFT_CATEGORY = "Класс в Черновике"
    DRAFT_TEXT = "Текст в черновике"
    DRAFT_STATUS = "Статус черновика"
    ACTIVE_STATUS = "Активный"
    CREATED = "Создано"
    UPDATED = "Обновлено"
