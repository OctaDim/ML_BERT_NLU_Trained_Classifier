import os
from typing import Dict

from ML_BERT_classifier.class_bert import ClassifierBERT
from configs.console_colors import CONSOLE_COLORS
from configs.settings import (
    BERT_OPTIONS, BERT_TRAIN_OPTIONS, ALCHEMY_OPTIONS)
from db_postgres.postgres_async_conn.pgs_async_connection import (
    PostgresConnection)
from db_postgres.postgres_async_conn.postgres_async_session import (
    PostgresSession)
from db_postgres.postgres_init.db_tables_initialization import (
    initialize_db_tables)
from db_postgres.postgres_models.trained_bert_model import (
    TrainedBertModel)
from db_postgres.postgres_queries.qry_find_create_dataset import (
    find_create_dataset_qry)
from db_postgres.postgres_queries.qry_get_label_category_data import (
    get_label_category_data_qry)
from db_postgres.postgres_queries.qry_get_last_saved_model_dir import (
    get_last_saved_model_dir_qry)
from db_postgres.postgres_queries.qry_save_label_category_dict import (
    cache_label_category_dict_qry)
from db_postgres.postgres_queries.qry_save_label_text_dict import (
    save_label_text_dict_qry)
from db_postgres.postgres_queries.qry_save_new_model_data import (
    save_new_model_data_qry)
from utils_common.exec_time_decorator import execution_time_decorator
from utils_common.normalized_path import get_full_file_normal_path
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

