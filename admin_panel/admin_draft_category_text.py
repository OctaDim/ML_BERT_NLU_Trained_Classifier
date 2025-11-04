from fastapi import Request
from fastapi.responses import RedirectResponse
from sqladmin import ModelView, action

from configs.settings import ADMIN_PANEL_OPTIONS
from configs.labels import LABELS
from db_postgres.postgres_models.draft_category_text_model import (
    DraftCategoryTextModel)


class DraftCategoryTextAdmin(ModelView, model=DraftCategoryTextModel):
    name = LABELS.DRAFT_CATEGORY_TEXT
    name_plural = LABELS.DRAFTS_CATEGORY_TEXT
    icon = LABELS.ICON
    page_size = 200
    page_size_options = [25, 50, 100, 200]

    column_list = [
        DraftCategoryTextModel.id,
        DraftCategoryTextModel.account_id,
        DraftCategoryTextModel.account_username,
        DraftCategoryTextModel.ds_existing_category,
        DraftCategoryTextModel.draft_category,
        DraftCategoryTextModel.ds_existing_text,
        DraftCategoryTextModel.draft_text,
        DraftCategoryTextModel.current_status,
        # DraftCategoryTextModel.updated_at,
        DraftCategoryTextModel.created_at, ]

    column_labels = {
        DraftCategoryTextModel.id: LABELS.ID,
        DraftCategoryTextModel.account_id: LABELS.ACCOUNT_ID,
        DraftCategoryTextModel.account_username: LABELS.ACCOUNT_USERNAME,
        DraftCategoryTextModel.ds_existing_category: LABELS.EXISTING_CATEGORY,
        DraftCategoryTextModel.draft_category: LABELS.DRAFT_CATEGORY,
        DraftCategoryTextModel.ds_existing_text: LABELS.EXISTING_TEXT,
        DraftCategoryTextModel.draft_text: LABELS.DRAFT_TEXT,
        DraftCategoryTextModel.current_status: LABELS.DRAFT_STATUS,
        DraftCategoryTextModel.updated_at: LABELS.CREATED,
        DraftCategoryTextModel.created_at: LABELS.UPDATED, }

    column_searchable_list = [
        DraftCategoryTextModel.account_id,
        DraftCategoryTextModel.account_username,
        DraftCategoryTextModel.ds_existing_category,
        DraftCategoryTextModel.draft_category,
        DraftCategoryTextModel.ds_existing_text,
        DraftCategoryTextModel.draft_text,
        DraftCategoryTextModel.current_status,
        DraftCategoryTextModel.created_at, ]

    # TODO: Settle issue with filter fields names or objs error
    # column_filters = [
    #     DraftCategoryTextModel.account_id,
    #     DraftCategoryTextModel.account_username,
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
        DraftCategoryTextModel.ds_existing_category,
        DraftCategoryTextModel.draft_category,
        DraftCategoryTextModel.ds_existing_text,
        DraftCategoryTextModel.draft_text,
        DraftCategoryTextModel.current_status,
        DraftCategoryTextModel.created_at, ]

    form_columns = [
        DraftCategoryTextModel.draft_category,
        DraftCategoryTextModel.draft_text,
        DraftCategoryTextModel.current_status,
        DraftCategoryTextModel.active, ]

    # form_excluded_columns = [  # If form_columns not defined
    #     "id",
    #     "created_at",
    #     "updated_at",
    #     "creation_reason", ]

    @staticmethod
    def format_current_status(model, attribute):
        list_display_value = model.current_status.value
        return list_display_value

    column_formatters = {DraftCategoryTextModel.current_status: format_current_status}
    column_formatters_detail = {DraftCategoryTextModel.current_status: format_current_status}

    def can_view_details(self, request: Request) -> bool:
        return False

    def can_create(self, request: Request) -> bool:
        return False

    def can_edit(self, request: Request) -> bool:
        return False

    def can_delete(self, request: Request) -> bool:
        return False

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
