from fastapi import BackgroundTasks
from sqladmin import ModelView
from starlette.requests import Request
from starlette.responses import RedirectResponse, HTMLResponse

from configs.labels_messages import MESSAGES
from configs.settings import (
    API_USERNAME, API_PASSWORD, SQLADMIN_OPTIONS, API_HOST, API_PORT,
    BERT_OPTIONS)
from fast_api.app_account_data.scheme_account_data import (
    AccountDataBert)
from fast_api.app_auth.scheme_auth import AuthDataBert
from fast_api.app_bert_train_model.router_bert_train_model import (
    bert_train_model, bert_base_url_name, bert_train_model_url)
from fast_api.app_bert_train_model.scheme_bert_train_model import (
    TrainModelDataBert)
from fast_api.fast_api_dependencies.dep_get_bert_model_instance import (
    get_bert_model_instance_dep)
import httpx


async def custom_start_train_model_func(
        self: ModelView,  # current AdminModel
        request: Request,
) -> RedirectResponse | HTMLResponse:
    referer = request.headers.get("referer", "/admin")

    auth_data = AuthDataBert(
        username=API_USERNAME,
        password=API_PASSWORD)
    account_data = AccountDataBert(
        account_id=SQLADMIN_OPTIONS.ADMIN_DEFAULT_DRAFT_ACCOUNT_ID,
        account_username=SQLADMIN_OPTIONS.ADMIN_DEFAULT_DRAFT_ACCOUNT_USERNAME)
    train_model_data = TrainModelDataBert(
        save_model_after_train=True,
        trained_model_save_dir_path="")
    background_tasks = BackgroundTasks()
    bert_model_inst = await get_bert_model_instance_dep()
    await bert_train_model(auth_data=auth_data,
                           account_data=account_data,
                           train_model_data=train_model_data,
                           background_tasks=background_tasks,
                           bert_model_inst=bert_model_inst)

    # If used with httpx request, background_tasks.add_task(background_train_save_model) can be used
    # async with httpx.AsyncClient() as httpx_client:
    #     url = (f"http://{API_HOST}:{API_PORT}/"
    #            f"{BERT_OPTIONS.BERT_API_URL_BASE_NAME}{bert_train_model_url}")
    #     auth_data = {"username": API_USERNAME,
    #                  "password": API_PASSWORD}
    #     account_data = {
    #         "account_id": SQLADMIN_OPTIONS.ADMIN_DEFAULT_DRAFT_ACCOUNT_ID,
    #         "account_username": SQLADMIN_OPTIONS.ADMIN_DEFAULT_DRAFT_ACCOUNT_USERNAME}
    #     train_model_data = {"save_model_after_train": True,
    #                         "trained_model_save_dir_path": ""}
    #     request_data = {"auth_data": auth_data,
    #                     "account_data": account_data,
    #                     "train_model_data": train_model_data}
    #     start_train_model_resp = await httpx_client.post(
    #         url=url,
    #         json=request_data,
    #         timeout=SQLADMIN_OPTIONS.TRAIN_MODEL_ACTION_TIMEOUT)

    msg_txt = MESSAGES.TRAIN_MODEL_START_PROCESS_MSG
    html_content = f"""
    <script>
    alert("{msg_txt}");
    window.location.href = "{referer}";
    </script>"""
    return HTMLResponse(html_content)
