from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from ML_BERT_classifier.class_bert import ClassifierBERT
from configs.settings import BERT_MODEL_NAMES, BERT_OPTIONS
from fast_api.fast_api_dependencies.dep_get_bert_model_instance import (
    get_bert_model_instance_dep)
from fast_api.app_auth.funcs_auth import verify_test_username_password
from fast_api.app_tests.test_func_group_prediction import (
    test_group_prediction)
from fast_api.app_tests.test_schemes import AuthDataTest

bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_test_categorise = APIRouter(prefix=f"/{bert_base_url_name}",
                                   tags=["TEST"])


@router_test_categorise.post(path="/test_categorise/",
                             response_model=None)
async def bert_test_categorise(
        auth_data: AuthDataTest,
        bert_model_inst: Annotated[
            ClassifierBERT, Depends(get_bert_model_instance_dep)]
) -> JSONResponse:
    verify_test_username_password(username=auth_data.username,
                                  password=auth_data.password)

    try:
        print("\nPrediction results without model training:")
        datetime_start = datetime.now()
        test_group_prediction(bert_model_inst=bert_model_inst)
        prediction_time = (datetime.now() - datetime_start).total_seconds()
        prediction_time = round(prediction_time, 1)

        json_response = JSONResponse(
            content={"message": "BERT text-phrase categorised [OK]",
                     "username": auth_data.username,
                     "model init": BERT_OPTIONS.BERT_MODEL_INIT,
                     "model name": BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED,
                     "model path": BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH,
                     "group prediction time": prediction_time},
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
