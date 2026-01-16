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
from db_postgres.postgres_queries.qry_create_update_renamed_class import (
    create_update_renamed_class_qry)
from fast_api.app_account_data.scheme_account_data import (
    AccountDataBert)
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from fast_api.app_auth.scheme_auth import AuthDataBert
from fast_api.app_save_renamed_class.scheme_save_renamed_class import (
    SaveRenamedClassInData)
from fast_api.fast_api_dependencies.dep_get_bert_model_instance import (
    get_bert_model_instance_dep)

bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_save_renamed_class_data = APIRouter(prefix=f"/{bert_base_url_name}",
                                           tags=["BERT"])


@router_save_renamed_class_data.post(path="/save_renamed_class/",
                                     # TODO: Describe responses here
                                     response_model=None)
async def save_renamed_class_data(
        auth_data: AuthDataBert,
        account_data: AccountDataBert,
        renamed_class_data: SaveRenamedClassInData,
        bert_model_inst: Annotated[
            ClassifierBERT, Depends(get_bert_model_instance_dep)]
) -> JSONResponse:
    verify_prod_username_password(username=auth_data.username,
                                  password=auth_data.password)

    log_pgs_good_ops = ALCHEMY_OPTIONS.ALCHEMY_SESSION_OK_ACTIONS_LOGS

    account_id = account_data.account_id
    account_username = account_data.account_username
    label_category_id = renamed_class_data.label_category_id
    model_class_name = renamed_class_data.model_class_name
    renamed_class_name = renamed_class_data.renamed_class_name

    try:
        print("Postgres DB Saving customer renamed class:")
        datetime_start = datetime.now()

        pgs_conn = PgsAsyncConnection()
        async with PgsAsyncSession(engine=pgs_conn.engine,
                                   log_good_ops=log_pgs_good_ops
                                   ) as pgs_session:
            print("Postgres DB Finding-creating customer id:")
            customer_creation_reason = (
                f"saving customer renamed class: "
                f"account_id: {account_id}, "
                f"account_username: {account_username}")
            customer_id = await find_create_customer_qry(
                ongoing_session=pgs_session,
                account_username=account_username,
                account_id=account_id,
                creation_reason=customer_creation_reason)

            print("Postgres DB Creating-updating customer renamed class:")
            renamed_class_creation_reason = (
                f"saving customer renamed class: "
                f"account_id: {account_id}, "
                f"account_username: {account_username}")
            renamed_class_id = await create_update_renamed_class_qry(
                ongoing_session=pgs_session,
                customer_id=customer_id,
                label_category_id=label_category_id,
                renamed_class_name=renamed_class_name,
                creation_reason=renamed_class_creation_reason)

        saving_time = (datetime.now() - datetime_start).total_seconds()
        saving_time = round(saving_time, 1)

        json_response = JSONResponse(
            content={"message": "Saving customer renamed class [OK]",
                     "username": auth_data.username,
                     "model init": BERT_OPTIONS.BERT_MODEL_INIT,
                     "model name": BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED,
                     "model path": BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH,
                     "saving time": saving_time,
                     "customer_id": customer_id,
                     "renamed_class_id": renamed_class_id,
                     "model_class_name": model_class_name,
                     "renamed_class_name": renamed_class_name},
            status_code=status.HTTP_200_OK)

        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        reset_color = CONSOLE_COLORS.RESET
        print(f"BERT response.body: {json_response.body}\n"
              f"BERT response.status_code: {json_response.status_code}\n"
              f"username: {auth_data.username}\n"
              f"customer_id: {customer_id}\n"
              f"label_category_id: {label_category_id}\n"
              f"model_class_name: {model_class_name}\n"
              f"renamed_class_id: {blue_color}{renamed_class_id}{reset_color}\n"
              f"renamed_class_name: {blue_color}{renamed_class_name}{reset_color}\n"
              f"saving_time: {saving_time}\n")
        return json_response
    except Exception as error:
        log_text = (f"BERT Saving renamed customer classes [ERROR]: "
                    f"error: {error}")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