print("🚀 LET'S GO !!! 🚀")
bert_model_inst = None
print("bert_model_inst => ", bert_model_inst)


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

    if BERT_OPTIONS.BERT_MODEL_INIT:
        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        reset_color = CONSOLE_COLORS.RESET

        if ALCHEMY_OPTIONS.USE_POSTGRES_DB:
            print("\nDB Postgres Getting labels categories data:")
            pgs_lab_cat_data = await get_label_category_data_qry()
            print(f"pgs_lab_cat_data [{len(pgs_lab_cat_data)}]: {pgs_lab_cat_data}")
        else:
            pgs_lab_cat_data = None

        last_saved_dataset_dir_path = None
        start_init_dataset_name = None
        if not pgs_lab_cat_data:  # No labels-categories data in Postgres DB
            print("\nGetting last dataset directory path:")
            last_saved_dataset_dir_path = get_last_saved_dataset_dir_path()
            initial_dataset_dir_path = None
            if last_saved_dataset_dir_path:
                bert_start_init_dataset_dir = last_saved_dataset_dir_path
            else:
                initial_dataset_dir_path = get_initial_dataset_dir_path()
                if initial_dataset_dir_path:
                    bert_start_init_dataset_dir = initial_dataset_dir_path
                else:
                    bert_start_init_dataset_dir = None
            start_init_dataset_dirs = bert_start_init_dataset_dir.split(os.sep)
            start_init_dataset_name = start_init_dataset_dirs[-1]
            print(f"bert_start_init_dataset_dir: {bert_start_init_dataset_dir}")
            print(f"start_init_dataset_name: {start_init_dataset_name}")

            print("\nGetting csv label-category train file path:")
            if bert_start_init_dataset_dir:
                last_saved_lab_cat_csv_path = get_full_file_normal_path(
                    all_dir_str_parts=[bert_start_init_dataset_dir],
                    file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)
                print(f"last_saved_lab_cat_csv_path: {last_saved_lab_cat_csv_path}")

                print("\nGetting csv label-category file data:")
                with open(file=last_saved_lab_cat_csv_path,
                          mode="r", encoding="utf-8") as lab_cat_csv_file:
                    csf_text_lab = CsvLabelCategory(lab_cat_csv_file)
                    saved_lab_cat_dict = csf_text_lab.get_label_category_dict()
                    print(f"saved_lab_cat_dict [{len(saved_lab_cat_dict)}]: "
                          f"{saved_lab_cat_dict}")
                if saved_lab_cat_dict:
                    labels_categories = saved_lab_cat_dict
                    print(f"labels_categories: {labels_categories}")
                else:
                    labels_categories = {0: "api initial category"}
                    print(f"Empty or wrong label-category csv data [ERROR]:\n"
                          f"last_saved_dataset_dir_path: {last_saved_dataset_dir_path}\n"
                          f"bert_start_init_dataset_dir: {bert_start_init_dataset_dir}\n"
                          f"saved_lab_cat_dict: {saved_lab_cat_dict}\n")
            else:
                labels_categories = {0: "api initial category"}
                print(f"BERT Last saved or initial dataset dir, files not found [ERROR]:\n"
                      f"last_saved_dataset_dir_path: {last_saved_dataset_dir_path}\n"
                      f"initial_dataset_dir_path: {initial_dataset_dir_path}\n"
                      f"bert_start_init_dataset_dir: {bert_start_init_dataset_dir}\n")

            print("\nGetting csv label-text train file path:")
            lab_txt_file_name = BERT_OPTIONS.BERT_TEXT_LABEL_CSV_FILE_NAME
            csv_lab_txt_file_path = get_full_file_normal_path(
                all_dir_str_parts=[bert_start_init_dataset_dir],
                file_name_with_ext=lab_txt_file_name)

            print("\nGetting csv label-text file data:")
            with open(file=csv_lab_txt_file_path,
                      mode="r", encoding="utf-8") as csv_lab_txt_file:
                csf_lab_txt = CsvTextLabel(csv_file_obj=csv_lab_txt_file)
                dataset_lab_text_dict = csf_lab_txt.get_text_label_dict()
            # print(f"dataset_lab_text_dict => {dataset_lab_text_dict}")  # Too long
            print(f"len(dataset_lab_text_dict) => {len(dataset_lab_text_dict)}")

            if ALCHEMY_OPTIONS.USE_POSTGRES_DB:
                print("\nPostgres DB saving label-category, label-text file data:")
                pgs_conn = PostgresConnection()
                async with PostgresSession(
                        async_engine=pgs_conn.engine) as pgs_session:
                    dataset_id = await find_create_dataset_qry(
                        ongoing_session=pgs_session,
                        dataset_name=start_init_dataset_name)

                    await cache_label_category_dict_qry(
                        ongoing_session=pgs_session,
                        dataset_id=dataset_id,
                        label_category_dict=labels_categories)
                    print(f"Postgres DB labels categories saved [OK]:\n"
                          f"labels_categories: {labels_categories}\n")

                    await save_label_text_dict_qry(
                        ongoing_session=pgs_session,
                        label_text_dict=dataset_lab_text_dict)
        else:  # Labels-categories data exists in Postgres DB
            labels_categories = pgs_lab_cat_data

        if ALCHEMY_OPTIONS.USE_POSTGRES_DB:
            print("\nDB Postgres getting last model directory path:")
            pgs_saved_model_dir_path = await get_last_saved_model_dir_qry()
        else:
            pgs_saved_model_dir_path = None

        if pgs_saved_model_dir_path:  # DB last saved model dir exists
            last_saved_model_dir_path = pgs_saved_model_dir_path
        else:  # No last saved model dir in DB or not found
            print("\nGetting last model directory path from file:")
            file_saved_model_dir_path = get_last_saved_model_dir_path()
            last_saved_model_dir_path = file_saved_model_dir_path

        print("\nGetting initial model directory path:")
        initial_model_dir_path = get_initial_model_dir_path()

        print(f">>>>>>> last_saved_model_dir_path => {last_saved_model_dir_path}")
        print(f">>>>>>> initial_model_dir_path => {initial_model_dir_path}")
        print(f">>>>>>> last_saved_dataset_dir_path => {last_saved_dataset_dir_path}")
        print(f">>>>>>> labels_categories => {labels_categories}")

        if last_saved_model_dir_path and initial_model_dir_path:
            bert_model_inst = initialise_bert_model(
                labels_categories_dict=labels_categories,
                model_name=BERT_OPTIONS.BERT_ACTIVE_MODEL_NAME,
                model_cache_dir=initial_model_dir_path,
                token_str_max_len=BERT_TRAIN_OPTIONS.BERT_TOKEN_STR_MAX_LENGTH,
                use_singleton=True,
                use_hard_singleton=True)

            if ALCHEMY_OPTIONS.USE_POSTGRES_DB:
                pgs_conn = PostgresConnection()
                async with PostgresSession(
                        async_engine=pgs_conn.engine) as pgs_session:
                    dataset_id = await find_create_dataset_qry(
                        ongoing_session=pgs_session,
                        dataset_name=start_init_dataset_name)

                    new_trained_model_data = {
                        "dataset_id": dataset_id,
                        "model_directory": initial_model_dir_path,
                        "creation_reason": "model initialized"}
                    await save_new_model_data_qry(
                        ModelClassORM=TrainedBertModel,
                        ongoing_session=pgs_session,
                        new_data=new_trained_model_data)

            load_error_log = bert_model_inst.load_model(
                dir_full_path=last_saved_model_dir_path)

            if not load_error_log:
                if ALCHEMY_OPTIONS.USE_POSTGRES_DB:
                    pgs_conn = PostgresConnection()
                    async with PostgresSession(
                            async_engine=pgs_conn.engine) as pgs_session:
                        dataset_id = await find_create_dataset_qry(
                            ongoing_session=pgs_session,
                            dataset_name=start_init_dataset_name)

                        new_trained_model_data = {
                            "dataset_id": dataset_id,
                            "model_directory": initial_model_dir_path,
                            "creation_reason": "model weights loaded"}
                        await save_new_model_data_qry(
                            ModelClassORM=TrainedBertModel,
                            ongoing_session=pgs_session,
                            new_data=new_trained_model_data)

                print(f"Last Saved BERT Model initialised and loaded [OK]:\n"
                      f"last_saved_model_dir_path: "
                      f"{blue_color}{last_saved_model_dir_path}{reset_color}\n"
                      f"initial_model_dir_path: {initial_model_dir_path}\n")
            else:
                print(f"Last Saved BERT Model load [ERROR]: error: {load_error_log}\n"
                      f"last_saved_model_dir_path: {last_saved_model_dir_path}\n"
                      f"initial_model_dir_path: {initial_model_dir_path}\n")
        elif initial_model_dir_path:
            bert_model_inst = initialise_bert_model(
                labels_categories_dict=labels_categories,
                model_name=BERT_OPTIONS.BERT_ACTIVE_MODEL_NAME,
                model_cache_dir=initial_model_dir_path,
                token_str_max_len=BERT_TRAIN_OPTIONS.BERT_TOKEN_STR_MAX_LENGTH,
                use_singleton=True,
                use_hard_singleton=True)

            if ALCHEMY_OPTIONS.USE_POSTGRES_DB:
                pgs_conn = PostgresConnection()
                with PostgresSession(async_engine=pgs_conn.engine) as pgs_sess:
                    dataset_id = await find_create_dataset_qry(
                        ongoing_session=pgs_session,
                        dataset_name=start_init_dataset_name)

                    new_trained_model_data = {
                        "dataset_id": dataset_id,
                        "model_directory": initial_model_dir_path,
                        "creation_reason": "model initialized"}
                    await save_new_model_data_qry(
                        ModelClassORM=TrainedBertModel,
                        ongoing_session=pgs_sess,
                        new_data=new_trained_model_data)

            print(f"Pretrained Init BERT Model initialised [OK]:\n"
                  f"initial_model_dir_path: "
                  f"{blue_color}{initial_model_dir_path}{reset_color}\n"
                  f"last_saved_model_dir_path: {last_saved_model_dir_path}\n")
        else:
            print(f"BERT Model initialise [ERROR]:\n"
                  f"last_saved_model_dir_path: {last_saved_model_dir_path}\n"
                  f"initial_model_dir_path: {initial_model_dir_path}\n")

        print(f">>>>>>> bert_model_inst => {bert_model_inst}")
        print(f">>>>>>> hash(bert_model_inst) => {hash(bert_model_inst)}")
        print(f">>>>>>> bert_model_inst.labels => {bert_model_inst.labels}")
        return bert_model_inst


if __name__ == "__main__":
    async def main_loop_func():
        await initialize_db_tables()
        await init_and_start_bert_model()


    import asyncio

    asyncio.run(main=main_loop_func(), debug=True)
    print(f"bert_model_inst: {bert_model_inst}")
