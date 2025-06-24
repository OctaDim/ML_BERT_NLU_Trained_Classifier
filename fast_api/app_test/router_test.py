from datetime import datetime
from typing import Union

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from ML_BERT_classifier.init_bert import bert_model_instance
from configs.console_colors import CONSOLE_COLORS
from configs.settings import BERT_MODEL_NAMES, BERT_OPTIONS, BERT_TRAIN_OPTIONS
from fast_api.app_test.scheme_test import IncomeDataTest
from test_phrases.test_phrases import test_phrases
from train_data_sets.labels_categories import labels
from train_data_sets.train_data_sets import common_train_dataset


bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_bert_test = APIRouter(prefix=f"/{bert_base_url_name}",
                             tags=["BERT"])


@router_bert_test.post(path="/test/", response_model=None)
async def bert_group_test_text_as_class(
        income_data: IncomeDataTest,
        # TODO: username: Annotated[str, Depends(verify_auth_data)],
) -> Union[JSONResponse, HTTPException]:
    print(f"\n{'#' * 100}")
    text_phrase = income_data.text_phrase
    if not text_phrase:
        log_text = (f"Empty text-phrase not allowed [ERROR]: "
                    f"text_phrase: {text_phrase}")
        print(log_text)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=log_text)

    try:
        datetime_start = datetime.now()

        # prepared_sync_func = partial(get_str_from_wav_vosk,
        #                              model_obj=vosk_model_instance,
        #                              full_file_path=new_wav_full_path,
        #                              log_wav_path=True,
        #                              log_wav_duration=True)
        # phrase = await asyncio.to_thread(prepared_sync_func)  # Executing prepared func

        # ##############################################################
        # ##############################################################
        # ##############################################################
        categories_lens = [len(label) for label in labels.values()]
        category_max_len = max(categories_lens)
        all_phrases_tot = len(test_phrases)
        green_color = CONSOLE_COLORS.BRIGHT_GREEN
        red_color = CONSOLE_COLORS.BRIGHT_RED
        reset_color = CONSOLE_COLORS.RESET

        print("Результаты предсказаний БЕЗ ОБУЧЕНИЯ модели:")
        right_answers_total = 0
        counter = 0
        for cur_test_phrase, cur_test_label in test_phrases.items():
            counter += 1
            pred_category = bert_model_instance.predict(cur_test_phrase)
            if pred_category == labels.get(cur_test_label):
                result_str = f"{green_color}[OK]{reset_color}"
                right_answers_total += 1
            else:
                result_str = f"{red_color}[ERROR]{reset_color}"
            category_str = f"{pred_category} -".ljust(
                category_max_len + 2, "-")
            order_str = f"{counter}/{all_phrases_tot}".ljust(9)
            print(f"{order_str} {category_str} {cur_test_phrase} {result_str}")
        percent = round((right_answers_total / all_phrases_tot) * 100)
        print("#" * 75)
        print(f"Правильные ответы: {right_answers_total}/{all_phrases_tot} "
              f"[{percent} %]\n\n")

        print("Данные для тренировки и дообучения модели:")
        train_dataset_unique = {}
        for cur_test_phrase, cur_test_label in common_train_dataset.items():
            train_dataset_unique[cur_test_phrase] = cur_test_label
        train_phrases = list(train_dataset_unique.keys())
        train_labels = list(train_dataset_unique.values())
        print(f"train_phrases: {train_phrases}\n"
              f"train_labels: {train_labels}\n")

        print("Создание тренировочного дата-сета:")
        bert_model_instance.create_train_dataset(
            texts_list=train_phrases,
            labels_list=train_labels,
            truncation=BERT_TRAIN_OPTIONS.BERT_TOKEN_TRUNCATION,
            padding=BERT_TRAIN_OPTIONS.BERT_TOKEN_PADDING,
            return_tensors=BERT_TRAIN_OPTIONS.BERT_RETURN_TENSOR)
        print()

        if not bert_model_instance.train_dataset:
            log_text = (f"TrainDataset [ERROR]: "
                        f"execute method .create_train_dataset() first")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=log_text)

        print("Дообучение модели:")
        bert_model_instance.train(
            max_training_epochs=BERT_TRAIN_OPTIONS.BERT_TRAIN_MAX_EPOCHS_NUMBER,
            max_cont_100perc_epochs=BERT_TRAIN_OPTIONS.CONTINUOUS_100PERC_EPOCHS,
            batch_size=BERT_TRAIN_OPTIONS.BERT_TRAIN_BATCH_SUZE,
            learning_rate=BERT_TRAIN_OPTIONS.BERT_TRAIN_LEARNING_RATE)
        print()

        print("Результаты предсказаний после ДООБУЧЕНИЯ модели:")
        right_answers_total = 0
        counter = 0
        for cur_test_phrase, cur_test_label in test_phrases.items():
            counter += 1
            pred_category = bert_model_instance.predict(cur_test_phrase)
            if pred_category == labels.get(cur_test_label):
                result_str = f"{green_color}[OK]{reset_color}"
                right_answers_total += 1
            else:
                result_str = f"{red_color}[ERROR]{reset_color}"
            category_str = f"{pred_category} -".ljust(
                category_max_len + 2, "-")
            order_str = f"{counter}/{all_phrases_tot}".ljust(9)
            print(f"{order_str} {category_str} {cur_test_phrase} {result_str}")
        percent = round((right_answers_total / all_phrases_tot) * 100)
        print("#" * 75)
        print(f"Правильные ответы: {right_answers_total}/{all_phrases_tot} "
              f"[{percent} %]\n\n")
        # ##############################################################
        # ##############################################################
        # ##############################################################





        determined_category = "future determined category"

        categorising_time = (datetime.now() - datetime_start).total_seconds()
        categorising_time = round(categorising_time, 1)

        json_response = JSONResponse(
            content={"message": "BERT text-phrase categorised: [OK]",
                     # TODO: "username": username,
                     "model init": BERT_OPTIONS.BERT_MODEL_INIT,
                     "model name": BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED,
                     "model path": BERT_OPTIONS.BERT_MODELS_DOWNLOAD_PATH,
                     "categorising time": categorising_time,
                     "determined_category": determined_category,
                     "text-phrase": text_phrase},
            status_code=status.HTTP_200_OK)

        blue_clr = CONSOLE_COLORS.BRIGHT_BLUE
        reset_clr = CONSOLE_COLORS.RESET
        print(f"BERT response.body: {json_response.body}\n"
              f"BERT response.status_code: {json_response.status_code}\n"
              f"BERT Determined Category: "
              f"{blue_clr}{determined_category}{reset_clr}\n")
        return json_response
    except Exception as error:
        log_text = f"BERT router [ERROR]: error: {error}"
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
    finally:
        # TODO: actions to be done anyway
        pass
