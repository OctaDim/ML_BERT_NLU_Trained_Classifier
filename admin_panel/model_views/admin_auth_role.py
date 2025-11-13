from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse

from db_postgres.postgres_conn.pgs_connection import (
    PgsAsyncConnection)
from db_postgres.postgres_conn.postgres_session import (
    PgsAsyncSession)
from db_postgres.postgres_models.auth_role_model import AuthRoleModel
from db_postgres.postgres_queries_utils.get_model_records_flex_query import (
    get_model_rows_flex_query)
from utils_common.hash_verify_password import verify_password


class AdminAuthRoleAuthBackend(AuthenticationBackend):
    async def signup(self):
        pass

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        pgs_conn = PgsAsyncConnection()
        async with PgsAsyncSession(engine=pgs_conn.engine
                                   ) as pgs_session:

            fields_filter = {"auth_username": username,
                             "active": True}

            auth_role_list = await get_model_rows_flex_query(
                orm_model_class=AuthRoleModel,
                ongoing_session=pgs_session,
                selected_fields=None,
                fields_values_filter=fields_filter,
                order_by_fields=None,
                return_scalars=True)

        auth_role_obj = auth_role_list[0] if auth_role_list else None

        if not auth_role_obj:
            return False

        password_is_valid = verify_password(
            plain_password=password,
            hashed_password=auth_role_obj.auth_hashed_password,
            compare_not_hashed=True)

        if password_is_valid:
            auth_role = auth_role_obj.auth_role.value
            request.session.update({"session_token": "auth-token",  # Temporary
                                    "auth_role": auth_role})
            print(f"Admin Panel: Admin authorised [OK]: "
                  f"{auth_role}: auth_role")
            return True
        else:  # Not authorised
            print(f"Admin Panel: Admin not authorised [ERROR]: "
                  f"auth_username: {auth_role_obj.auth_username}")
            return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        print("Admin Panel: Admin logout [OK]")
        return True

    async def authenticate(self, request: Request) -> bool | RedirectResponse:
        token = request.session.get("session_token")
        if token and token == "auth-token":
            print("Admin Panel: Session token is valid [OK]")
            return True
        else:
            print("Admin Panel: Session token is empty or not valid [ERROR]")
            # return RedirectResponse(request.url_for("admin:login"), status_code=302)
            return False
