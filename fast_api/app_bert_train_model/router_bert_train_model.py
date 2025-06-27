# import asyncio
# from functools import partial
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from ML_BERT_classifier.init_bert import bert_model_inst
from configs.console_colors import CONSOLE_COLORS
from configs.settings import (
    BERT_MODEL_NAMES, BERT_OPTIONS, BERT_TRAIN_OPTIONS)
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from fast_api.app_auth.scheme_auth import AuthDataBert
from fast_api.app_bert_train_model.scheme_bert_train_model import TrainingData


bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_bert_train_model = APIRouter(prefix=f"/{bert_base_url_name}",
                                    tags=["BERT"])


@router_bert_train_model.post(path="/bert_train_model/",
                              # TODO: Describe responses here
                              response_model=None)
async def bert_train_model(auth_data: AuthDataBert,
                           train_data: TrainingData):
    verify_prod_username_password(username=auth_data.username,
                                  password=auth_data.password)

    # save_after_train_flag = train_data.save_after_train  # TODO: For future

    try:
        print("\nPreparing training data set:")
        datetime_start = datetime.now()
        train_dataset_unique = {}
        for cur_test_phrase, cur_test_label in test_train_dataset.items():
            train_dataset_unique[cur_test_phrase] = cur_test_label
        train_phrases = list(train_dataset_unique.keys())
        train_labels = list(train_dataset_unique.values())
        print(f"train_phrases: {train_phrases}")
        print(f"train_labels: {train_labels}")

        print("\nStart training BERT model:")
        new_train_dataset = bert_model_inst.create_train_dataset(
            texts_list=train_phrases,
            labels_list=train_labels,
            truncation=BERT_TRAIN_OPTIONS.BERT_TOKEN_TRUNCATION,
            padding=BERT_TRAIN_OPTIONS.BERT_TOKEN_PADDING,
            return_tensors=BERT_TRAIN_OPTIONS.BERT_RETURN_TENSOR)
        creating_dataset_time = (datetime.now() - datetime_start).total_seconds()
        creating_dataset_time = round(creating_dataset_time, 1)

        if not new_train_dataset:
            log_text = (f"TrainDataset [ERROR]: get train dataset with"
                        f"method .create_train_dataset() first:\n"
                        f"new_train_dataset: {new_train_dataset}")
            print(log_text)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=log_text)

        print("\nModel training:")
        datetime_start = datetime.now()
        bert_model_inst.train(
            train_dataset=new_train_dataset,
            max_training_epochs=BERT_TRAIN_OPTIONS.BERT_TRAIN_MAX_EPOCHS_NUMBER,
            max_cont_100perc_epochs=BERT_TRAIN_OPTIONS.CONTINUOUS_100PERC_EPOCHS,
            batch_size=BERT_TRAIN_OPTIONS.BERT_TRAIN_BATCH_SUZE,
            learning_rate=BERT_TRAIN_OPTIONS.BERT_TRAIN_LEARNING_RATE)
        training_time = (datetime.now() - datetime_start).total_seconds()
        training_time = round(training_time, 1)
        # print()

        json_response = JSONResponse(
            content={"message": "BERT model training [OK]",
                     "username": auth_data.username,
                     "model init": BERT_OPTIONS.BERT_MODEL_INIT,
                     "model name": BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED,
                     "model path": BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH,
                     "creating data-set time": creating_dataset_time,
                     "training model time": training_time},
            status_code=status.HTTP_200_OK)

        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        reset_color = CONSOLE_COLORS.RESET
        print(f"BERT response.body: {json_response.body}\n"
              f"BERT response.status_code: {json_response.status_code}\n"
              f"username: {auth_data.username}\n"
              f"creating data-set time: {creating_dataset_time}\n"
              f"training model time: {blue_color}{training_time}{reset_color}\n")
        return json_response
    except Exception as error:
        log_text = f"BERT router [ERROR]: error: {error}"
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
