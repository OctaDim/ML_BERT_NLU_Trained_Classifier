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
    DRAFT_ADDED: str = "ЧЕРНОВИК C НОВЫМ ТЕКСТОМ"
    OVERRIDING_DRAFT_ADDED = "черновик с перекрытием класса"
    NEW_TEXT_CLASS_DRAFT_ADDED = "черновик с новым текстом/классом"
    NEW_CLASS_DRAFT_ADDED = "ЧЕРНОВИК с НОВЫМ КЛАССОМ"
    DRAFT_INACTIVE: str = "неактивный черновик"
    DATASET_ADDED: str = "перенесено в датасет"
    DRAFT_EXISTS: str = "уже есть в черновике"
    DATASET_EXISTS: str = "уже есть в датасете"
