from pydantic import BaseModel


class AccountDataBert(BaseModel):
    account_username: str = None
    account_id: str = None
    # account_username: str = "globalhome"  # DEBUG ONLY
    # account_id: str = "30"  # DEBUG ONLY
