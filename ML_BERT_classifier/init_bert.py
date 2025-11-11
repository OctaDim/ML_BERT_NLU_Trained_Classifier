import os
from typing import Dict, Optional

from ML_BERT_classifier.class_bert import ClassifierBERT
from configs.console_colors import CONSOLE_COLORS
from configs.settings import (
    BERT_OPTIONS, BERT_TRAIN_OPTIONS, ALCHEMY_OPTIONS)
from db_postgres.postgres_conn_async.pgs_async_connection import (
    PgsAsyncConnection)
from db_postgres.postgres_conn_async.postgres_async_session import (
    PgsAsyncSession)
from db_postgres.postgres_models.trained_bert_model import (
    TrainedBertModel)
from db_postgres.postgres_queries.qry_find_cache_label_categ_dict import (
    cache_unique_lab_cat_dict_qry)
from db_postgres.postgres_queries.qry_find_create_dataset import (
    find_create_dataset_qry)
from db_postgres.postgres_queries.qry_save_direct_categ_text_dicts_list import (
    save_direct_cat_text_dicts_list_qry)
from db_postgres.postgres_queries.qry_save_label_text_dicts_list import (
    save_label_text_dicts_list_qry)
from db_postgres.postgres_queries.qry_save_new_model_data import (
    save_new_model_data_qry)
from db_postgres.postgres_queries_helpers.hpr_get_bert_model_data import (
    get_postgres_bert_model_data_hpr)
from utils_common.exec_time_decorator import execution_time_decorator
from utils_common.normalized_path import get_full_file_normal_path
from utils_specific.class_csv_direct_categories_texts import (
    CsvDirectCategoryText)
from utils_specific.class_csv_labels_categories import CsvLabelCategory
from utils_specific.class_csv_texts_labels import CsvTextLabel
from utils_specific.get_initial_dataset_dir_path import (
    get_initial_dataset_dir_path)
from utils_specific.get_initial_model_dir_path import (
    get_initial_model_dir_path)
from utils_specific.get_last_saved_dataset_path import (
    get_last_saved_dataset_dir_path)
from utils_specific.get_last_saved_model_dir import (
    get_last_saved_model_dir_path)
from utils_specific.validate_bert_model_directory import (
    validate_bert_model_directory)

print("🚀 LET'S START !!! 🚀")
bert_model_inst: Optional[ClassifierBERT]  # Global. Lazy init in func. Get via func. Just annotation


def get_global_bert_model_inst():
    """Very important function to get global variable. If not used
    the value may be None depending on import order"""
    global bert_model_inst
    return bert_model_inst


class HardSingletonBERT(ClassifierBERT):
    singleton_instance = None
    instance_initialized = False
    """More complex and complete singleton with inheritance, but very
    obvious and controlled. New instance cannot be created via
    __init__() method"""

    def __new__(cls, *args, **kwargs):
        if not cls.singleton_instance:
            print("HardSingletonBERT.__new__()")
            cls.singleton_instance = super().__new__(cls)
        return cls.singleton_instance

    def __init__(self, labels, model_name, max_len, cache_dir):
        if not self.__class__.instance_initialized:
            print("HardSingletonBERT.__init__()")
            super().__init__(labels=labels,
                             model_name=model_name,
                             max_len=max_len,
                             cache_dir=cache_dir)
            self.__class__.instance_initialized = True


class SimpleSingletonBERT:
    singleton_instance = None
    """Easier singleton without inheritance, but not obvious and
    controlled, new instance can be created via __init__() anyway"""

    def __new__(cls, labels, model_name, max_len, cache_dir):
        print("SimpleSingletonBERT.__init__()")
        if not cls.singleton_instance:
            cls.singleton_instance = ClassifierBERT(labels=labels,
                                                    model_name=model_name,
                                                    max_len=max_len,
                                                    cache_dir=cache_dir)
        return cls.singleton_instance


@execution_time_decorator(in_seconds=True,
                          exec_time_logging=True,
                          new_line_after=True,
                          note="BERT Model initialization time")
