import inspect
import json
from datetime import datetime, timedelta
from typing import List, Tuple

from ML_BERT_classifier.class_bert import ClassifierBERT
from configs.console_colors import CONSOLE_COLORS
from configs.settings import (
    REDIS_OPTIONS, BERT_OPTIONS, BERT_MODEL_NAMES, STATUSES,
    ALCHEMY_OPTIONS)
from db_postgres.postgres_conn_async.pgs_async_connection import (
    PgsAsyncConnection)
from db_postgres.postgres_conn_async.postgres_async_session import (
    PgsAsyncSession)
from db_postgres.postgres_queries.qry_get_direct_category_by_text import (
    get_direct_category_by_text)
from db_redis.redis_funcs.func_redis_save_key_mapping import (
    redis_save_key_mapping_dict)
from fast_api.app_account_data.scheme_account_data import (
    AccountDataBert)
from fast_api.app_auth.scheme_auth import AuthDataBert


async def background_checkset_test_model(
        auth_data: AuthDataBert,
        account_data: AccountDataBert,
        checkset_data_list: List[Tuple[str, str]],
        checkset_file_name: str,
        bert_model_inst: ClassifierBERT,
        checkset_redis_name: str
) -> None:
    cur_func_name = inspect.currentframe().f_code.co_name

    print("@" * 65)
    print("BERT background checkset model test start:")
    REDIS_KEY_EXPIRE_TIME = timedelta(days=REDIS_OPTIONS.CHECKSET_TESTS_EXPIRY_DAYS)
    log_pgs_good_ops = ALCHEMY_OPTIONS.ALCHEMY_SESSION_OK_ACTIONS_LOGS

    redis_update = {
        "checkset_status": STATUSES.STATUS_CHECKSET_TEST_PROCESS_EN,
        "step_t3_model_checkset_testing_in_process": "[OK]", }
    redis_error = await redis_save_key_mapping_dict(
        key_name=checkset_redis_name,
        mapping_dict=redis_update,
        expiry_seconds=REDIS_KEY_EXPIRE_TIME)
    if redis_error:
        print(redis_error)

    green_color = CONSOLE_COLORS.BRIGHT_GREEN
    red_color = CONSOLE_COLORS.BRIGHT_RED
    reset_color = CONSOLE_COLORS.RESET

    datetime_start = datetime.now()
    all_categories_lens = [len(cur_list[1]) for cur_list in checkset_data_list]
    categories_max_len = max(all_categories_lens)
    all_texts_total = len(checkset_data_list)

    checkset_test_results = []
    right_categories_counter = 0
    step_counter = 1
    for cur_test_text, cur_test_category in checkset_data_list:
        pgs_conn = PgsAsyncConnection()
        async with PgsAsyncSession(engine=pgs_conn.engine,
                                   log_good_ops=log_pgs_good_ops
                                   ) as pgs_session:
            direct_predicted_category = await get_direct_category_by_text(
                ongoing_session= pgs_session,
                account_id=account_data.account_id,
                account_username=account_data.account_username,
                direct_text=cur_test_text)

        if direct_predicted_category:
            predicted_category = direct_predicted_category
        else:
            predicted_category = bert_model_inst.predict(cur_test_text)

        cur_result_dict = {"checkset_text": cur_test_text,
                           "checkset_category": cur_test_category,
                           "predicted_category": predicted_category}

        if predicted_category == cur_test_category:
            cur_result_dict["checkset_result"] = "OK"
            result_str = f"{green_color}[OK]{reset_color}"
            right_categories_counter += 1
        else:
            cur_result_dict["checkset_result"] = "ERROR"
            result_str = f"{red_color}[ERROR]{reset_color}"

        checkset_test_results.append(cur_result_dict)
        step_counter += 1
        category_str = f"{predicted_category} -".ljust(
            categories_max_len + 2, "-")
        order_str = f"{step_counter}/{all_texts_total}".ljust(9)
        print(f"{order_str} {category_str} {cur_test_text} {result_str}")
    accuracy = round((right_categories_counter / all_texts_total) * 100)
    print("#" * 65)
    print(f"Right Categories: {right_categories_counter}/{all_texts_total} "
          f"[{accuracy} %]\n")

    testing_time = (datetime.now() - datetime_start).total_seconds()
    hours, remainder = [int(el) for el in divmod(testing_time, 3600)]
    minutes, seconds = [int(el) for el in divmod(remainder, 60)]
    testing_time_str = f"{hours} hrs : {minutes} min : {seconds} sec"
    testing_time_str_ru = f"{hours} час {minutes} мин {seconds} сек"
    # testing_time_str = f"{hours} hrs : {minutes} min"
    # testing_time_str_ru = f"{hours} час {minutes} мин"

    json_checkset_test_results = json.dumps(checkset_test_results)
    redis_update = {
        "checkset_status": STATUSES.STATUS_CHECKSET_TEST_FINISH_EN,
        "checkset_complete_status": "complete",
        "checkset_test_results": json_checkset_test_results,
        "all_texts_total": all_texts_total,
        "right_categories_total": right_categories_counter,
        "accuracy": accuracy,
        "testing_time_str": testing_time_str,
        "testing_time_str_ru": testing_time_str_ru,
        "step_t4_model_checkset_testing_finished": "[OK]", }
    redis_error = await redis_save_key_mapping_dict(
        key_name=checkset_redis_name,
        mapping_dict=redis_update,
        expiry_seconds=REDIS_KEY_EXPIRE_TIME)
    if redis_error:
        print(redis_error)

    blue_color = CONSOLE_COLORS.BRIGHT_BLUE
    reset_color = CONSOLE_COLORS.RESET
    print(f"message: BERT model check-set testing finished [OK]\n"
          f"username: {auth_data.username}\n"
          f"model init: {BERT_OPTIONS.BERT_MODEL_INIT}\n"
          f"model name: {BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED}\n"
          f"model path: {BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH}\n"
          f"checkset_file_name: {checkset_file_name}\n"
          f"checkset_redis_name: {checkset_redis_name}\n"
          f"testing_time_str: {testing_time_str}\n"
          f"checkset_test_results: {blue_color}{checkset_test_results[:2]}.....{reset_color}")  # Too long
