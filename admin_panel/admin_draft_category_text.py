from fastapi import Request
from fastapi.responses import RedirectResponse
from sqladmin import ModelView, action

from configs.labels import LABELS
from configs.settings import ADMIN_PANEL_OPTIONS
from db_postgres.postgres_models.draft_category_text_model import (
    DraftCategoryTextModel)


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
        DraftCategoryTextModel.account_data,
        DraftCategoryTextModel.ds_existing_category,
        DraftCategoryTextModel.draft_category,
        DraftCategoryTextModel.ds_existing_text,
        DraftCategoryTextModel.draft_text,
        DraftCategoryTextModel.current_status,
        DraftCategoryTextModel.active,
        DraftCategoryTextModel.created_at, ]

    # TODO: Settle issue with filter fields names or objs error
    # column_filters = [
    #     DraftCategoryTextModel.account_id,
    #     DraftCategoryTextModel.account_username,
    #     DraftCategoryTextModel.account_data,
    #     DraftCategoryTextModel.ds_existing_category,
    #     DraftCategoryTextModel.draft_category,
    #     DraftCategoryTextModel.ds_existing_text,
    #     DraftCategoryTextModel.draft_text,
    #     DraftCategoryTextModel.current_status,
    #     DraftCategoryTextModel.active,
    #     DraftCategoryTextModel.created_at, ]

    column_default_sort = [
        (DraftCategoryTextModel.created_at, False), ]  # True - ascending, False - descending

    column_sortable_list = [
        DraftCategoryTextModel.account_id,
        DraftCategoryTextModel.account_username,
        # DraftCategoryTextModel.account_data,
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
            label=ADMIN_PANEL_OPTIONS.DATASET_ACTION_NAME,
            confirmation_message=ADMIN_PANEL_OPTIONS.DATASET_CONFIRM_MSG,
            add_in_list=True,
            add_in_detail=True,
            include_in_schema=True)
    async def custom_action_process(self, request: Request) -> RedirectResponse:
        selected_ids_str = request.query_params.get("pks").split(sep=",")
        selected_ids_int = [int(ids_str) for ids_str in selected_ids_str]
        print("admin panel: selected_ids_int: ", selected_ids_int)
        referer = request.headers.get("referer", "/admin")
        return RedirectResponse(referer)
