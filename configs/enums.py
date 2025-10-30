from enum import Enum


class USER_ROLE(Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    USER = "user"


class DRAFT_STATUS(Enum):
    DRAFT = "черновик"
    DATASET = "добавлен в датасет"
