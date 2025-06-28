from typing import Dict

from ML_BERT_classifier.class_bert import ClassifierBERT
from configs.console_colors import CONSOLE_COLORS
from configs.settings import BASE_DIR, BERT_OPTIONS, BERT_TRAIN_OPTIONS
from ML_BERT_train_datasets.test_init_train_datasets.test_labels_categories import (
    labels_categories)
from utils_common.exec_time_decorator import execution_time_decorator
from utils_common.normalized_path import get_full_dir_normal_path


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
    green_clr = CONSOLE_COLORS.BRIGHT_GREEN
    reset_clr = CONSOLE_COLORS.RESET
    print(f"Model Name: {green_clr}{model_name}{reset_clr}\n"
          f"Model Cached Dir: {green_clr}{model_cache_dir}{reset_clr}")

    # TODO: Use common data with unpacking instead of params for creating model bellow
    # bert_init_data = {"test_train_data": labels_categories_dict,
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
    bert_model_path = get_full_dir_normal_path(
        [BASE_DIR, BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH])

    bert_model_inst = initialise_bert_model(
        labels_categories_dict=labels_categories,
        model_name=BERT_OPTIONS.BERT_ACTIVE_MODEL_NAME,
        model_cache_dir=BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH,
        token_str_max_len=BERT_TRAIN_OPTIONS.BERT_TOKEN_STR_MAX_LENGTH,
        use_singleton=True,
        use_hard_singleton=True)
