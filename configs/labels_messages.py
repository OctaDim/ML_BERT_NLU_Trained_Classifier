from dataclasses import dataclass


@dataclass(frozen=True)
class LABELS:
    ADMIN_PANEL = "АДМИН-ПАНЕЛЬ"
    DRAFT_CATEGORY_TEXT = "ЧЕРНОВИК:"
    DRAFTS_CATEGORIES_TEXT = "ЧЕРНОВИКИ:"
    DIRECT_PREDICT_TEXT = "ПРЯМОЕ ПРЕДСКАЗАНИЕ"
    DIRECT_PREDICTS_TEXT = "ПРЯМЫЕ ПРЕДСКАЗАНИЯ"
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
    ACTIVE_STATUS = "РАЗРЕШЁННЫЕ"
    CREATED = "СОЗДАНО"
    UPDATED = "ОБНОВЛЕНО"
    ALLOWED_RECS = "Разрешённые ✅"
    NOT_ALLOWED_RECS = "Неразрешённые ❌"
    ALL_RECS = "Все"
    NEW_RECS = "Новые записи"
    NEW_CLASS_ONLY = "Класс новый"
    NEW_TEXT_ONLY = "Текст новый"
    NEW_CLASS_AND_TEXT = "Класс и Текст новый"
    FILTER_ALLOWED = "РАЗРЕШЁННЫЕ"
    FILTER_NEW_DRAFT = "НОВЫЕ ЧЕРНОВИКИ"
    FILTER_ACCOUNT_DATA = "АККАУНТ"
    FILTER_ACCOUNT_ID = "АККАУНТ ID"
    FILTER_ACCOUNT_USERNAME = "АККАУНТ USERNAME"
    FILTER_DRAFT_CATEGORY = "КЛАСС"
    FILTER_DRAFT_TEXT = "ТЕКСТ"


@dataclass(frozen=True)
class MESSAGES:
    DATASET_ACTION_NAME = "ДОБАВИТЬ ВЫБРАННЫЕ ЧЕРНОВИКИ В ОБУЧАЮЩИЙ ДАТАСЕТ"
    DATASET_CONFIRM_MSG = "ПОДТВЕРДИТЕ ДОБАВЛЕНИЕ В ОБУЧАЮЩИЙ ДАТАСЕТ ⁉️"
    RECORDS_NOT_SELECTED = "НЕ ВЫБРАНО НИ ОДНОГО ЧЕРНОВИКА"
    DRAFTS_NOT_ALLOWED = "ВЫБРАНЫ НЕРАЗРЕШЁННЫЕ ЧЕРНОВИКИ"
    DRAFTS_ADDED_SUCCESS = "ЧЕРНОВИКИ ДОБАВЛЕНЫ УСПЕШНО"
    DRAFTS_SKIPPED = "ЧЕРНОВИКИ ПРОПУЩЕНЫ"
