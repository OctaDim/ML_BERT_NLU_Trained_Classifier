# import asyncio
# from functools import partial
import json
import os.path
from datetime import datetime

from matplotlib import pyplot as plt
import pandas as pd
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

from configs.settings import BERT_MODEL_NAMES, BERT_OPTIONS, BASE_DIR
from db_redis.func_redis_get_part_key_values import get_redis_values_by_pattern
from fast_api.app_auth.funcs_auth import verify_prod_username_password
from fast_api.app_auth.scheme_auth import AuthDataBert
from fast_api.app_get_checkset_result.scheme_get_checkset_result import (
    CheckSetData)
from utils_common.normalized_path import (
    get_full_dir_normal_path, get_full_file_normal_path)

bert_base_url_name = BERT_OPTIONS.BERT_API_URL_BASE_NAME
router_bert_single_checkset_result = APIRouter(prefix=f"/{bert_base_url_name}",
                                               tags=["BERT"])


@router_bert_single_checkset_result.post(path="/bert_get_checkset_result/",
                                         # TODO: Describe responses here
                                         response_model=None)
async def bert_get_single_checkset_result(auth_data: AuthDataBert,
                                          checkset_data: CheckSetData):
    verify_prod_username_password(username=auth_data.username,
                                  password=auth_data.password)
    try:
        print("\nGetting check-set result by check-set file name:")
        checkset_filename = checkset_data.checkset_filename
        if not checkset_filename:
            log_text = (f"Check-sets empty file name [ERROR]: "
                        f"checkset_filename: {checkset_filename}")
            print(log_text)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=log_text)

        datetime_start = datetime.now()
        checkset_prefix = BERT_OPTIONS.BERT_CHECKSET_NAME_REDIS_PREFIX
        redis_checkset_name = f"{checkset_prefix}_{checkset_filename}"
        redis_match_pattern = f"{redis_checkset_name}"  # * - starts, ends with any symbols
        redis_checksets_results = await get_redis_values_by_pattern(
            partial_pattern=redis_match_pattern,
            get_dictionary=False)

        if redis_checksets_results:
            checkset_result = redis_checksets_results[0]
            try:
                json_str_dict = checkset_result.get("checkset_test_results")
                print(f"type(json_str_dict): {type(json_str_dict)}")
                # print(f"json_str_dict: {type(json_str_dict)}, {json_str_dict}")
                if json_str_dict:
                    python_dict = json.loads(json_str_dict)
                    print(f"type(python_dict): {type(python_dict)}")
                    # print(f"python_dict: {type(python_dict)}, {python_dict}")
                    checkset_result["checkset_test_results"] = python_dict
                else:
                    checkset_result["checkset_test_results"] = []
            except Exception as error:
                log_text = (f"Redis json deserialization [ERROR]: "
                            f"error: {error}")
                print(log_text)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=log_text)
        else:
            checkset_result = {}
        getting_time = (datetime.now() - datetime_start).total_seconds()
        getting_time = round(getting_time, 1)

        # ################ CONFUSION MATRIX (start) ####################
        # ##############################################################
        print("\nConfusion Matrix data preparing:")
        checkset_test_results = checkset_result["checkset_test_results"]
        y_true_labels = []
        x_predicted_labels = []
        for cur_result_row in checkset_test_results:
            y_true_labels.append(cur_result_row["checkset_category"])
            x_predicted_labels.append(cur_result_row["predicted_category"])
        all_labels = sorted(set(y_true_labels + x_predicted_labels))

        confusion_mtrx = confusion_matrix(y_true=sorted(y_true_labels),
                                          y_pred=sorted(x_predicted_labels),
                                          labels=all_labels,
                                          sample_weight=None,
                                          normalize=None)

        figure, axes = plt.subplots(figsize=(20, 20))  # Replacing lines bellow
        # figure = plt.figure(figsize=(20, 20))
        # axes = figure.add_subplot()

        conf_mtrx_display = ConfusionMatrixDisplay(
            confusion_matrix=confusion_mtrx,
            display_labels=all_labels)

        conf_mtrx_display.plot(ax=axes, values_format="d", xticks_rotation=30)
        # conf_mtrx_display.plot(ax=axes, values_format=".2f", xticks_rotation=90)
        # conf_mtrx_display.plot(ax=axes, values_format="d", cmap="Blues", xticks_rotation=45)

        conf_matrix_title = BERT_OPTIONS.BERT_CONFUSION_MATRIX_AXE_TITLE
        true_label_text = BERT_OPTIONS.BERT_CONFUSION_MATRIX_TRUE_LABEL_TXT
        predict_label_text = BERT_OPTIONS.BERT_CONFUSION_MATRIX_PREDICT_LABEL_TXT

        axes.set_title(label=conf_matrix_title, fontsize=32)
        axes.set_xlabel(predict_label_text, fontsize=26)
        axes.set_ylabel(true_label_text, fontsize=26)
        axes.tick_params(axis='both', which='major', labelsize=24)

        for text_row in conf_mtrx_display.text_:
            for text in text_row:
                text.set_fontsize(22)
                text.set_fontweight('bold')

        axes.xaxis.label.set_fontsize(26)
        axes.yaxis.label.set_fontsize(26)
        axes.title.set_fontsize(32)

        for label in axes.get_xticklabels():
            label.set_fontsize(20)
        for label in axes.get_yticklabels():
            label.set_fontsize(20)

        cbar = conf_mtrx_display.im_.colorbar
        if cbar:
            cbar.ax.tick_params(labelsize=20)
            cbar.ax.yaxis.label.set_size(22)

        print("\nConfusion Matrix image filename creating:")
        checkset_no_ext_name, _ = os.path.splitext(checkset_filename)
        conf_mtrx_save_dir = BERT_OPTIONS.BERT_CONFUSION_MATRICES_IMAGES_PATH
        conf_mtrx_dir_path = get_full_dir_normal_path(
            all_dir_str_parts=[BASE_DIR, conf_mtrx_save_dir])

        if not os.path.isdir(conf_mtrx_dir_path):
            os.makedirs(conf_mtrx_dir_path, exist_ok=True)

        conf_mtrx_img_filename = f"{checkset_no_ext_name}.png"
        conf_mtrx_img_file_path = get_full_file_normal_path(
            all_dir_str_parts=[conf_mtrx_dir_path],
            file_name_with_ext=conf_mtrx_img_filename)

        plt.tight_layout()

        print("\nConfusion Matrix image saving:")
        plt.savefig(conf_mtrx_img_file_path,
                    format="png",
                    dpi=100,
                    # quality=95,  # Not for jpg, for png can be used
                    transparent=False,
                    # bbox_inches="tight",
                    facecolor="white",
                    edgecolor="none")

        print("\nConfusion Matrix window displaying:")
        plt.show()  # Important: Only after savefig(), because show() cleans figure

        print("\nConfusion Matrix data frame creating:")
        conf_mtrx_data_frame = pd.DataFrame(
            confusion_mtrx, index=all_labels, columns=all_labels)
        print(f"conf_mtrx_data_frame:\n"
              f"{conf_mtrx_data_frame}")

        if not os.path.isfile(conf_mtrx_img_file_path):
            conf_mtrx_img_filename = ""
        # ################# CONFUSION MATRIX (end) #####################
        # ##############################################################

        json_content = {
            "message": "BERT train model tasks list [OK]",
            "username": auth_data.username,
            "model init": BERT_OPTIONS.BERT_MODEL_INIT,
            "model name": BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED,
            "model path": BERT_OPTIONS.BERT_INITIAL_MODEL_DOWNLOAD_PATH,
            "getting_time": getting_time,
            "checkset_result": checkset_result,
            "conf_mtrx_filename": conf_mtrx_img_filename}
        json_response = JSONResponse(
            content=json_content,
            status_code=status.HTTP_200_OK)

        print(f"BERT response message: {json_content.get('message')}\n"
              f"BERT response.body keys: {json_content.keys()}\n"
              # f"BERT response.body: {json_response.body}\n"  # Long to log
              f"BERT response.status_code: {json_response.status_code}\n"
              f"username: {auth_data.username}\n"
              f"getting_time: {getting_time}\n"
              f"type(checkset_result): {type(checkset_result)}\n"
              # f"checkset_result: {checkset_result}\n"  # Long to log
              f"checkset_result.keys(): {checkset_result.keys()}\n"
              f"conf_mtrx_filename: {conf_mtrx_img_filename}\n")
        return json_response
    except Exception as error:
        log_text = (f"BERT router get check-set result [ERROR]: "
                    f"error: {error}")
        print(log_text)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=log_text)
