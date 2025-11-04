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
    DRAFT_ADDED: str = "Черновик"
    OVERRIDING_DRAFT_ADDED = "Черновик с Перекрытием"
    DRAFT_INACTIVE: str = "Неактивный Черновик"
    DATASET_ADDED: str = "Перенесено в Датасет"
    DRAFT_EXISTS: str = "Уже есть в Черновике"
    DATASET_EXISTS: str = "Уже есть в Датасете"
