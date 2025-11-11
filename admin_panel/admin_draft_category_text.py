from fastapi import Request
from fastapi.responses import RedirectResponse
from sqladmin import ModelView, action
from starlette.responses import HTMLResponse

from ML_BERT_classifier.init_bert import get_global_bert_model_inst
from admin_panel.custom_override_classes import (
    CustomBooleanFilter, CustomStaticValuesFilter)
from configs.enums import DRAFT_STATUS
from configs.labels_messages import LABELS, MESSAGES
from configs.settings import ALCHEMY_OPTIONS
from db_postgres.postgres_conn_async.pgs_async_connection import (
    PgsAsyncConnection)
from db_postgres.postgres_conn_async.postgres_async_session import (
    PgsAsyncSession)
from db_postgres.postgres_conn_sync.pgs_sync_connection import (
    PostgresSyncConn)
from db_postgres.postgres_conn_sync.postgres_sync_session import (
    PgsSyncSession)
from db_postgres.postgres_models.draft_category_text_model import (
    DraftCategoryTextModel)
from db_postgres.postgres_queries.qry_get_id_draft_dict_by_ids_list import (
    get_id_draft_dict_by_ids_list_qry)
from db_postgres.postgres_queries.qry_get_draft_active_data_tuples_sync import (
    get_sync_active_drafts_data)
from db_postgres.postgres_queries.qry_save_new_model_data import (
    save_new_model_data_qry)
from fast_api.app_account_data.scheme_account_data import AccountDataBert
from fast_api.app_add_single_category.func_add_single_category import (
    add_save_single_category)
from fast_api.app_add_text_category.func_add_save_text_category import (
    add_save_single_text_category)


