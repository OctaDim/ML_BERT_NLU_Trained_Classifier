import os
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from ML_BERT_classifier.class_bert import ClassifierBERT
from configs.console_colors import CONSOLE_COLORS
from configs.settings import (
    BERT_MODEL_NAMES, BERT_OPTIONS, ALCHEMY_OPTIONS, BASE_DIR)
from db_postgres.postgres_async_conn.pgs_async_connection import (
    PostgresConnection)
from db_postgres.postgres_async_conn.postgres_async_session import (
    PostgresSession)
from db_postgres.postgres_dependencies.dep_get_bert_model_instance import (
    get_bert_model_instance_dep)
from db_postgres.postgres_models.trained_bert_model import (
    TrainedBertModel)
from db_postgres.postgres_queries.qry_find_create_customer import (
    find_create_customer_qry)
from db_postgres.postgres_queries.qry_find_create_dataset import (
    find_create_dataset_qry)
from db_postgres.postgres_queries.qry_get_last_dataset_name_and_dir import (
    get_last_dataset_name_and_dir_qry)
from db_postgres.postgres_queries.qry_get_last_saved_model_dir import (
    get_last_saved_model_dir_qry)
from db_postgres.postgres_queries.qry_save_new_model_data import (
    save_new_model_data_qry)
from fast_api.app_account_data.scheme_account_data import (
    AccountDataBert)
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from fast_api.app_auth.scheme_auth import AuthDataBert
from fast_api.app_bert_load_model.scheme_bert_load_model import (
    LoadModelDataBert)
from utils_common.normalized_path import (
    get_full_dir_normal_path, get_full_file_normal_path)
from utils_specific.get_initial_dataset_dir_path import (
    get_initial_dataset_dir_path)
from utils_specific.get_last_saved_dataset_path import (
    get_last_saved_dataset_dir_path)
from utils_specific.get_last_saved_model_dir import (
    get_last_saved_model_dir_path)
from utils_specific.get_new_model_dir_path import (
    get_new_model_random_dir_path)

bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_bert_load_model = APIRouter(prefix=f"/{bert_base_url_name}",
                                   tags=["BERT"])


@router_bert_load_model.post(path="/bert_load_model/",
                             response_model=None)
