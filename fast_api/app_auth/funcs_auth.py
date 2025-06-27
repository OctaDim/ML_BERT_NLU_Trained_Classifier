from typing import Union

from fastapi import HTTPException, status

from configs.settings import API_PASSWORD, API_TEST_PASSWORD, API_TEST_USERNAME, API_USERNAME


def verify_prod_username_password(username: str, password: str
                                  ) -> Union[bool, HTTPException]:
    if username != API_USERNAME or password != API_PASSWORD:
        log_text = (f"Wrong test username or test password [ERROR]:"
                    f"username: {username}, password: ***")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=log_text)
    return True


def verify_test_username_password(username: str, password: str
                                  ) -> Union[bool, HTTPException]:
    if username != API_TEST_USERNAME or password != API_TEST_PASSWORD:
        log_text = (f"Wrong product username or product password [ERROR]:"
                    f"username: {username}, password: ***")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=log_text)
    return True
