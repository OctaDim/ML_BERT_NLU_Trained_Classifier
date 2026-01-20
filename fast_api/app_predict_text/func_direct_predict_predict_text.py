from configs.settings import ALCHEMY_OPTIONS
from db_postgres.postgres_conn.pgs_connection import PgsAsyncConnection
from db_postgres.postgres_conn.postgres_session import PgsAsyncSession
from db_postgres.postgres_queries.qry_get_direct_category_by_text import (
    get_direct_category_by_text)
from fast_api.app_account_data.scheme_account_data import (
    AccountDataBert)


async def direct_predict_predict_single_text(
        account_data: AccountDataBert,
        text_phrase: str
) -> str:
    print("BERT Direct prediction by single text func:")
    log_pgs_good_ops = ALCHEMY_OPTIONS.ALCHEMY_SESSION_OK_ACTIONS_LOGS

    pgs_conn = PgsAsyncConnection()
    async with PgsAsyncSession(engine=pgs_conn.engine,
                               log_good_ops=log_pgs_good_ops
                               ) as pgs_session:
        pgs_direct_category = await get_direct_category_by_text(
            ongoing_session=pgs_session,
            account_id=account_data.account_id,
            account_username=account_data.account_username,
            direct_text=text_phrase)
    return pgs_direct_category
