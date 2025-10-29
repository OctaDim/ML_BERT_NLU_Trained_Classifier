from fastapi import Request
from fastapi.responses import RedirectResponse
from sqladmin import ModelView, action

from configs.settings import ADMIN_PANEL_OPTIONS
from db_postgres.postgres_models.direct_predict_model import (
    DirectPredictModel)


class DirectPredictAdmin(ModelView, model=DirectPredictModel):
    name = "Direct Predict"
    name_plural = "Direct Predicts"
    icon = "Some Icon"

    column_list = [DirectPredictModel.id,
                   DirectPredictModel.account_id,
                   DirectPredictModel.account_username,
                   DirectPredictModel.direct_category,
                   DirectPredictModel.direct_text,
                   # DirectPredictModel.updated_at,
                   DirectPredictModel.created_at, ]

    column_searchable_list = [DirectPredictModel.account_id,
                              DirectPredictModel.account_username,
                              DirectPredictModel.direct_category,
                              DirectPredictModel.direct_text,
                              DirectPredictModel.created_at, ]

    # column_filters = [DirectPredictModel.direct_category,
    #                   DirectPredictModel.active,
    #                   DirectPredictModel.created_at]

    column_default_sort = [(DirectPredictModel.created_at, False)]  # True - ascending, False - descending

    form_columns = ["account_id",
                    "account_username",
                    "direct_category",
                    "direct_text",
                    "active"]

    # form_excluded_columns = [
    #     "id", "created_at", "updated_at", "creation_reason"]  # If form_columns not defined

    page_size = 200
    page_size_options = [25, 50, 100, 200]

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
        selected_ids_list = request.query_params.get("pks").split(sep=",")
        print("admin panel: selected_ids_list: ", selected_ids_list)
        referer = request.headers.get("referer", "/admin")
        return RedirectResponse(referer)
