from configs.enums import USER_ROLE
from configs.settings import (
    ALCHEMY_OPTIONS, SQLADMIN_SUPERADMIN_PASSWORD, SQLADMIN_OPTIONS,
    SQLADMIN_ADMIN_PASSWORD, SQLADMIN_ADMIN_USERNAME,
    SQLADMIN_SUPERADMIN_USERNAME)
from db_postgres.postgres_conn.pgs_connection import PgsAsyncConnection
from db_postgres.postgres_conn.postgres_session import PgsAsyncSession
from db_postgres.postgres_models.auth_role_model import AuthRoleModel
from db_postgres.postgres_queries_utils.get_model_records_flex_query import (
    get_model_rows_flex_query)
from db_postgres.postgres_queries_utils.save_new_model_object import (
    save_new_model_object_qry)


async def create_default_sqladmin_users() -> bool | None:
    if not (SQLADMIN_OPTIONS.CREATE_DEFAULT_ADMIN_SUPERADMIN
            or SQLADMIN_OPTIONS.CREATE_DEBUG_ADMIN_SUPERADMIN):
        return None

    pgs_async_conn = PgsAsyncConnection()
    async with PgsAsyncSession(
            engine=pgs_async_conn.engine,
            log_good_ops=ALCHEMY_OPTIONS.ALCHEMY_SESSION_OK_ACTIONS_LOGS
    ) as pgs_async_session:
        sqladmin_users_objs = await get_model_rows_flex_query(
            orm_model_class=AuthRoleModel,
            ongoing_session=pgs_async_session,
            selected_fields=None,
            fields_values_filter=None,
            order_by_fields=None,
            return_scalars=True)
        if sqladmin_users_objs:
            print("SQLAdmin default users already exist [OK]")
            return None

        sqladmin_initial_users = []
        if SQLADMIN_OPTIONS.CREATE_DEFAULT_ADMIN_SUPERADMIN:
            sqladmin_default_users = [
                {"auth_username": SQLADMIN_SUPERADMIN_USERNAME,
                 "auth_hashed_password": SQLADMIN_SUPERADMIN_PASSWORD,
                 "auth_role": USER_ROLE.SUPERADMIN.value},
                {"auth_username": SQLADMIN_ADMIN_USERNAME,
                 "auth_hashed_password": SQLADMIN_ADMIN_PASSWORD,
                 "auth_role": USER_ROLE.ADMIN.value}, ]
            sqladmin_initial_users.extend(sqladmin_default_users)

        if SQLADMIN_OPTIONS.CREATE_DEBUG_ADMIN_SUPERADMIN:
            sqladmin_debug_users = [
                {"auth_username": "1",
                 "auth_hashed_password": "1",
                 "auth_role": USER_ROLE.SUPERADMIN.value},
                {"auth_username": "2",
                 "auth_hashed_password": "2",
                 "auth_role": USER_ROLE.ADMIN.value},
                {"auth_username": "3",
                 "auth_hashed_password": "3",
                 "auth_role": USER_ROLE.USER.value}, ]
            sqladmin_initial_users.extend(sqladmin_debug_users)

        for cur_sqladmin_user_data in sqladmin_initial_users:
            await save_new_model_object_qry(
                ModelClassORM=AuthRoleModel,
                ongoing_session=pgs_async_session,
                new_data=cur_sqladmin_user_data)

    print("SQLAdmin default users creation [OK]")
    return True