async def bert_load_model(
        auth_data: AuthDataBert,
        account_data: AccountDataBert,
        load_model_data: LoadModelDataBert,
        bert_model_inst: Annotated[
            ClassifierBERT, Depends(get_bert_model_instance_dep)]
) -> JSONResponse:
    verify_prod_username_password(username=auth_data.username,
                                  password=auth_data.password)

    log_pgs_good_ops = ALCHEMY_OPTIONS.ALCHEMY_SESSION_OK_ACTIONS_LOGS

    print("Getting load model directory path from request:")
    request_load_model_dir = load_model_data.model_load_dir_path
    inst_last_saved_model_dir, file_last_saved_model_dir = None, None
    if request_load_model_dir:
        model_load_path = request_load_model_dir
    else:
        print("Postgres DB Getting last saved model directory path:")
        pgs_conn = PostgresConnection()
        async with PostgresSession(async_engine=pgs_conn.engine,
                                   log_good_ops=log_pgs_good_ops
                                   ) as pgs_session:
            pgs_last_saved_model_dir = get_last_saved_model_dir_qry(
                ongoing_session=pgs_session)

        if pgs_last_saved_model_dir:
            last_saved_model_dir_path = pgs_last_saved_model_dir
        else:
            print("Getting last saved model directory path from instance:")
            inst_last_saved_model_dir = bert_model_inst.last_saved_model_dir
            file_last_saved_model_dir = None
            if inst_last_saved_model_dir:
                last_saved_model_dir_path = inst_last_saved_model_dir
            else:
                print("Getting last saved model directory path from file:")
                file_last_saved_model_dir = get_last_saved_model_dir_path()
                if file_last_saved_model_dir:
                    last_saved_model_dir_path = file_last_saved_model_dir
                else:
                    last_saved_model_dir_path = ""

            if not last_saved_model_dir_path:
                log_text = (
                    f"BERT Last saved directory model not found [ERROR]:\n"
                    f"inst_last_saved_model_dir: {inst_last_saved_model_dir}\n"
                    f"file_last_saved_model_dir: {file_last_saved_model_dir}\n"
                    f"last_saved_model_dir_path: {last_saved_model_dir_path}\n")
                print(log_text)
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail=log_text)
        model_load_path = last_saved_model_dir_path

    if not model_load_path:
        log_text = (f"BERT Model load dir path not defined [ERROR]: "
                    f"as request parameter 'model_load_dir_path' "
                    f"or method save_model() not called before\n"
                    f"request_load_model_dir: {request_load_model_dir}, "
                    f"pgs_last_saved_model_dir: {pgs_last_saved_model_dir}, "
                    f"inst_last_saved_model_dir: {inst_last_saved_model_dir}"
                    f"file_last_saved_model_dir: {file_last_saved_model_dir}")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=log_text)

    if not os.path.isdir(model_load_path):
        log_text = (f"BERT Model load directory path not exists [ERROR]: "
                    f"model_load_path: {model_load_path}")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)

    try:
        normal_model_load_path = get_full_dir_normal_path([model_load_path, ])

        datetime_start = datetime.now()
        error_log = bert_model_inst.load_model(
            dir_full_path=normal_model_load_path)
        # TODO: Make loading dataset from the the saved/loaded model
        #  directory also and creating new updated csv dataset directory
        #  and saving path in the last saved dataset ini file
        if error_log:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_log)

        model_load_time = (datetime.now() - datetime_start).total_seconds()
        model_load_time = round(model_load_time, 1)

        print("Creating new directory path to save loaded model:")
        model_save_path = get_new_model_random_dir_path()

        print("BERT saving model after loading:")
        error_log = bert_model_inst.save_model(
            dir_full_path=model_save_path)
        # TODO: Make saving learning dataset into the saved model dir also
        #  to have opportunity to load model and to load corresponding
        #  dataset for the model
        if error_log:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_log)

        last_saved_model_ini_fpath = get_full_file_normal_path(
            all_dir_str_parts=[BASE_DIR],
            file_name_with_ext=BERT_OPTIONS.BERT_LAST_SAVED_MODEL_INI_FILE_PATH)
        last_saved_model_ini_fdir = os.path.dirname(
            last_saved_model_ini_fpath)
        os.makedirs(name=last_saved_model_ini_fdir, exist_ok=True)
        with open(file=last_saved_model_ini_fpath,
                  mode="w", encoding="utf-8") as model_ini_file:
            model_ini_file.write(model_save_path)

        # Double attribute assigning for bert_model_inst.load_model()
        bert_model_inst.last_saved_model_dir = normal_model_load_path

        print("Postgres DB Getting last saved dataset directory and dataset name:")
        pgs_conn = PostgresConnection()
        async with PostgresSession(async_engine=pgs_conn.engine,
                                   log_good_ops=log_pgs_good_ops
                                   ) as pgs_session:
            pgs_last_dataset_data = await get_last_dataset_name_and_dir_qry(
                ongoing_session=pgs_session)

        if pgs_last_dataset_data:
            train_dataset_dir = pgs_last_dataset_data[1]
            dataset_name = pgs_last_dataset_data[0]
        else:
            print("Getting csv last saved dataset directory and dataset name:")
            inst_last_saved_dataset_path = bert_model_inst.last_saved_dataset_dir
            last_saved_dataset_dir_path, initial_dataset_dir_path = None, None
            if inst_last_saved_dataset_path:
                train_dataset_dir = inst_last_saved_dataset_path
            else:
                last_saved_dataset_dir_path = get_last_saved_dataset_dir_path()
                if last_saved_dataset_dir_path:
                    train_dataset_dir = last_saved_dataset_dir_path
                else:
                    initial_dataset_dir_path = get_initial_dataset_dir_path()
                    if initial_dataset_dir_path:
                        train_dataset_dir = initial_dataset_dir_path
                    else:
                        train_dataset_dir = ""
            if not train_dataset_dir:
                log_text = (
                    f"BERT Train dataset directory or files not found [ERROR]:\n"
                    f"inst_last_saved_dataset_path: {inst_last_saved_dataset_path}\n"
                    f"last_saved_dataset_dir_path: {last_saved_dataset_dir_path}\n"
                    f"initial_dataset_dir_path: {initial_dataset_dir_path}\n"
                    f"train_dataset_dir: {train_dataset_dir}\n")
                print(log_text)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=log_text)

            dataset_path_dirs = train_dataset_dir.split(os.sep)
            dataset_name = dataset_path_dirs[-1]  # As dataset files directory name

        print("Postgres DB Saving trained model data:")
        pgs_conn = PostgresConnection()
        async with PostgresSession(async_engine=pgs_conn.engine,
                                   log_good_ops=log_pgs_good_ops
                                   ) as pgs_session:
            creation_reason = (f"loaded and saved: {dataset_name}, "
                               f"loaded from: {normal_model_load_path}, "
                               f"saved to: {model_save_path}")

            customer_id = await find_create_customer_qry(
                ongoing_session=pgs_session,
                account_username=account_data.account_username,
                account_id=account_data.account_id)

            dataset_id = await find_create_dataset_qry(
                ongoing_session=pgs_session,
                dataset_name=dataset_name,
                customer_id=customer_id,
                dataset_csv_dir=train_dataset_dir,
                creation_reason=creation_reason)

            trained_model_upd_data = {
                "dataset_id": dataset_id,
                "dataset_name": dataset_name,
                "model_directory": model_save_path,
                "creation_reason": creation_reason}
            await save_new_model_data_qry(
                ModelClassORM=TrainedBertModel,
                ongoing_session=pgs_session,
                new_data=trained_model_upd_data)

        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        reset_color = CONSOLE_COLORS.RESET
        log_text = (
            f"BERT Model loaded [OK]:\n"
            f"username: {auth_data.username}\n"
            f"Pretrained Model init: {BERT_OPTIONS.BERT_MODEL_INIT}\n"
            f"Pretrained Model name: {BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED}\n"
            f"Pretrained Model download dir: {BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH}\n"
            f"Trained Model common load dir: {BERT_OPTIONS.BERT_TRAINED_MODELS_BASE_PATH}\n"
            f"Trained Model loaded dir path: {blue_color}{normal_model_load_path}{reset_color}\n"

            f"Trained Model loading time: {model_load_time}\n")
        print(log_text)

        json_response = JSONResponse(
            content={"message": log_text},
            status_code=status.HTTP_200_OK)
        return json_response
    except Exception as error:
        log_text = f"BERT Model not loaded [ERROR]: error: {error}"
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
