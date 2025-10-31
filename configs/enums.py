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
    DRAFT_ADDED: str = "draft"
    DRAFT_INACTIVE: str = "inactive draft"
    DATASET_ADDED: str = "dataset added"
    DRAFT_EXISTS: str = "exists in draft"
    DATASET_EXISTS: str = "exists in dataset"
