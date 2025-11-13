from enum import Enum


class USER_ROLE(Enum):
    """NOTE: If changed enums names here, containing tables and data
    types also should be deleted and reinitialized in Postgres DB"""
    SUPERADMIN: str = "superadmin"
    ADMIN: str = "admin"
    USER: str = "user"


class DRAFT_STATUS(Enum):
    """NOTE: If changed enums names here, containing tables and data
    types also should be deleted and reinitialized in Postgres DB"""
    NEW_TEXT_DRAFT_ADDED: str = "ЧЕРНОВИК с НОВЫМ ТЕКСТОМ"
    NEW_CLASS_DRAFT_ADDED = "ЧЕРНОВИК с НОВЫМ КЛАССОМ"
    OVERRIDING_DRAFT_ADDED = "черновик с перекрытием класса"
    NEW_TEXT_CLASS_DRAFT_ADDED = "черновик с новым текстом/классом"
    DRAFT_INACTIVE: str = "неактивный черновик"
    NEW_TEXT_DATASET_ADDED: str = "текст перенесен в датасет"
    NEW_CLASS_DATASET_ADDED: str = "класс перенесен в датасет"
    DRAFT_EXISTS: str = "уже есть в черновике"
    DATASET_EXISTS: str = "уже есть в датасете"

class NEW_STATUS(Enum):
    NEW_RECORD: str = "new"