class DraftCategoryTextAdmin(ModelView, model=DraftCategoryTextModel):
    name = LABELS.DRAFT_CATEGORY_TEXT
    name_plural = LABELS.DRAFTS_CATEGORY_TEXT
    icon = LABELS.ICON
    page_size = 200
    page_size_options = [25, 50, 100, 200]
    can_create = False
    can_delete = False

    column_list = [
        DraftCategoryTextModel.id,
        # DraftCategoryTextModel.account_id,
        # DraftCategoryTextModel.account_username,
        DraftCategoryTextModel.account_data,
        DraftCategoryTextModel.ds_existing_category,
        DraftCategoryTextModel.draft_category,
        DraftCategoryTextModel.ds_existing_text,
        DraftCategoryTextModel.draft_text,
        DraftCategoryTextModel.current_status,
        DraftCategoryTextModel.active,
        # DraftCategoryTextModel.updated_at,
        DraftCategoryTextModel.created_at, ]

    column_labels = {
        DraftCategoryTextModel.id: LABELS.ID,
        DraftCategoryTextModel.account_id: LABELS.ACCOUNT_ID,
        DraftCategoryTextModel.account_username: LABELS.ACCOUNT_USERNAME,
        DraftCategoryTextModel.account_data: LABELS.ACCOUNT_DATA,
        DraftCategoryTextModel.ds_existing_category: LABELS.EXISTING_CATEGORY,
        DraftCategoryTextModel.draft_category: LABELS.DRAFT_CATEGORY,
        DraftCategoryTextModel.ds_existing_text: LABELS.EXISTING_TEXT,
        DraftCategoryTextModel.draft_text: LABELS.DRAFT_TEXT,
        DraftCategoryTextModel.current_status: LABELS.DRAFT_STATUS,
        DraftCategoryTextModel.active: LABELS.ACTIVE_STATUS,
        DraftCategoryTextModel.created_at: LABELS.CREATED,
        DraftCategoryTextModel.updated_at: LABELS.UPDATED, }

    column_searchable_list = [
        DraftCategoryTextModel.account_id,
        DraftCategoryTextModel.account_username,
        # DraftCategoryTextModel.account_data,
        DraftCategoryTextModel.ds_existing_category,
        DraftCategoryTextModel.draft_category,
        DraftCategoryTextModel.ds_existing_text,
        DraftCategoryTextModel.draft_text,
        DraftCategoryTextModel.current_status,
        DraftCategoryTextModel.active,
        DraftCategoryTextModel.created_at, ]

    @property
    def column_filters(self):
        pgs_sync_conn = PostgresSyncConn()
        with PgsSyncSession(
                engine=pgs_sync_conn.engine,
                log_good_ops=ALCHEMY_OPTIONS.ALCHEMY_ORM_RAW_SQL_LOGS
        ) as pgs_sync_session:
            active_drafts_data = get_sync_active_drafts_data(
                ongoing_sync_session=pgs_sync_session)
        category_values = active_drafts_data["filter_cat_values"]
        text_values = active_drafts_data["filter_text_values"]
        acc_id_values = active_drafts_data["filter_acc_id_values"]
        username_values = active_drafts_data["filter_username_values"]

        column_filters_list = [
            CustomBooleanFilter(
                column=DraftCategoryTextModel.active,
                title=LABELS.ACTIVE_STATUS),
            CustomStaticValuesFilter(
                column=DraftCategoryTextModel.draft_category,
                values=category_values,
                title=LABELS.DRAFT_CATEGORY),
            CustomStaticValuesFilter(
                column=DraftCategoryTextModel.draft_text,
                values=text_values,
                title=LABELS.DRAFT_TEXT),
            # CustomForeignKeyFilter(
            #     foreign_key=DraftCategoryTextModel.customer_id,
            #     foreign_display_field=CustomerModel.account_id,
            #     foreign_model=CustomerModel,
            #     title=LABELS.ACCOUNT_ID),
            # CustomForeignKeyFilter(
            #     foreign_key=DraftCategoryTextModel.customer_id,
            #     foreign_display_field=CustomerModel.account_username,
            #     foreign_model=CustomerModel,
            #     title=LABELS.ACCOUNT_USERNAME),
            CustomStaticValuesFilter(
                column=DraftCategoryTextModel.account_username,
                values=username_values,
                title=LABELS.ACCOUNT_USERNAME),
            CustomStaticValuesFilter(
                column=DraftCategoryTextModel.account_id,
                values=acc_id_values,
                title=LABELS.ACCOUNT_ID),
        ]
        return column_filters_list

    column_default_sort = [
        (DraftCategoryTextModel.active, True),
        (DraftCategoryTextModel.created_at, True),
    ]  # True - ascending, False - descending

    column_sortable_list = [
        DraftCategoryTextModel.id,
        DraftCategoryTextModel.account_id,
        DraftCategoryTextModel.account_username,
        # DraftCategoryTextModel.account_data,  # Property not allowed
        DraftCategoryTextModel.ds_existing_category,
        DraftCategoryTextModel.draft_category,
        DraftCategoryTextModel.ds_existing_text,
        DraftCategoryTextModel.draft_text,
        DraftCategoryTextModel.current_status,
        DraftCategoryTextModel.active,
        DraftCategoryTextModel.created_at,
        DraftCategoryTextModel.updated_at, ]

    column_details_list = [
        DraftCategoryTextModel.id,
        DraftCategoryTextModel.account_data,
        DraftCategoryTextModel.ds_existing_category,
        DraftCategoryTextModel.draft_category,
        DraftCategoryTextModel.ds_existing_text,
        DraftCategoryTextModel.draft_text,
        DraftCategoryTextModel.current_status,
        DraftCategoryTextModel.active,
        DraftCategoryTextModel.created_at
    ]

    # column_details_exclude_list = [
    #     DraftCategoryTextModel.customer_id,
    #     DraftCategoryTextModel.updated_at, ]

    form_columns = [
        DraftCategoryTextModel.account_id,
        DraftCategoryTextModel.account_username,
        DraftCategoryTextModel.ds_existing_category,
        DraftCategoryTextModel.draft_category,
        DraftCategoryTextModel.ds_existing_text,
        DraftCategoryTextModel.draft_text,
        DraftCategoryTextModel.current_status,
        DraftCategoryTextModel.active,
        DraftCategoryTextModel.created_at, ]

    form_include_pk = True

    # async def update_model(self, request: Request, pk: str, data: dict) -> None:
    #     stmt = select(self.model).where(self.model.id == int(pk))
    #     result = await request.state.session.execute(stmt)
    #     current_model = result.scalar_one()
    #     data["account_id"] = current_model.account_id
    #     return await super().update_model(request, pk, data)

    # TODO: Display readonly ENUM fields
    form_widget_args = {
        "account_id": {"readonly": True},
        "account_username": {"readonly": True},
        "ds_existing_category": {"readonly": True},
        "draft_category": {"readonly": True},
        "ds_existing_text": {"readonly": True},
        "draft_text": {"readonly": True},
        # TODO: Settle issue with disabled field error in SQLAdmin
        # "current_status": {"readonly": True, "disabled": True},
        "created_at": {"readonly": True}, }

    # form_excluded_columns = [  # If form_columns not defined
    #     "id",
    #     "created_at",
    #     "updated_at",
    #     "creation_reason", ]

    @staticmethod
    def format_current_status(model, attribute):  # added in column_formatters/column_formatters_detail
        list_display_value = model.current_status.value
        return list_display_value

    @staticmethod
    def format_created_at(model, attribute):  # added in column_formatters/column_formatters_detail
        formated_data = None
        if model.created_at:
            formated_data = model.created_at.strftime("%d-%m-%Y %H:%M:%S")
        return formated_data

    column_formatters = {
        DraftCategoryTextModel.current_status: format_current_status,
        DraftCategoryTextModel.created_at: format_created_at, }

    column_formatters_detail = {
        DraftCategoryTextModel.current_status: format_current_status,
        DraftCategoryTextModel.created_at: format_created_at, }

    # def can_view_details(self, request: Request) -> bool:
    #     return False
    #
    # def can_create(self, request: Request) -> bool:
    #     return False
    #
    # def can_edit(self, request: Request) -> bool:
    #     return False
    #
    # def can_delete(self, request: Request) -> bool:
    #     return False

    @action(name="custom_action",
            label=MESSAGES.DATASET_ACTION_NAME,
            confirmation_message=MESSAGES.DATASET_CONFIRM_MSG,
            add_in_list=True,
            add_in_detail=True,
            include_in_schema=True)
    async def custom_action_process(
            self, request: Request
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

            print(ds_existing_category, draft_category, ds_existing_text, draft_text)

            if new_category_no_text_flag:
                await add_save_single_category(
                    account_data=account_data,
                    update_category=draft_category,
                    bert_model_inst=bert_model_instance)
                drafts_added_list.append(cur_draft_id)
            elif exist_category_new_text_flag:
                await add_save_single_text_category(
                    account_data=account_data,
                    update_text=draft_text,
                    update_category=draft_category,
                    bert_model_inst=bert_model_instance)
                drafts_added_list.append(cur_draft_id)
            else:
                drafts_skipped_list.append(cur_draft_id)

        pgs_conn = PgsAsyncConnection()
        async with PgsAsyncSession(engine=pgs_conn.engine) as pgs_session:
            for cur_added_draft_id in drafts_added_list:
                await save_new_model_data_qry(
                    ModelClassORM=DraftCategoryTextModel,
                    ongoing_session=pgs_session,
                    new_data={"id": cur_added_draft_id,
                              "current_status": DRAFT_STATUS.DATASET_ADDED,
                              "active": False})

        error_msg = f"{MESSAGES.DRAFTS_ADDED_SUCCESS}: {drafts_added_list}"
        if drafts_skipped_list:
            error_msg = (f"{error_msg}, "
                         f"{MESSAGES.DRAFTS_SKIPPED}: {drafts_added_list}")
        html_content = f"""<script>
        alert("{error_msg}");
        window.location.href = "{referer}";
        </script>"""
        return HTMLResponse(html_content)  # if not result info msg: return RedirectResponse(referer)
