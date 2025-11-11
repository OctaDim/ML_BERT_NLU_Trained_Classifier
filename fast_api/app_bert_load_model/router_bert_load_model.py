import json
import os
import shutil
from datetime import datetime
from typing import Annotated

import aiofiles
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from ML_BERT_classifier.class_bert import ClassifierBERT
from configs.console_colors import CONSOLE_COLORS
from configs.hard_constants import HARD_CONST
from configs.settings import (
    BERT_MODEL_NAMES, BERT_OPTIONS, ALCHEMY_OPTIONS, BASE_DIR)
from db_postgres.postgres_conn_async.pgs_async_connection import (
    PgsAsyncConnection)
from db_postgres.postgres_conn_async.postgres_async_session import (
    PgsAsyncSession)
from db_postgres.postgres_dependencies.dep_get_bert_model_instance import (
    get_bert_model_instance_dep)
from db_postgres.postgres_models.direct_predict_model import (
    DirectPredictModel)
from db_postgres.postgres_models.trained_bert_model import (
    TrainedBertModel)
from db_postgres.postgres_queries.deactivate_all_model_records_query import (
    deactivate_all_model_records_qry)
from db_postgres.postgres_queries.qry_find_create_customer import (
    find_create_customer_qry)
from db_postgres.postgres_queries.qry_find_create_dataset import (
    find_create_dataset_qry)
from db_postgres.postgres_queries.qry_get_last_saved_model_dir import (
    get_last_saved_model_dir_qry)
from db_postgres.postgres_queries.qry_save_direct_categ_text_dicts_list import (
    save_direct_cat_text_dicts_list_qry)
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
from utils_specific.class_csv_direct_categories_texts import (
    CsvDirectCategoryText)
from utils_specific.get_last_saved_model_dir import (
    get_last_saved_model_dir_path)
