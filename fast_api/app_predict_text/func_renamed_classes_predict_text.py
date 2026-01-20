from sqlalchemy.ext.asyncio import AsyncSession

from configs.settings import ALCHEMY_OPTIONS
from db_postgres.postgres_conn.pgs_connection import PgsAsyncConnection
from db_postgres.postgres_conn.postgres_session import PgsAsyncSession
from db_postgres.postgres_queries.qry_find_create_customer import (
    find_create_customer_qry)
from db_postgres.postgres_queries.qry_get_id_category_dict import (
    get_id_category_dict_qry)
from db_postgres.postgres_queries.qry_get_renamed_class_category_id_dict import (
    get_renamed_class_cat_id_dict)
from fast_api.app_account_data.scheme_account_data import (
    AccountDataBert)


async def renamed_classes_predict_single_text(
        account_data: AccountDataBert,
        predicted_category: str
) -> None:
    print("BERT Renamed classes prediction by single text func:")
    log_pgs_good_ops = ALCHEMY_OPTIONS.ALCHEMY_SESSION_OK_ACTIONS_LOGS

    account_id = account_data.account_id
    account_username = account_data.account_username

    pgs_conn = PgsAsyncConnection()
    async with PgsAsyncSession(engine=pgs_conn.engine,
                               log_good_ops=log_pgs_good_ops
                               ) as pgs_session:
        customer_creation_reason = (f"renamed classes predict text: "
                                    f"account_id: {account_id}, "
                                    f"account_username: {account_username}")
        customer_id = await find_create_customer_qry(
            ongoing_session=pgs_session,
            account_id=account_id,
            account_username=account_username,
            creation_reason=customer_creation_reason)

        category_id_dict = await get_id_category_dict_qry(
            ongoing_session=pgs_session,
            reversed_category_id_dict=True)

        cat_id_renamed_class_dict = await get_renamed_class_cat_id_dict(
            ongoing_session=pgs_session,
            customer_id=customer_id,
            reversed_cat_id_renamed_class_dict=True)

        predicted_cat_id = category_id_dict[predicted_category]  # Some PyCharm bug. Annotation and variable value is ok

        renamed_class = cat_id_renamed_class_dict.get(predicted_cat_id)
    return renamed_class
