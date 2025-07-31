from datetime import datetime, timedelta

from torch.utils.data import TensorDataset

from ML_BERT_classifier.init_bert import bert_model_inst
from configs.console_colors import CONSOLE_COLORS
from configs.settings import (
    REDIS_OPTIONS, BERT_OPTIONS, BERT_MODEL_NAMES, BERT_TRAIN_OPTIONS)
from db_redis.func_redis_save_key_mapping import redis_save_key_mapping_dict
from fast_api.app_auth.scheme_auth import AuthDataBert
from fast_api.app_bert_save_model.router_bert_save_model import (
    bert_save_model)
from fast_api.app_bert_save_model.scheme_bert_save_model import (
    SaveModelDataBert, SaveModelAfterTrainBert)
from fast_api.app_bert_train_model.scheme_bert_train_model import (
    TrainModelDataBert)


async def background_train_save_model(
        auth_data: AuthDataBert,
        train_model_data: TrainModelDataBert,
        new_train_dataset: TensorDataset,
        dataset_name: str,
        train_text_lab_csv_path: str,
        creating_dataset_time: float
) -> None:
    print("\nBERT model training start:")
    REDIS_KEY_EXPIRE_TIME = timedelta(days=REDIS_OPTIONS.STATUSES_EXPIRY_DAYS)

    redis_update = {
        "status": REDIS_OPTIONS.STATUS_TRAIN_PROCESS,
        "step_4_training_start": "[OK]",
    }
    redis_error = await redis_save_key_mapping_dict(
        key_name=dataset_name,
        mapping_dict=redis_update,
        expiry_seconds=REDIS_KEY_EXPIRE_TIME)
    if redis_error:
        print(redis_error)

    datetime_start = datetime.now()
    # TODO: Training model temporary switched off
    # time.sleep(60)
    bert_model_inst.train(
        train_dataset=new_train_dataset,
        max_training_epochs=BERT_TRAIN_OPTIONS.BERT_TRAIN_MAX_EPOCHS_NUMBER,
        max_cont_100perc_epochs=BERT_TRAIN_OPTIONS.CONTINUOUS_100PERC_EPOCHS,
        batch_size=BERT_TRAIN_OPTIONS.BERT_TRAIN_BATCH_SUZE,
        learning_rate=BERT_TRAIN_OPTIONS.BERT_TRAIN_LEARNING_RATE)
    training_time = (datetime.now() - datetime_start).total_seconds()
    hours, remainder = [int(el) for el in divmod(training_time, 3600)]
    minutes, seconds = [int(el) for el in divmod(remainder, 60)]
    # training_time_str = f"{hours} hrs : {minutes} min : {seconds} sec"
    training_time_str = f"{hours} hrs : {minutes} min"
    training_time_str_ru = f"{hours} час {minutes} мин"

    redis_update = {
        "status": REDIS_OPTIONS.STATUS_TRAIN_FINISH,
        "training_time_str": training_time_str,
        "training_time_str_ru": training_time_str_ru,
        "step_5_training_finish": "[OK]",
    }
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
          f"train dataset path: {train_text_lab_csv_path}\n"
          f"creating dataset time: {creating_dataset_time}\n"
          f"new_train_dataset: {new_train_dataset}\n"
          f"dataset_name: {dataset_name}\n"
          f"training model time: {blue_color}{training_time_str}{reset_color}\n")

    if train_model_data.save_model_after_train:
        print("\nBERT saving model after train start:")
        redis_update = {
            "status": REDIS_OPTIONS.STATUS_MODEL_SAVING_START,
            "step_6-2_saving_model_start": "[OK]",
        }
        redis_error = await redis_save_key_mapping_dict(
            key_name=dataset_name,
            mapping_dict=redis_update,
            expiry_seconds=REDIS_KEY_EXPIRE_TIME)
        if redis_error:
            print(redis_error)

        trained_model_save_dir_path = train_model_data.trained_model_save_dir_path

        # Preparing main Pydantic data for bert_save_model router view
        save_model_data_bert = SaveModelDataBert(
            model_save_dir_path=trained_model_save_dir_path)

        # Preparing extra Pydantic data for bert_save_model router view
        save_model_after_train_bert = SaveModelAfterTrainBert(
            trained_model_redirected_save_flag=True,
            redirected_train_text_lab_csv_path=train_text_lab_csv_path,
            redirected_creating_dataset_time=creating_dataset_time,
            redirected_training_time=training_time_str)

        # Redirecting to bert_save_model router view with necessary params
        await bert_save_model(
            auth_data=auth_data,
            save_model_data=save_model_data_bert,
            save_model_after_train_data=save_model_after_train_bert,
            dataset_name=dataset_name,
        )
    else:
        print("\nBERT training model without saving finish:")
        redis_update = {
            "status": REDIS_OPTIONS.STATUS_TRAIN_NO_SAVE_FINISH,
            "complete_status": "complete",
            "step_6-1_training_no_saving_finish": "[OK]",
        }
        redis_error = await redis_save_key_mapping_dict(
            key_name=dataset_name,
            mapping_dict=redis_update,
            expiry_seconds=REDIS_KEY_EXPIRE_TIME)
        if redis_error:
            print(redis_error)
