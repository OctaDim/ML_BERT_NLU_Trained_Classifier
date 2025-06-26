# import asyncio
# from functools import partial
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from ML_BERT_classifier.init_bert import bert_model_instance
from configs.console_colors import CONSOLE_COLORS
from configs.settings import BERT_MODEL_NAMES, BERT_OPTIONS
from fast_api.app_auth.funcs_auth import verify_product_username_password
from fast_api.app_auth.scheme_auth import AuthDataBert
from fast_api.app_predict.schemes_predict import PredictDataBert


bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_predict_single_text = APIRouter(prefix=f"/{bert_base_url_name}",
                                       tags=["BERT"])


@router_predict_single_text.post(path="/predict_single_text/",
                                 # TODO: Describe responses here
                                 response_model=None)
async def bert_predict_single_text(auth_data: AuthDataBert,
                                   predict_data: PredictDataBert):
    verify_product_username_password(username=auth_data.username,
                                     password=auth_data.password)

    text_phrase = predict_data.text_phrase
    if not text_phrase:
        log_text = (f"Empty text-phrase not allowed to predict [ERROR]: "
                    f"categorise_data.text_phrase: {predict_data.text_phrase}")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=log_text)

    try:
        print("\nPrediction single text:")
        datetime_start = datetime.now()
        # predicted_category = bert_model_instance.predict(text_phrase)
        # prepared_sync_func = partial(bert_model_instance.predict,
        #                              text=text_phrase)
        # predicted_category = await asyncio.to_thread(prepared_sync_func)  # Exec prepared func
        prediction_time = (datetime.now() - datetime_start).total_seconds()
        prediction_time = round(prediction_time, 1)

        json_response = JSONResponse(
            content={"message": "BERT text-phrase categorised: [OK]",
                     "username": auth_data.username,
                     "model init": BERT_OPTIONS.BERT_MODEL_INIT,
                     "model name": BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED,
                     "model path": BERT_OPTIONS.BERT_MODELS_DOWNLOAD_PATH,
                     "prediction time": prediction_time,
                     "predicted_category": predicted_category,
                     "text-phrase": text_phrase},
            status_code=status.HTTP_200_OK)

        blue_color = CONSOLE_COLORS.BRIGHT_BLUE
        reset_color = CONSOLE_COLORS.RESET
        print(f"BERT response.body: {json_response.body}\n"
              f"BERT response.status_code: {json_response.status_code}\n"
              f"username: {auth_data.username}\n"
              f"predicted_category: {blue_color}{predicted_category}{reset_color}\n"
              f"prediction time: {prediction_time}\n")
        return json_response
    except Exception as error:
        log_text = f"BERT router [ERROR]: error: {error}"
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
