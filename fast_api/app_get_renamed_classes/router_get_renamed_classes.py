# import asyncio
# from functools import partial
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from fastapi.responses import JSONResponse

from ML_BERT_classifier.class_bert import ClassifierBERT
from configs.console_colors import CONSOLE_COLORS
from configs.settings import (
    BERT_MODEL_NAMES, BERT_OPTIONS, ALCHEMY_OPTIONS)
from db_postgres.postgres_conn.pgs_connection import (
    PgsAsyncConnection)
from db_postgres.postgres_conn.postgres_session import (
    PgsAsyncSession)
from db_postgres.postgres_queries.qry_find_create_customer import (
    find_create_customer_qry)
from db_postgres.postgres_queries.qry_get_renamed_classes_by_customer_list import (
    get_renamed_classes_by_customer)
from fast_api.app_account_data.scheme_account_data import (
    AccountDataBert)
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from fast_api.app_auth.scheme_auth import AuthDataBert
from fast_api.fast_api_dependencies.dep_get_bert_model_instance import (
    get_bert_model_instance_dep)

bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_get_customer_renamed_classes = APIRouter(prefix=f"/{bert_base_url_name}",
                                                tags=["BERT"])


@router_get_customer_renamed_classes.post(path="/get_customer_renamed_classes_list/",
                                          # TODO: Describe responses here
                                          response_model=None)
async def get_renamed_classes_list(
        auth_data: AuthDataBert,
        account_data: AccountDataBert,
        bert_model_inst: Annotated[
            ClassifierBERT, Depends(get_bert_model_instance_dep)]
) -> JSONResponse:
    verify_prod_username_password(username=auth_data.username,
                                  password=auth_data.password)

    log_pgs_good_ops = ALCHEMY_OPTIONS.ALCHEMY_SESSION_OK_ACTIONS_LOGS

    account_id = account_data.account_id
    account_username = account_data.account_username
    try:
        print("Getting all customer categories list by account data:")
        datetime_start = datetime.now()

        print("Postgres DB Getting model origin and customer renamed classes:")
        pgs_conn = PgsAsyncConnection()
        async with PgsAsyncSession(engine=pgs_conn.engine,
                                   log_good_ops=log_pgs_good_ops
                                   ) as pgs_session:
            print("Postgres DB Finding-creating customer id:")
            creation_reason = "getting customer renamed classes"
            customer_id = await find_create_customer_qry(
                ongoing_session=pgs_session,
                account_username=account_username,
                account_id=account_id,
                creation_reason=creation_reason)

            print("Postgres DB Getting origin-renamed customer classes list:")
            orig_renamed_classes_list = await get_renamed_classes_by_customer(
                ongoing_session=pgs_session,
                customer_id=customer_id)

        getting_time = (datetime.now() - datetime_start).total_seconds()
        getting_time = round(getting_time, 1)

        json_response = JSONResponse(
            content={"message": "Getting model origin customer renamed classes [OK]",
                     "username": auth_data.username,
                     "model init": BERT_OPTIONS.BERT_MODEL_INIT,
                     "model name": BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED,
                     "model path": BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH,
                     "getting time": getting_time,
                     "customer_id": customer_id,
                     "orig_renamed_classes_list": orig_renamed_classes_list},
            status_code=status.HTTP_200_OK)

        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        reset_color = CONSOLE_COLORS.RESET
        print(f"BERT response.body: {json_response.body}\n"
              f"BERT response.status_code: {json_response.status_code}\n"
              f"username: {auth_data.username}\n"
              f"customer_id: {blue_color}{customer_id}{reset_color}\n"
              f"orig_renamed_classes_list: {blue_color}{orig_renamed_classes_list}{reset_color}\n"
              f"getting_time: {getting_time}\n")
        return json_response
    except Exception as error:
        log_text = (f"BERT Getting origin-renamed customer classes [ERROR]:"
                    f"error: {error}")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
