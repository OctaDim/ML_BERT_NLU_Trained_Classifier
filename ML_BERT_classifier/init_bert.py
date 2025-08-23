# from ML_BERT_train_datasets.test_init_train_datasets.test_labels_categories import labels_categories
from typing import Dict

from ML_BERT_classifier.class_bert import ClassifierBERT
from configs.console_colors import CONSOLE_COLORS
from configs.settings import BERT_OPTIONS, BERT_TRAIN_OPTIONS
from utils_common.exec_time_decorator import execution_time_decorator
from utils_common.normalized_path import get_full_file_normal_path
from utils_specific.class_csv_labels_categories import CsvLabelCategory
from utils_specific.get_initial_dataset_dir_path import get_initial_dataset_dir_path
from utils_specific.get_initial_model_dir_path import get_initial_model_dir_path
from utils_specific.get_last_saved_dataset_path import get_last_saved_dataset_dir_path
from utils_specific.get_last_saved_model_dir import get_last_saved_model_dir_path


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


if BERT_OPTIONS.BERT_MODEL_INIT:
    blue_color = CONSOLE_COLORS.BRIGHT_BLUE
    yellow_color = CONSOLE_COLORS.BRIGHT_YELLOW
    reset_color = CONSOLE_COLORS.RESET

    print("\nGetting last dataset directory path:")
    last_saved_dataset_dir_path = get_last_saved_dataset_dir_path()
    initial_dataset_dir_path = None
    if last_saved_dataset_dir_path:
        bert_init_dataset_dir = last_saved_dataset_dir_path
    else:
        initial_dataset_dir_path = get_initial_dataset_dir_path()
        if initial_dataset_dir_path:
            bert_init_dataset_dir = initial_dataset_dir_path
        else:
            bert_init_dataset_dir = ""

    print("\nGetting csv label-category train file path:")
    if bert_init_dataset_dir:
        last_saved_lab_cat_csv_path = get_full_file_normal_path(
            all_dir_str_parts=[bert_init_dataset_dir],
            file_name_with_ext=BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_FILE_NAME)
        print(f"last_saved_lab_cat_csv_path: {last_saved_lab_cat_csv_path}")

        print("\nGetting csv label-category file data:")
        with open(file=last_saved_lab_cat_csv_path,
                  mode="r", encoding="utf-8") as lab_cat_csv_file:
            csf_text_lab = CsvLabelCategory(lab_cat_csv_file)
            new_lab_cat_dict = csf_text_lab.get_label_category_dict()
            print(f"new_lab_cat_dict [{len(new_lab_cat_dict)}]: "
                  f"{new_lab_cat_dict}")

        if new_lab_cat_dict:
            labels_categories = new_lab_cat_dict
        else:
            labels_categories = {0: "api initial category"}
            print(f"Empty or wrong label-category csv data [ERROR]:\n"
                  f"last_saved_dataset_dir: {bert_init_dataset_dir}\n"
                  f"last_saved_lab_cat_csv_path: {last_saved_lab_cat_csv_path}\n"
                  f"new_lab_cat_dict: {new_lab_cat_dict}\n")
    else:
        labels_categories = {0: "api initial category"}
        print(f"BERT Last saved or initial dataset dir, files not found [ERROR]:\n"
            f"last_saved_dataset_dir_path: {last_saved_dataset_dir_path}\n"
            f"initial_dataset_dir_path: {initial_dataset_dir_path}\n"
            f"initial_dataset_dir_path: {initial_dataset_dir_path}\n")

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
