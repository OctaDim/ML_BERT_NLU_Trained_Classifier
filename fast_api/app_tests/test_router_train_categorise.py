from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from ML_BERT_classifier.class_bert import ClassifierBERT
from configs.settings import (
    BERT_MODEL_NAMES, BERT_OPTIONS, BERT_TRAIN_OPTIONS)
from db_postgres.postgres_dependencies.dep_get_bert_model_instance import (
    get_bert_model_instance_dep)
from fast_api.app_auth.funcs_auth import verify_test_username_password
from fast_api.app_tests.test_func_group_prediction import (
    test_group_prediction)
from fast_api.app_tests.test_schemes import AuthDataTest
from fast_api.app_tests.test_texts_labels import (
    texts_labels)

bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_test_train_categorise = APIRouter(prefix=f"/{bert_base_url_name}",
                                         tags=["TEST"])


@router_test_train_categorise.post(path="/test_train_categorise/",
                                   response_model=None)
async def bert_test_train_categorise(
        auth_data: AuthDataTest,
        bert_model_inst: Annotated[
            ClassifierBERT, Depends(get_bert_model_instance_dep)]
) -> JSONResponse:
    verify_test_username_password(username=auth_data.username,
                                  password=auth_data.password)
    try:
        print("\nPrediction results without model training:")
        test_group_prediction(bert_model_inst=bert_model_inst)

        print("Preparing training data set:")
        train_dataset_unique = {}
        for cur_test_phrase, cur_test_label in texts_labels.items():
            train_dataset_unique[cur_test_phrase] = cur_test_label
        train_phrases = list(train_dataset_unique.keys())
        train_labels = list(train_dataset_unique.values())
        print("####### TEST: train_phrases:", type(train_phrases), train_phrases)
        print("####### TEST: train_labels:", type(train_labels), train_labels)

        new_train_dataset = bert_model_inst.create_train_dataset(
            texts_list=train_phrases,
            labels_list=train_labels,
            truncation=BERT_TRAIN_OPTIONS.BERT_TOKEN_TRUNCATION,
            padding=BERT_TRAIN_OPTIONS.BERT_TOKEN_PADDING,
            return_tensors=BERT_TRAIN_OPTIONS.BERT_RETURN_TENSOR)

        print("####### TEST: new_train_dataset:", type(new_train_dataset), new_train_dataset)

        if not new_train_dataset:
            log_text = (f"TrainDataset [ERROR]: get train dataset with"
                        f"method .create_train_dataset() first:\n"
                        f"new_train_dataset: {new_train_dataset}")
            print(log_text)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=log_text)

        print("Model training:")
        datetime_start = datetime.now()
        await bert_model_inst.train(
            train_dataset=new_train_dataset,
            max_training_epochs=BERT_TRAIN_OPTIONS.BERT_TRAIN_MAX_EPOCHS_NUMBER,
            max_cont_100perc_epochs=BERT_TRAIN_OPTIONS.CONTINUOUS_100PERC_EPOCHS,
            batch_size=BERT_TRAIN_OPTIONS.BERT_TRAIN_BATCH_SUZE,
            learning_rate=BERT_TRAIN_OPTIONS.BERT_TRAIN_LEARNING_RATE)
        training_time = (datetime.now() - datetime_start).total_seconds()
        training_time = round(training_time, 1)
        print()

        print("Prediction results after model training:")
        test_group_prediction()

        json_response = JSONResponse(
            content={"message": "BERT text-phrase categorised [OK]",
                     "username": auth_data.username,
                     "model init": BERT_OPTIONS.BERT_MODEL_INIT,
                     "model name": BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED,
                     "model path": BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH,
                     "training time": training_time},
            status_code=status.HTTP_200_OK)

        print(f"BERT response.body: {json_response.body}\n"
              f"BERT response.status_code: {json_response.status_code}\n"
              f"username: {auth_data.username}\n")
        return json_response
    except Exception as error:
        log_text = f"BERT router [ERROR]: error: {error}"
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