def initialise_bert_model(labels_categories_dict: Dict[int, str],
                          model_name: str,
                          model_cache_dir: str,
                          token_str_max_len: int,
                          use_singleton=True,
                          use_hard_singleton=True) -> ClassifierBERT:
    green_color = CONSOLE_COLORS.BRIGHT_GREEN
    reset_color = CONSOLE_COLORS.RESET
    print(f"Model Name: {green_color}{model_name}{reset_color}\n"
          f"Model Cached Dir: {green_color}{model_cache_dir}{reset_color}")

    bert_init_data = {"labels": labels_categories_dict,
                      "model_name": model_name,
                      "cache_dir": model_cache_dir,
                      "max_len": token_str_max_len}
    if use_singleton:
        if use_hard_singleton:
            model = HardSingletonBERT(**bert_init_data)
        else:
            model = SimpleSingletonBERT(**bert_init_data)
    else:
        model = ClassifierBERT(**bert_init_data)
    return model


async def init_and_start_bert_model():
    global bert_model_inst  # Global BERT model instance, init from main.py
    log_pgs_good_ops = ALCHEMY_OPTIONS.ALCHEMY_SESSION_OK_ACTIONS_LOGS

    if not BERT_OPTIONS.BERT_MODEL_INIT:
        return

    blue_color = CONSOLE_COLORS.BRIGHT_BLUE
    reset_color = CONSOLE_COLORS.RESET

    if ALCHEMY_OPTIONS.USE_POSTGRES_DATABASE:
        pgs_bert_model_data = await get_postgres_bert_model_data_hpr()
        pgs_all_data_flag = pgs_bert_model_data["all_data_flag"]
    else:
        pgs_bert_model_data = None
        pgs_all_data_flag = False

    last_saved_dataset_dir_path = None
    if not pgs_all_data_flag:  # Not all data in Postgres DB
        print("Getting last dataset directory path:")
        last_saved_dataset_dir_path = get_last_saved_dataset_dir_path()
        initial_dataset_dir_path = None
        if last_saved_dataset_dir_path:
            start_init_dataset_dir = last_saved_dataset_dir_path
        else:
            initial_dataset_dir_path = get_initial_dataset_dir_path()
            if initial_dataset_dir_path:
                start_init_dataset_dir = initial_dataset_dir_path
            else:
                start_init_dataset_dir = None
        start_init_dataset_dirs = start_init_dataset_dir.split(os.sep)
        start_init_dataset_name = start_init_dataset_dirs[-1]
        print(f"start_init_dataset_dir: {start_init_dataset_dir}")
        print(f"start_init_dataset_name: {start_init_dataset_name}")

        if start_init_dataset_dir:
            print("Getting csv label-category train file path:")
            last_saved_lab_cat_csv_path = get_full_file_normal_path(
                all_dir_str_parts=[start_init_dataset_dir],
                file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)
            print(f"last_saved_lab_cat_csv_path: {last_saved_lab_cat_csv_path}")

            print("Getting csv label-category file data:")
            with open(file=last_saved_lab_cat_csv_path,
                      mode="r", encoding="utf-8") as lab_cat_csv_file:
                csf_text_lab = CsvLabelCategory(lab_cat_csv_file)
                saved_lab_cat_dict = csf_text_lab.get_label_category_dict()
                print(f"saved_lab_cat_dict [{len(saved_lab_cat_dict)}]: "
                      f"{saved_lab_cat_dict}")
            if saved_lab_cat_dict:
                label_category_dict = saved_lab_cat_dict
                print(f"label_category_dict: {label_category_dict}")
            else:
                label_category_dict = {0: "api initial category"}
                print(f"Empty or wrong label-category csv data [ERROR]:\n"
                      f"last_saved_dataset_dir_path: {last_saved_dataset_dir_path}\n"
                      f"start_init_dataset_dir: {start_init_dataset_dir}\n"
                      f"saved_lab_cat_dict: {saved_lab_cat_dict}\n")
        else:
            label_category_dict = {0: "api initial category"}
            print(f"BERT Last saved or initial dataset dir, files not found [ERROR]:\n"
                  f"last_saved_dataset_dir_path: {last_saved_dataset_dir_path}\n"
                  f"initial_dataset_dir_path: {initial_dataset_dir_path}\n"
                  f"start_init_dataset_dir: {start_init_dataset_dir}\n")

        print("Getting csv label-text train file path:")
        lab_txt_file_name = BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME
        csv_lab_txt_file_path = get_full_file_normal_path(
            all_dir_str_parts=[start_init_dataset_dir],
            file_name_with_ext=lab_txt_file_name)

        print("Getting csv text-label dict and label-text list file data:")
        with open(file=csv_lab_txt_file_path,
                  mode="r", encoding="utf-8") as csv_lab_txt_file:
            csf_lab_txt = CsvTextLabel(csv_file_obj=csv_lab_txt_file)
            # text_label_dict = csf_lab_txt.get_text_label_dict()
            # # print(f"text_label_dict: {text_label_dict}")  # Too long
            # print(f"len(text_label_dict): {len(text_label_dict)}")

            lab_text_dicts_list = csf_lab_txt.get_label_text_dicts_list()
            # print(f"lab_text_dicts_list: {lab_text_dicts_list}")  # Too long
            print(f"len(lab_text_dicts_list): {len(lab_text_dicts_list)}")

        print("Getting csv category-test train file path:")
        last_saved_direct_cat_text_csv_path = get_full_file_normal_path(
            all_dir_str_parts=[start_init_dataset_dir],
            file_name_with_ext=BERT_OPTIONS.BERT_DIRECT_CATEGORY_TEXT_CSV_FILE_NAME)
        print(f"last_saved_cat_text_csv_path: "
              f"{last_saved_direct_cat_text_csv_path}")

        print("Getting csv category-text dicts list file data:")
        with open(file=last_saved_direct_cat_text_csv_path,
                  mode="r", encoding="utf-8") as csv_direct_cat_txt_f:
            csf_direct_cat_txt = CsvDirectCategoryText(csv_file_obj=csv_direct_cat_txt_f)
            direct_cat_text_dicts_list = csf_direct_cat_txt.get_direct_categories_texts_list()
            # print(f"direct_cat_text_dicts_list: {direct_cat_text_dicts_list}")  # Too long
            print(f"len(direct_cat_text_dicts_list): {len(direct_cat_text_dicts_list)}")

        print("Getting last model directory path from file:")
        file_saved_model_dir_path = get_last_saved_model_dir_path()
        if file_saved_model_dir_path:
            last_saved_model_dir_path = file_saved_model_dir_path
        else:
            last_saved_model_dir_path = None

        if ALCHEMY_OPTIONS.USE_POSTGRES_DATABASE:
            print("Postgres DB saving lab-cat, lab-text file data:")
            pgs_conn = PgsAsyncConnection()
            async with PgsAsyncSession(engine=pgs_conn.engine,
                                       log_good_ops=log_pgs_good_ops
                                       ) as pgs_session:
                creation_reason = (f"service restarted, csv file: "
                                   f"{start_init_dataset_name}")

                dataset_id = await find_create_dataset_qry(
                    ongoing_session=pgs_session,
                    dataset_name=start_init_dataset_name,
                    dataset_csv_dir=start_init_dataset_dir,
                    creation_reason=creation_reason)

                await cache_unique_lab_cat_dict_qry(
                    ongoing_session=pgs_session,
                    dataset_id=dataset_id,
                    label_category_dict=label_category_dict,
                    creation_reason=creation_reason,
                    save_only_unique=True)
                print(f"Postgres DB labels categories saved [OK]:\n"
                      f"label_category_dict: {label_category_dict}\n")

                await save_label_text_dicts_list_qry(
                    ongoing_session=pgs_session,
                    label_text_dicts_list=lab_text_dicts_list,
                    creation_reason=creation_reason,
                    save_only_unique=True)

                await save_direct_cat_text_dicts_list_qry(
                    ongoing_session=pgs_session,
                    direct_cat_text_dicts_list=direct_cat_text_dicts_list,
                    creation_reason=creation_reason,
                    save_only_unique=True)
    else:  # All Postgres DB data exists
        label_category_dict = pgs_bert_model_data["lab_cat_dict"]
        # text_label_dict = pgs_bert_model_data["text_lab_dict"]
        lab_text_dicts_list = pgs_bert_model_data["lab_text_dicts_list"]
        direct_cat_text_dicts_list = pgs_bert_model_data["direct_cat_text_dicts_list"]
        start_init_dataset_name = pgs_bert_model_data["dataset_name"]
        start_init_dataset_dir = pgs_bert_model_data["dataset_dir"]
        last_saved_model_dir_path = pgs_bert_model_data["model_dir_path"]

        if ALCHEMY_OPTIONS.USE_POSTGRES_DATABASE:
            pgs_conn = PgsAsyncConnection()
            async with PgsAsyncSession(engine=pgs_conn.engine,
                                       log_good_ops=log_pgs_good_ops
                                       ) as pgs_session:
                creation_reason = (f"service restarted, pgs data: "
                                   f"{start_init_dataset_name}")

                dataset_id = await find_create_dataset_qry(
                    ongoing_session=pgs_session,
                    dataset_name=start_init_dataset_name,
                    dataset_csv_dir=start_init_dataset_dir,
                    creation_reason=creation_reason)

                await cache_unique_lab_cat_dict_qry(
                    ongoing_session=pgs_session,
                    dataset_id=dataset_id,
                    label_category_dict=label_category_dict,
                    creation_reason=creation_reason,
                    save_only_unique=True)
                print(f"Postgres DB labels-categories saved [OK]:\n"
                      f"label_category_dict: {label_category_dict}\n")

                await save_label_text_dicts_list_qry(
                    ongoing_session=pgs_session,
                    label_text_dicts_list=lab_text_dicts_list,
                    creation_reason=creation_reason,
                    save_only_unique=True)

                await save_direct_cat_text_dicts_list_qry(
                    ongoing_session=pgs_session,
                    direct_cat_text_dicts_list=direct_cat_text_dicts_list,
                    creation_reason=creation_reason,
                    save_only_unique=True)
    print("Getting initial model directory path:")
    initial_model_dir_path = get_initial_model_dir_path()

    print(f">>>>>>> initial_model_dir_path => {initial_model_dir_path}")
    print(f">>>>>>> last_saved_model_dir_path => {last_saved_model_dir_path}")
    print(f">>>>>>> last_saved_dataset_dir_path => {last_saved_dataset_dir_path}")
    print(f">>>>>>> label_category_dict => {label_category_dict}")

    if initial_model_dir_path:
        bert_model_inst = initialise_bert_model(
            labels_categories_dict=label_category_dict,
            model_name=BERT_OPTIONS.BERT_ACTIVE_MODEL_NAME,
            model_cache_dir=initial_model_dir_path,
            token_str_max_len=BERT_TRAIN_OPTIONS.BERT_TOKEN_STR_MAX_LENGTH,
            use_singleton=True,
            use_hard_singleton=True)
        bert_model_inst.last_saved_dataset_dir = last_saved_dataset_dir_path
        bert_model_inst.last_saved_dataset_dir = start_init_dataset_dir
        print(f"Pretrained Init BERT Model initialised [OK]:\n"
              f"initial_model_dir_path: "
              f"{blue_color}{initial_model_dir_path}{reset_color}\n"
              f"last_saved_model_dir_path: {last_saved_model_dir_path}\n")

        if ALCHEMY_OPTIONS.USE_POSTGRES_DATABASE:
            pgs_conn = PgsAsyncConnection()
            async with PgsAsyncSession(engine=pgs_conn.engine,
                                       log_good_ops=log_pgs_good_ops
                                       ) as pgs_session:
                creation_reason = (f"service restart init: "
                                   f"{start_init_dataset_name}")

                dataset_id = await find_create_dataset_qry(
                    ongoing_session=pgs_session,
                    dataset_name=start_init_dataset_name,
                    dataset_csv_dir=start_init_dataset_dir,
                    creation_reason=creation_reason)

                new_trained_model_data = {
                    "dataset_id": dataset_id,
                    "dataset_name": start_init_dataset_name,
                    "model_directory": initial_model_dir_path,
                    "creation_reason": creation_reason}
                await save_new_model_data_qry(
                    ModelClassORM=TrainedBertModel,
                    ongoing_session=pgs_session,
                    new_data=new_trained_model_data)

    model_dir_exists_flag = validate_bert_model_directory(
        model_directory_path=last_saved_model_dir_path)

    if last_saved_model_dir_path and model_dir_exists_flag:
        model_load_error_log = bert_model_inst.load_model(
            model_load_dir_path=last_saved_model_dir_path)
        bert_model_inst.last_saved_dataset_dir = last_saved_dataset_dir_path
        bert_model_inst.last_saved_dataset_dir = start_init_dataset_dir
        print(f"Last Saved BERT Model initialised preliminary and loaded [OK]:\n"
              f"last_saved_model_dir_path: "
              f"{blue_color}{last_saved_model_dir_path}{reset_color}\n"
              f"initial_model_dir_path: {initial_model_dir_path}\n")

        if not model_load_error_log:
            if ALCHEMY_OPTIONS.USE_POSTGRES_DATABASE:
                pgs_conn = PgsAsyncConnection()
                async with PgsAsyncSession(engine=pgs_conn.engine,
                                           log_good_ops=log_pgs_good_ops
                                           ) as pgs_session:
                    if not pgs_all_data_flag:
                        creation_reason = (f"loaded after restart, csv file: "
                                           f"{start_init_dataset_name}")
                    else:
                        creation_reason = (f"loaded after restart, pgs data: "
                                           f"{start_init_dataset_name}")

                    dataset_id = await find_create_dataset_qry(
                        ongoing_session=pgs_session,
                        dataset_name=start_init_dataset_name,
                        dataset_csv_dir=start_init_dataset_dir,
                        creation_reason=creation_reason)

                    new_trained_model_data = {
                        "dataset_id": dataset_id,
                        "dataset_name": start_init_dataset_name,
                        "model_directory": last_saved_model_dir_path,
                        "creation_reason": creation_reason}
                    await save_new_model_data_qry(
                        ModelClassORM=TrainedBertModel,
                        ongoing_session=pgs_session,
                        new_data=new_trained_model_data)

            print(f"Last Saved BERT Model initialised and loaded [OK]:\n"
                  f"last_saved_model_dir_path: "
                  f"{blue_color}{last_saved_model_dir_path}{reset_color}\n"
                  f"initial_model_dir_path: {initial_model_dir_path}\n")
        else:
            print(f"Last Saved BERT Model load [ERROR]: "
                  f"error: {model_load_error_log}\n"
                  f"last_saved_model_dir_path: {last_saved_model_dir_path}\n"
                  f"initial_model_dir_path: {initial_model_dir_path}\n")

    if not initial_model_dir_path and not last_saved_model_dir_path:
        print(f"BERT Model initialise [ERROR]:\n"
              f"last_saved_model_dir_path: {last_saved_model_dir_path}\n"
              f"initial_model_dir_path: {initial_model_dir_path}\n")

    print("🚀 LET'S GO !!! 🚀")
    print(f">>>>>>> bert_model_inst => {bert_model_inst}")
    print(f">>>>>>> hash(bert_model_inst) => {hash(bert_model_inst)}")
    print(f">>>>>>> bert_model_inst.labels => {bert_model_inst.labels}\n")
    return bert_model_inst
