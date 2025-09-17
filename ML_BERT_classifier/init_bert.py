from typing import Dict

from sqlalchemy import MetaData

from ML_BERT_classifier.class_bert import ClassifierBERT
from configs.console_colors import CONSOLE_COLORS
from configs.settings import BERT_OPTIONS, BERT_TRAIN_OPTIONS
from db_postgres.postgres_async_conn.db_tables_manager import DBTablesManager
from db_postgres.postgres_async_conn.pgs_async_connection import (
    PostgresConnection, Base)
from db_postgres.postgres_init.db_tables_initialization import (
    initialize_db_tables)
from db_postgres.postgres_models.label_category_model import (
    LabelCategoryModel)
from db_postgres.postgres_queries.save_label_category_dict import (
    save_pgs_label_category_data)
from db_postgres.postgres_utils.convert_orm_rows_to_dict import (
    convert_orm_rows_to_dicts, convert_model_recs_to_dicts)
from db_postgres.postgres_utils.get_model_records_flex_query import (
    get_model_rows_flex_query)
from utils_common.exec_time_decorator import execution_time_decorator
from utils_common.normalized_path import get_full_file_normal_path
from utils_specific.class_csv_labels_categories import CsvLabelCategory
from utils_specific.get_initial_dataset_dir_path import (
    get_initial_dataset_dir_path)
from utils_specific.get_initial_model_dir_path import (
    get_initial_model_dir_path)
from utils_specific.get_last_saved_dataset_path import (
    get_last_saved_dataset_dir_path)
from utils_specific.get_last_saved_model_dir import (
    get_last_saved_model_dir_path)
from db_postgres.postgres_async_conn.postgres_async_session import (
    PostgresSession)

print("000")
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

    # TODO: Use common data with unpacking instead of params for creating model bellow
    # bert_init_data = {"labels": label_category_dict,
    #                   "model_name": model_name,
    #                   "cache_dir": model_cache_dir,
    #                   "max_len": token_str_max_len}

    if use_singleton:
        if use_hard_singleton:
            model = HardSingletonBERT(labels=labels_categories_dict,
                                      model_name=model_name,
                                      cache_dir=model_cache_dir,
                                      max_len=token_str_max_len)
        else:
            model = SimpleSingletonBERT(labels=labels_categories_dict,
                                        model_name=model_name,
                                        cache_dir=model_cache_dir,
                                        max_len=token_str_max_len)
    else:
        model = ClassifierBERT(labels=labels_categories_dict,
                               model_name=model_name,
                               cache_dir=model_cache_dir,
                               max_len=token_str_max_len)
    return model