from utils_specific.get_new_dataset_dir_path import (
    get_new_dataset_rand_dir_path)
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
        pgs_conn = PgsAsyncConnection()
        async with PgsAsyncSession(async_engine=pgs_conn.engine,
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
        print("Model: Loading model data from directory")
        datetime_start = datetime.now()
        model_load_path = get_full_dir_normal_path([model_load_path])
        error_log = bert_model_inst.load_model(
            model_load_dir_path=model_load_path)
        if error_log:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_log)

        model_load_time = (datetime.now() - datetime_start).total_seconds()
        model_load_time = round(model_load_time, 1)

        print("Dataset: Creating new random dir path to save loaded dataset:")
        datetime_start = datetime.now()
        dataset_save_new_dir_path = get_new_dataset_rand_dir_path()
        dataset_save_path_dirs = dataset_save_new_dir_path.split(os.sep)
        dataset_save_new_name = dataset_save_path_dirs[-1]  # Dataset dir as dataset name

        print("Dataset: Copying model loaded dataset into new random dir:")
        loaded_model_extra_data_fpath = get_full_file_normal_path(
            all_dir_str_parts=[model_load_path,
                               HARD_CONST.SAVED_MODEL_EXTRA_DIR],
            file_name_with_ext=HARD_CONST.SAVED_MODEL_EXTRA_DATA_JSON_FN)
        async with (aiofiles.open(
                file=loaded_model_extra_data_fpath,
                mode="r", encoding="utf-8") as model_extra_data_f):
            json_data = await model_extra_data_f.read()
            loaded_model_extra_data = json.loads(json_data)

        loaded_model_dataset_name = loaded_model_extra_data["saved dataset name"]
        loaded_model_dataset_subdir = get_full_dir_normal_path(
            all_dir_str_parts=[model_load_path,
                               HARD_CONST.SAVED_MODEL_EXTRA_DIR,
                               loaded_model_dataset_name])
        shutil.copytree(src=loaded_model_dataset_subdir,
                        dst=dataset_save_new_dir_path,
                        dirs_exist_ok=True)

        print("Dataset: Saving last saved dataset dir path into ini file")
        last_saved_dataset_ini_fpath = get_full_file_normal_path(
            all_dir_str_parts=[BASE_DIR],
            file_name_with_ext=BERT_OPTIONS.BERT_LAST_SAVED_DATASET_INI_FILE_PATH)
        last_saved_dataset_ini_fdir = os.path.dirname(
            last_saved_dataset_ini_fpath)
        os.makedirs(name=last_saved_dataset_ini_fdir, exist_ok=True)
        with open(file=last_saved_dataset_ini_fpath,
                  mode="w", encoding="utf-8") as dataset_ini_file:
            dataset_ini_file.write(dataset_save_new_dir_path)

        dataset_load_copy_time = (datetime.now() - datetime_start).total_seconds()
        dataset_load_copy_time = round(dataset_load_copy_time, 1)

        print("Model: Creating new random dir path to save loaded model:")
        datetime_start = datetime.now()
        model_save_rand_path = get_new_model_random_dir_path()

        print("Model: BERT saving model after loading:")
        error_log = bert_model_inst.save_model(
            model_save_dir_path=model_save_rand_path,
            dataset_save_dir_path=dataset_save_new_dir_path)
        if error_log:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_log)

        print("Model: Saving last saved model dir path into ini file")
        last_saved_model_ini_fpath = get_full_file_normal_path(
            all_dir_str_parts=[BASE_DIR],
            file_name_with_ext=BERT_OPTIONS.BERT_LAST_SAVED_MODEL_INI_FILE_PATH)
        last_saved_model_ini_fdir = os.path.dirname(
            last_saved_model_ini_fpath)
        os.makedirs(name=last_saved_model_ini_fdir, exist_ok=True)
        with open(file=last_saved_model_ini_fpath,
                  mode="w", encoding="utf-8") as model_ini_file:
            model_ini_file.write(model_save_rand_path)

        model_save_time = (datetime.now() - datetime_start).total_seconds()
        model_save_time = round(model_save_time, 1)

        print("Extra Data: Copying loaded model dataset into extra dir")
        datetime_start = datetime.now()
        model_save_rand_dir_subdir = get_full_dir_normal_path(
            all_dir_str_parts=[model_save_rand_path,
                               HARD_CONST.SAVED_MODEL_EXTRA_DIR,
                               dataset_save_new_name])
        shutil.copytree(src=loaded_model_dataset_subdir,
                        dst=model_save_rand_dir_subdir,
                        dirs_exist_ok=True)

        print("Extra Data: Writing loaded model-dataset extra data into json")
        model_save_rand_path_dirs = model_save_rand_path.split(os.sep)
        model_save_rand_name = model_save_rand_path_dirs[-1]  # Same as new model directory name

        saved_model_extra_dir_path = get_full_dir_normal_path(
            all_dir_str_parts=[model_save_rand_path,
                               HARD_CONST.SAVED_MODEL_EXTRA_DIR])
        os.makedirs(saved_model_extra_dir_path, exist_ok=True)

        saved_model_extra_data_fpath = get_full_file_normal_path(
            all_dir_str_parts=[model_save_rand_path,
                               HARD_CONST.SAVED_MODEL_EXTRA_DIR],
            file_name_with_ext=HARD_CONST.SAVED_MODEL_EXTRA_DATA_JSON_FN)
        saved_model_extra_data = {
            "saved model name": model_save_rand_name,
            "saved dataset name": dataset_save_new_name,
            "original model saving path": model_save_rand_path,
            "original dataset saving path": dataset_save_new_dir_path,
            "account_id": account_data.account_id,
            "account_username": account_data.account_username,
            # "save_after_train_flag": save_after_train_flag,
            "original dataset name": loaded_model_dataset_name,
            "original dataset dir": loaded_model_dataset_subdir}
        async with aiofiles.open(
                file=saved_model_extra_data_fpath,
                mode="w", encoding="utf-8") as model_extra_data_f:
            json_data = json.dumps(obj=saved_model_extra_data,
                                   indent=4, ensure_ascii=False)
            await model_extra_data_f.write(json_data)

        extra_data_save_time = (datetime.now() - datetime_start).total_seconds()
        extra_data_save_time = round(extra_data_save_time, 1)

        print("Saving last saved model and dataset dir path into instance attrs")
        bert_model_inst.last_saved_model_dir = model_save_rand_path  # Double assigning attr in addition to save_model()
        bert_model_inst.last_saved_dataset_dir = dataset_save_new_dir_path  # Double assigning attr in addition to save_model()

        print("Getting loaded-copied csv category-text file path:")
        direct_cat_text_csv_f_name = BERT_OPTIONS.BERT_DIRECT_CATEGORY_TEXT_CSV_FILE_NAME
        loaded_direct_cat_text_fpath = get_full_file_normal_path(
            all_dir_str_parts=[loaded_model_dataset_subdir],  # equal dataset_save_new_dir_path
            file_name_with_ext=direct_cat_text_csv_f_name)

        print("Getting category-text dicts list from loaded-copied csv file:")
        with open(file=loaded_direct_cat_text_fpath,
                  mode="r", encoding="utf-8") as direct_cat_text_csv_f:
            direct_cat_text = CsvDirectCategoryText(direct_cat_text_csv_f)
            loaded_direct_cat_text_list = direct_cat_text.get_direct_categories_texts_list()
        # print(f"loaded_direct_cat_text_list: {loaded_direct_cat_text_list}")  # Too long
        print(f"type(loaded_direct_cat_text_list): {type(loaded_direct_cat_text_list)}")
        print(f"len(loaded_direct_cat_text_list): {len(loaded_direct_cat_text_list)}")

        print("Postgres DB Saving loaded model and dataset data:")
        pgs_conn = PgsAsyncConnection()
        async with PgsAsyncSession(async_engine=pgs_conn.engine,
                                   log_good_ops=log_pgs_good_ops
                                   ) as pgs_session:
            creation_reason = (f"model loaded from: {model_load_path}, "
                               f"saved to: {model_save_rand_path}, "
                               f"dataset loaded from: {loaded_model_dataset_subdir}, "
                               f"saved to: {dataset_save_new_dir_path}")

            customer_id = await find_create_customer_qry(
                ongoing_session=pgs_session,
                account_username=account_data.account_username,
                account_id=account_data.account_id)

            dataset_id = await find_create_dataset_qry(
                ongoing_session=pgs_session,
                dataset_name=dataset_save_new_name,
                customer_id=customer_id,
                dataset_csv_dir=dataset_save_new_dir_path,
                creation_reason=creation_reason)

            await deactivate_all_model_records_qry(
                ongoing_session=pgs_session,
                ModelClassORM=DirectPredictModel)

            await save_direct_cat_text_dicts_list_qry(
                ongoing_session=pgs_session,
                direct_cat_text_dicts_list=loaded_direct_cat_text_list,
                creation_reason=creation_reason,
                save_only_unique=True)
            print(f"Postgres DB direct categories-texts saved [OK]")
            print(f"loaded_direct_cat_text_list: {loaded_direct_cat_text_list[:2]}")  # Too long

            trained_model_upd_data = {
                "dataset_id": dataset_id,
                "dataset_name": dataset_save_new_name,
                "model_directory": model_save_rand_path,
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
            f"pretrained model init: {BERT_OPTIONS.BERT_MODEL_INIT}\n"
            f"pretrained model name: {BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED}\n"
            f"pretrained model download dir: {BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH}\n"
            f"trained model common load dir: {BERT_OPTIONS.BERT_TRAINED_MODELS_BASE_PATH}\n"
            f"trained model loaded dir path: {blue_color}{model_load_path}{reset_color}\n"
            f"dataset loading and copying time: {dataset_load_copy_time}\n"
            f"trained model loading time: {model_load_time}\n"
            f"trained model saving time: {model_save_time}\n"
            f"extra data saving time: {extra_data_save_time}\n")
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
