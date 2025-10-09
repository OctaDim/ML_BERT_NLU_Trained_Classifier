from datetime import datetime, timedelta

from torch.utils.data import TensorDataset

from ML_BERT_classifier.class_bert import ClassifierBERT
from configs.console_colors import CONSOLE_COLORS
from configs.settings import (
    REDIS_OPTIONS, BERT_OPTIONS, BERT_MODEL_NAMES, STATUSES,
    BERT_TRAIN_OPTIONS)
from db_redis.redis_funcs.func_redis_save_key_mapping import (
    redis_save_key_mapping_dict)
from fast_api.app_account_data.scheme_account_data import (
    AccountDataBert)
from fast_api.app_auth.scheme_auth import AuthDataBert
from fast_api.app_bert_save_model.router_bert_save_model import (
    bert_save_model)
from fast_api.app_bert_save_model.scheme_bert_save_model import (
    SaveModelDataBert, SaveModelAfterTrainBert)
from fast_api.app_bert_train_model.scheme_bert_train_model import (
    TrainModelDataBert)


async def background_train_save_model(
        auth_data: AuthDataBert,
        account_data: AccountDataBert,
        train_model_data: TrainModelDataBert,
        new_train_dataset: TensorDataset,
        dataset_name: str,
        train_text_lab_csv_path: str,
        creating_dataset_time: float,
        bert_model_inst: ClassifierBERT
) -> None:
    print("#" * 65)
    print("BERT model background training start:")
    REDIS_KEY_EXPIRE_TIME = timedelta(days=REDIS_OPTIONS.STATUSES_EXPIRY_DAYS)

    redis_update = {
        "train_status": STATUSES.STATUS_MODEL_TRAIN_PROCESS_EN,
        "train_step_7_model_training_in_process": "[OK]", }
    redis_error = await redis_save_key_mapping_dict(
        key_name=dataset_name,
        mapping_dict=redis_update,
        expiry_seconds=REDIS_KEY_EXPIRE_TIME)
    if redis_error:
        print(redis_error)

    datetime_start = datetime.now()
    if BERT_TRAIN_OPTIONS.BERT_TEMPORARY_SKIP_TRAINING:
        print("**** MODEL TRAINING TEMPORARY SWITCHED OFF (start) ****")
        # await asyncio.sleep(60)
        # time.sleep(60)
        print("***** MODEL TRAINING TEMPORARY SWITCHED OFF (end) *****")
    else:
        print("********* MODEL TRAINING SWITCHED ON (start) **********")
        await bert_model_inst.train(
            train_dataset=new_train_dataset,
            max_training_epochs=BERT_TRAIN_OPTIONS.BERT_TRAIN_MAX_EPOCHS_NUMBER,
            max_cont_100perc_epochs=BERT_TRAIN_OPTIONS.CONTINUOUS_100PERC_EPOCHS,
            batch_size=BERT_TRAIN_OPTIONS.BERT_TRAIN_BATCH_SUZE,
            learning_rate=BERT_TRAIN_OPTIONS.BERT_TRAIN_LEARNING_RATE)
        print("********** MODEL TRAINING SWITCHED ON (end) ***********")

    training_time = (datetime.now() - datetime_start).total_seconds()
    hours, remainder = [int(el) for el in divmod(training_time, 3600)]
    minutes, seconds = [int(el) for el in divmod(remainder, 60)]
    # training_time_str = f"{hours} hrs : {minutes} min : {seconds} sec"
    training_time_str = f"{hours} hrs : {minutes} min"
    training_time_str_ru = f"{hours} час {minutes} мин"

    redis_update = {
        "train_status": STATUSES.STATUS_TRAINED_MODEL_SAVE_FINISH_EN,
        "training_time_str": training_time_str,
        "training_time_str_ru": training_time_str_ru,
        "train_step_8_model_training_finished": "[OK]", }
    redis_error = await redis_save_key_mapping_dict(
        key_name=dataset_name,
        mapping_dict=redis_update,
        expiry_seconds=REDIS_KEY_EXPIRE_TIME)
    if redis_error:
        print(redis_error)

    blue_color = CONSOLE_COLORS.BRIGHT_BLUE
    reset_color = CONSOLE_COLORS.RESET
    print(f"message: BERT model trained [OK]\n"
          f"username: {auth_data.username}\n"
          f"model init: {BERT_OPTIONS.BERT_MODEL_INIT}\n"
          f"model name: {BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED}\n"
          f"model path: {BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH}\n"
          f"train_text_lab_csv_path: {train_text_lab_csv_path}\n"
          f"creating_dataset_time: {creating_dataset_time}\n"
          f"new_train_dataset: {new_train_dataset}\n"
          f"dataset_name: {dataset_name}\n"
          f"training_time_str: {blue_color}{training_time_str}{reset_color}\n")

    if train_model_data.save_model_after_train:
        print("BERT background saving model after train start:")
        redis_update = {
            "train_status": STATUSES.STATUS_TRAINED_MODEL_SAVE_START_EN,
            "train_step_9_saving_model_after_training_started": "[OK]", }
        redis_error = await redis_save_key_mapping_dict(
            key_name=dataset_name,
            mapping_dict=redis_update,
            expiry_seconds=REDIS_KEY_EXPIRE_TIME)
        if redis_error:
            print(redis_error)

        trained_model_save_dir_path = train_model_data.trained_model_save_dir_path

        print("Preparing main Pydantic data for bert_save_model router view")
        save_model_data_bert = SaveModelDataBert(
            model_save_dir_path=trained_model_save_dir_path)

        print("Preparing extra Pydantic data for bert_save_model router view")
        save_model_after_train_bert = SaveModelAfterTrainBert(
            trained_model_redirected_save_flag=True,
            redirected_train_text_lab_csv_path=train_text_lab_csv_path,
            redirected_creating_dataset_time=creating_dataset_time,
            redirected_training_time=training_time_str)

        print("Redirecting to bert_save_model router view with necessary params")
        await bert_save_model(
            auth_data=auth_data,
            account_data=account_data,
            save_model_data=save_model_data_bert,
            save_model_after_train_data=save_model_after_train_bert,
            # dataset_name=dataset_name,
            bert_model_inst=bert_model_inst)

        print("BERT background saving model after train finished")
        redis_update = {
            "train_status": STATUSES.STATUS_TRAIN_AND_SAVE_COMPLETE_EN,
            "train_step_12_saving_model_after_training_complete": "[OK]", }
        redis_error = await redis_save_key_mapping_dict(
            key_name=dataset_name,
            mapping_dict=redis_update,
            expiry_seconds=REDIS_KEY_EXPIRE_TIME)
        if redis_error:
            print(redis_error)
    else:
        print("BERT background training model without saving completed:")
        redis_update = {
            "train_status": STATUSES.STATUS_TRAIN_WITHOUT_SAVE_COMPLETE_EN,
            "train_complete_status": "complete",
            "train_step_1212_training_without_saving_complete": "[OK]", }
        redis_error = await redis_save_key_mapping_dict(
            key_name=dataset_name,
            mapping_dict=redis_update,
            expiry_seconds=REDIS_KEY_EXPIRE_TIME)
        if redis_error:
            print(redis_error)