async def init_and_start_bert_model():
    global bert_model_inst  # Global BERT model instance, init from main.py

    if BERT_OPTIONS.BERT_MODEL_INIT:
        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        reset_color = CONSOLE_COLORS.RESET

        print("\nDB Postgres getting labels categories data:")
        pgs_conn = PostgresConnection()
        print(f">>>>>>> DB HEALTH CHECK: {await pgs_conn.db_health_check()}")

        async with PostgresSession(async_engine=pgs_conn.engine) as pgs_session:
            pgs_lab_cat_recs = await get_model_rows_flex_query(
                orm_model_class=LabelCategoryModel,
                ongoing_session=pgs_session,
                fields_values_filter=None,
                order_by_fields=None,
                return_scalars=True)
            pgs_lab_cat_dicts = await convert_model_recs_to_dicts(
                model_records_list=pgs_lab_cat_recs)
            print(f"####### type(pgs_lab_cat_dicts): {type(pgs_lab_cat_dicts)}")
            print(f"####### len(pgs_lab_cat_dicts): {len(pgs_lab_cat_dicts)}")
            print(f"####### pgs_lab_cat_dicts: {pgs_lab_cat_dicts}")

        pgs_lab_cat_data = {}
        for cur_record_dict in pgs_lab_cat_dicts:
            label_index = cur_record_dict["label_index"]
            category_name = cur_record_dict["category_name"]
            pgs_lab_cat_data[label_index] = category_name
        print(f"####### pgs_lab_cat_data [{len(pgs_lab_cat_data)}] => {pgs_lab_cat_data}")


        last_saved_dataset_dir_path = ""
        if not pgs_lab_cat_data:
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
                    bert_start_init_dataset_dir = ""

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
                    await save_pgs_label_category_data(
                        label_category_dict=saved_lab_cat_dict)
                else:
                    labels_categories = {0: "api initial category"}
                    await save_pgs_label_category_data(
                        label_category_dict=labels_categories)
                    print(f"Empty or wrong label-category csv data [ERROR]:\n"
                          f"last_saved_dataset_dir: {bert_start_init_dataset_dir}\n"
                          f"last_saved_lab_cat_csv_path: {last_saved_lab_cat_csv_path}\n"
                          f"saved_lab_cat_dict: {saved_lab_cat_dict}\n")
            else:
                labels_categories = {0: "api initial category"}
                await save_pgs_label_category_data(
                    label_category_dict=labels_categories)
                print(f"BERT Last saved or initial dataset dir, files not found [ERROR]:\n"
                      f"last_saved_dataset_dir_path: {last_saved_dataset_dir_path}\n"
                      f"initial_dataset_dir_path: {initial_dataset_dir_path}\n"
                      f"initial_dataset_dir_path: {initial_dataset_dir_path}\n")
        else:  # if pgs_lab_cat_data:
            labels_categories = pgs_lab_cat_data

        print("\nGetting last model directory path:")
        last_saved_model_dir_path = get_last_saved_model_dir_path()
        initial_model_dir_path = get_initial_model_dir_path()
        # load_error_log = ""

        print(">>>>>>> last_saved_model_dir_path => ", last_saved_model_dir_path)
        print(">>>>>>> initial_model_dir_path => ", initial_model_dir_path)
        print(">>>>>>> last_saved_model_dir_path => ", last_saved_model_dir_path)
        print(">>>>>>> last_saved_dataset_dir_path => ", last_saved_dataset_dir_path)
        print(">>>>>>> labels_categories => ", labels_categories)

        if last_saved_model_dir_path and initial_model_dir_path:
            bert_model_inst = initialise_bert_model(
                labels_categories_dict=labels_categories,
                model_name=BERT_OPTIONS.BERT_ACTIVE_MODEL_NAME,
                model_cache_dir=get_initial_model_dir_path(),
                token_str_max_len=BERT_TRAIN_OPTIONS.BERT_TOKEN_STR_MAX_LENGTH,
                use_singleton=True,
                use_hard_singleton=True)

            load_error_log = bert_model_inst.load_model(
                dir_full_path=last_saved_model_dir_path)
            if not load_error_log:
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
                model_cache_dir=get_initial_model_dir_path(),
                token_str_max_len=BERT_TRAIN_OPTIONS.BERT_TOKEN_STR_MAX_LENGTH,
                use_singleton=True,
                use_hard_singleton=True)
            print(f"Pretrained Init BERT Model initialised [OK]:\n"
                  f"initial_model_dir_path: "
                  f"{blue_color}{initial_model_dir_path}{reset_color}\n"
                  f"last_saved_model_dir_path: {last_saved_model_dir_path}\n")
        else:
            print(f"BERT Model initialise [ERROR]:\n"
                  f"last_saved_model_dir_path: {last_saved_model_dir_path}\n"
                  f"initial_model_dir_path: {initial_model_dir_path}\n")

        print(">>>>>>> bert_model_inst", bert_model_inst)
        print(">>>>>>> hash(bert_model_inst)", hash(bert_model_inst))
        print(">>>>>>> bert_model_inst.labels", bert_model_inst.labels)

        print("bert_model_inst => ", bert_model_inst)
        return bert_model_inst


# bert_model_inst = init_and_start_bert_model()
# # print(">>>>>>> hash(bert_model_inst)", hash(bert_model_inst))

if __name__ == "__main__":
    async def main_loop_func():
        await initialize_db_tables()
        await init_and_start_bert_model()

    import asyncio
    asyncio.run(main=main_loop_func(), debug=True)
    print(bert_model_inst)
