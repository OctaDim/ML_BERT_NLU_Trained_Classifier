from sqladmin import ModelView
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

from ML_BERT_classifier.init_bert import get_global_bert_model_inst
from configs.enums import DRAFT_STATUS
from configs.labels_messages import MESSAGES
from configs.settings import (
    ALCHEMY_OPTIONS)
from db_postgres.postgres_conn.pgs_connection import PgsAsyncConnection
from db_postgres.postgres_conn.postgres_session import PgsAsyncSession
from db_postgres.postgres_models.draft_category_text_model import (
    DraftCategoryTextModel)
from db_postgres.postgres_queries.qry_get_id_draft_dict_by_ids_list import (
    get_id_draft_dict_by_ids_list_qry)
from db_postgres.postgres_queries_utils.save_new_model_data import (
    save_new_model_data_qry)
from fast_api.app_account_data.scheme_account_data import (
    AccountDataBert)
from fast_api.app_add_single_category.func_add_single_category import (
    add_save_single_category)
from fast_api.app_add_text_category.func_add_save_text_category import (
    add_save_single_text_category)


async def custom_add_drafts_in_dataset_func(
        self: ModelView,  # current AdminModel
        request: Request,
) -> RedirectResponse | HTMLResponse:
    referer = request.headers.get("referer", "/admin")
    request_selected_ids_str = request.query_params.get("pks")
    if not request_selected_ids_str:
        error_msg = MESSAGES.RECORDS_NOT_SELECTED
        html_content = f"""<script>
        alert("{error_msg}");
        window.location.href = "{referer}";
        </script>"""
        return HTMLResponse(html_content)

    selected_ids_str_list = request_selected_ids_str.split(sep=",")
    print("selected_ids_str_list: ", selected_ids_str_list)

    selected_ids_int_list = [int(ids_str) for ids_str in selected_ids_str_list]
    print("selected_ids_int_list: ", selected_ids_int_list)

    pgs_conn = PgsAsyncConnection()
    async with PgsAsyncSession(
            engine=pgs_conn.engine,
            log_good_ops=ALCHEMY_OPTIONS.ALCHEMY_ORM_RAW_SQL_LOGS
    ) as pgs_session:
        id_draft_dicts_dict = await get_id_draft_dict_by_ids_list_qry(
            ongoing_session=pgs_session,
            drafts_ids_list=selected_ids_int_list)

    not_allowed_drafts_ids = []
    for cur_draft_id in selected_ids_int_list:
        cur_draft_dict = id_draft_dicts_dict[cur_draft_id]
        active = cur_draft_dict["active"]
        if not active:
            not_allowed_drafts_ids.append(cur_draft_id)

    if not_allowed_drafts_ids:
        error_msg = (f"{MESSAGES.DRAFTS_NOT_ALLOWED}: "
                     f"{not_allowed_drafts_ids}")
        html_content = f"""<script>
        alert("{error_msg}");
        window.location.href = "{referer}";
        </script>"""
        return HTMLResponse(html_content)

    drafts_added_list = []
    drafts_skipped_list = []
    for cur_draft_id in selected_ids_int_list:
        cur_draft_dict = id_draft_dicts_dict[cur_draft_id]
        account_id = cur_draft_dict["account_id"]
        account_username = cur_draft_dict["account_username"]
        ds_existing_category = cur_draft_dict["ds_existing_category"]
        draft_category = cur_draft_dict["draft_category"]
        ds_existing_text = cur_draft_dict["ds_existing_text"]
        draft_text = cur_draft_dict["draft_text"]

        new_category_no_text_flag = all([
            not ds_existing_category, draft_category,
            not ds_existing_text, not draft_text])

        exist_category_new_text_flag = all([
            ds_existing_category, draft_category,
            ds_existing_category == draft_category,
            not ds_existing_text, draft_text])

        account_data = AccountDataBert(
            account_id=account_id,
            account_username=account_username)

        bert_model_instance = get_global_bert_model_inst()

        print(f"ds_existing_category: {ds_existing_category}, "
              f"draft_category: {draft_category}\n"
              f"ds_existing_text: {ds_existing_text}, "
              f"draft_text: {draft_text}")

        if new_category_no_text_flag:
            await add_save_single_category(
                account_data=account_data,
                update_category=draft_category,
                bert_model_inst=bert_model_instance)
            drafts_added_list.append(cur_draft_id)
            pgs_conn = PgsAsyncConnection()
            async with PgsAsyncSession(engine=pgs_conn.engine) as pgs_session:
                update_data = {
                    "id": cur_draft_id,
                    "ds_existing_category": draft_category,
                    "current_status": DRAFT_STATUS.NEW_CLASS_DATASET_ADDED,
                    # "new_category": None,
                    # "new_text": None,
                    "active": False}
                await save_new_model_data_qry(
                    ModelClassORM=DraftCategoryTextModel,
                    ongoing_session=pgs_session,
                    new_data=update_data)
        elif exist_category_new_text_flag:
            await add_save_single_text_category(
                account_data=account_data,
                update_text=draft_text,
                update_category=draft_category,
                bert_model_inst=bert_model_instance)
            drafts_added_list.append(cur_draft_id)
            pgs_conn = PgsAsyncConnection()
            async with PgsAsyncSession(engine=pgs_conn.engine) as pgs_session:
                update_data = {
                    "id": cur_draft_id,
                    "ds_existing_text": draft_text,
                    "current_status": DRAFT_STATUS.NEW_TEXT_DATASET_ADDED,
                    # "new_category": None,
                    # "new_text": None,
                    "active": False}
                await save_new_model_data_qry(
                    ModelClassORM=DraftCategoryTextModel,
                    ongoing_session=pgs_session,
                    new_data=update_data)
            await save_new_model_data_qry(
                ModelClassORM=DraftCategoryTextModel,
                ongoing_session=pgs_session,
                new_data=update_data)
        else:
            drafts_skipped_list.append(cur_draft_id)

    # pgs_conn = PgsAsyncConnection()
    # async with PgsAsyncSession(engine=pgs_conn.engine) as pgs_session:
    #     for cur_added_draft_id in drafts_added_list:
    #         update_data = {
    #             "id": cur_added_draft_id,
    #             "current_status": DRAFT_STATUS.NEW_TEXT_DATASET_ADDED,
    #             "active": False}
    #
    #         await save_new_model_data_qry(
    #             ModelClassORM=DraftCategoryTextModel,
    #             ongoing_session=pgs_session,
    #             new_data=update_data)

    error_msg = f"{MESSAGES.DRAFTS_ADDED_SUCCESS}: {drafts_added_list}"
    if drafts_skipped_list:
        error_msg = (f"{error_msg}, "
                     f"{MESSAGES.DRAFTS_SKIPPED}: {drafts_added_list}")
    html_content = f"""<script>
    alert("{error_msg}");
    window.location.href = "{referer}";
    </script>"""
    return HTMLResponse(html_content)  # if not result info msg: return RedirectResponse(referer)
