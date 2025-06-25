from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from configs.settings import (
    BERT_MODEL_NAMES, BERT_OPTIONS)
from fast_api.app_auth.funcs_auth import verify_username_password
from fast_api.app_auth.scheme_auth import AuthDataTest
from fast_api.app_tests.func_tests import test_group_prediction


bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_test_categorise = APIRouter(prefix=f"/{bert_base_url_name}",
                                   tags=["TEST"])


@router_test_categorise.post(path="/test_categorise/",
                             response_model=None)
async def bert_test_categorise(auth_data: AuthDataTest):
    verify_username_password(username=auth_data.username,
                             password=auth_data.password)

    try:
        print("\nPrediction results without model training:")
        datetime_start = datetime.now()
        test_group_prediction()
        categorising_time = (datetime.now() - datetime_start).total_seconds()
        categorising_time = round(categorising_time, 1)

        json_response = JSONResponse(
            content={"message": "BERT text-phrase categorised: [OK]",
                     # TODO: "username": username,
                     "model init": BERT_OPTIONS.BERT_MODEL_INIT,
                     "model name": BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED,
                     "model path": BERT_OPTIONS.BERT_MODELS_DOWNLOAD_PATH,
                     "group categorising time": categorising_time},
            status_code=status.HTTP_200_OK)

        print(f"BERT response.body: {json_response.body}\n"
              f"BERT response.status_code: {json_response.status_code}\n")
        return json_response
    except Exception as error:
        log_text = f"BERT router [ERROR]: error: {error}"
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
