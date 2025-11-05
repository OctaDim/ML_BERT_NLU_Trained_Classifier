from fastapi import Request
from fastapi.responses import RedirectResponse
from sqladmin import ModelView, action

from configs.labels_messages import MESSAGES
from db_postgres.postgres_models.direct_predict_model import (
    DirectPredictModel)


class DirectPredictAdmin(ModelView, model=DirectPredictModel):
    name = "DIRECT PREDICT"
    name_plural = "DIRECT PREDICTS"
    icon = "octadim"

    column_list = [
        DirectPredictModel.id,
        DirectPredictModel.account_id,
        DirectPredictModel.account_username,
        DirectPredictModel.direct_category,
        DirectPredictModel.direct_text,
        # DirectPredictModel.updated_at,
        DirectPredictModel.created_at, ]

    column_labels = {
        DirectPredictModel.id: "ID",
        DirectPredictModel.account_id: "Account-ID",
        DirectPredictModel.account_username: "Account-Username",
        DirectPredictModel.direct_category: "Direct Category",
        DirectPredictModel.direct_text: "Direct Text",
        DirectPredictModel.created_at: "Created",
        DirectPredictModel.updated_at: "Updated",
        DirectPredictModel.active: "Active", }

    column_searchable_list = [
        DirectPredictModel.account_id,
        DirectPredictModel.account_username,
        DirectPredictModel.direct_category,
        DirectPredictModel.direct_text,
        DirectPredictModel.created_at, ]

    # TODO: Settle issue with filter fields names or objs error
    # column_filters = [
    #     DirectPredictModel.direct_category,
    #     DirectPredictModel.active,
    #     DirectPredictModel.created_at, ]

    column_default_sort = [
        (DirectPredictModel.created_at, False), ]  # True - ascending, False - descending

    form_columns = [
        DirectPredictModel.account_id,
        DirectPredictModel.account_username,
        DirectPredictModel.direct_category,
        DirectPredictModel.direct_text,
        DirectPredictModel.active,
    ]

    # form_excluded_columns = [  # If form_columns not defined
    #     "id",
    #     "created_at",
    #     "updated_at",
    #     "creation_reason", ]

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
            label=MESSAGES.DATASET_ACTION_NAME,
            confirmation_message=MESSAGES.DATASET_CONFIRM_MSG,
            add_in_list=True,
            add_in_detail=True,
            include_in_schema=True)
    async def custom_action_process(self, request: Request) -> RedirectResponse:
        selected_ids_str = request.query_params.get("pks").split(sep=",")
        selected_ids_int = [int(ids_str) for ids_str in selected_ids_str]
        print("admin panel: selected_ids_int: ", selected_ids_int)
        referer = request.headers.get("referer", "/admin")
        return RedirectResponse(referer)
