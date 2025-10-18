import os
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from ML_BERT_classifier.class_bert import ClassifierBERT
from configs.console_colors import CONSOLE_COLORS
from configs.settings import (
    BASE_DIR, BERT_MODEL_NAMES, BERT_OPTIONS, REDIS_OPTIONS, STATUSES,
    ALCHEMY_OPTIONS)
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
from db_postgres.postgres_queries.qry_save_new_model_data import (
    save_new_model_data_qry)
from db_redis.redis_funcs.func_redis_save_key_mapping import (
    redis_save_key_mapping_dict)
from fast_api.app_account_data.scheme_account_data import (
    AccountDataBert)
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from fast_api.app_auth.scheme_auth import AuthDataBert
from fast_api.app_bert_save_model.scheme_bert_save_model import (
    SaveModelAfterTrainBert, SaveModelDataBert)
from utils_common.normalized_path import (
    get_full_file_normal_path)
from utils_specific.get_initial_dataset_dir_path import (
    get_initial_dataset_dir_path)
from utils_specific.get_last_saved_dataset_path import (
    get_last_saved_dataset_dir_path)
from utils_specific.get_new_model_dir_path import (
    get_new_model_random_dir_path)

bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_bert_save_model = APIRouter(prefix=f"/{bert_base_url_name}",
                                   tags=["BERT"])


@router_bert_save_model.post(path="/bert_save_model/",
                             # TODO: Describe responses here
                             response_model=None)
async def bert_save_model(
        auth_data: AuthDataBert,
        account_data: AccountDataBert,
        save_model_data: SaveModelDataBert,
        save_model_after_train_data: SaveModelAfterTrainBert,
        bert_model_inst: Annotated[
            ClassifierBERT, Depends(get_bert_model_instance_dep)],
        # dataset_name: str = None,
) -> JSONResponse:
    verify_prod_username_password(username=auth_data.username,
                                  password=auth_data.password)

    REDIS_KEY_EXPIRE_TIME = timedelta(days=REDIS_OPTIONS.STATUSES_EXPIRY_DAYS)
    log_pgs_good_ops = ALCHEMY_OPTIONS.ALCHEMY_SESSION_OK_ACTIONS_LOGS

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

    print("BERT saving model without train or after train process:")
    save_after_train_flag = save_model_after_train_data.trained_model_redirected_save_flag
    try:
        if save_after_train_flag:
            redis_update = {
                "train_status": STATUSES.STATUS_TRAINED_MODEL_SAVE_PROCESS_EN,
                "train_step_10_saving_model_after_train_in_process": "[OK]", }
            redis_error = await redis_save_key_mapping_dict(
                key_name=dataset_name,
                mapping_dict=redis_update,
                expiry_seconds=REDIS_KEY_EXPIRE_TIME)
            if redis_error:
                print(redis_error)

        if save_model_data.model_save_dir_path:
            model_save_path = save_model_data.model_save_dir_path
        else:
            print("Creating new dir path to save trained or saved model:")
            model_save_path = get_new_model_random_dir_path()
    except Exception as error:
        log_text = (f"Creating new trained model save dir path [ERROR]: "
                    f"error: {error}\n"
                    f"save_model_data.model_save_dir_path: "
                    f"{save_model_data.model_save_dir_path},"
                    f"BERT_OPTIONS.BERT_TRAINED_MODELS_SAVE_PATH: "
                    f"{BERT_OPTIONS.BERT_TRAINED_MODELS_BASE_PATH}")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=log_text)

    if not model_save_path:
        log_text = (f"Trained Models save dir path not defined [ERROR]: "
                    f"as req param 'model_save_dir_path' or in settings\n"
                    f"save_model_data.model_save_dir_path: "
                    f"{save_model_data.model_save_dir_path},"
                    f"BERT_OPTIONS.BERT_TRAINED_MODELS_SAVE_PATH: "
                    f"{BERT_OPTIONS.BERT_TRAINED_MODELS_BASE_PATH}")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=log_text)

    try:
        datetime_start = datetime.now()
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

        # Double attribute assigning in bert_model_inst.save_model()
        bert_model_inst.last_saved_model_dir = model_save_path

        print("Postgres DB Saving trained model data:")
        pgs_conn = PostgresConnection()
        async with PostgresSession(async_engine=pgs_conn.engine,
                                   log_good_ops=log_pgs_good_ops
                                   ) as pgs_session:
            if save_after_train_flag:
                creation_reason = f"trained and saved: {dataset_name}"
            else:
                creation_reason = f"saved without training: {dataset_name}"

            customer_id = await find_create_customer_qry(
                ongoing_session=pgs_session,
                account_username=account_data.account_username,
                account_id=account_data.account_id,
                creation_reason=creation_reason)

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

        model_saving_time = (datetime.now() - datetime_start).total_seconds()
        model_saving_time = round(model_saving_time, 1)

        new_model_path_dirs = model_save_path.split(os.sep)
        new_model_name = new_model_path_dirs[-1]  # Same as new model directory name

        if save_after_train_flag:
            redis_update = {
                "train_status": STATUSES.STATUS_TRAINED_MODEL_SAVE_FINISH_EN,
                "train_complete_status": "complete",
                "new_model_name": new_model_name,
                "model_saving_time": model_saving_time,
                "train_step_11_saving_model_after_training_finished": "[OK]", }
            redis_error = await redis_save_key_mapping_dict(
                key_name=dataset_name,
                mapping_dict=redis_update,
                expiry_seconds=REDIS_KEY_EXPIRE_TIME)
            if redis_error:
                print(redis_error)

        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        reset_color = CONSOLE_COLORS.RESET
        log_text = (
            f"BERT Model saved [OK]:\n"
            f"username: {auth_data.username}\n"
            f"Pretrained Model init: {BERT_OPTIONS.BERT_MODEL_INIT}\n"
            f"Pretrained Model name: {BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED}\n"
            f"Pretrained Model download dir: {BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH}\n"
            f"Trained Model common save dir: {BERT_OPTIONS.BERT_TRAINED_MODELS_BASE_PATH}\n"
            f"Trained Model saved dir path: {blue_color}{model_save_path}{reset_color}\n"
            f"Trained Model saving time: {model_saving_time}\n")

        if save_after_train_flag:
            log_text = (
                f"{log_text}\n"
                f"save after train redirected flag: {save_after_train_flag}\n"
                f"train dataset path: {save_model_after_train_data.redirected_train_text_lab_csv_path}\n"
                f"creating dataset time: {save_model_after_train_data.redirected_creating_dataset_time}\n"
                f"training model time: {blue_color}{save_model_after_train_data.redirected_training_time}{reset_color}\n")
        print(log_text)
        json_response = JSONResponse(
            content={"message": log_text},
            status_code=status.HTTP_200_OK)
        return json_response
    except Exception as error:
        log_text = f"BERT Model not saved [ERROR]: error: {error}"
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
