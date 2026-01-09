from typing import Any

from sqladmin import ModelView
from sqladmin._queries import Query
from starlette.requests import Request
from wtforms import widgets
from wtforms.fields import SelectField

from admin_panel.custom_actions.drafts_category_text_actions import (
    custom_drafts_action_func)
from admin_panel.custom_classes.custom_override_classes import (
    CustomBooleanFilter, CustomStaticValuesFilter, CustAccountDataFilter,
    CustomCurrentStatusFilter)
from configs.enums import DRAFT_STATUS
from configs.labels_messages import LABELS
from configs.settings import ALCHEMY_OPTIONS, SQLADMIN_OPTIONS
from db_postgres.postgres_conn.pgs_connection import (
    PgsSyncConnection)
from db_postgres.postgres_conn.postgres_session import (
    PgsSyncSession)
from db_postgres.postgres_models.draft_category_text_model import (
    DraftCategoryTextModel)
from db_postgres.postgres_queries.qry_get_draft_active_data_tuples_sync import (
    get_sync_active_drafts_data)


class DraftCategoryTextAdmin(ModelView, model=DraftCategoryTextModel):
    name = LABELS.DRAFT_CATEGORY_TEXT
    name_plural = LABELS.DRAFTS_CATEGORIES_TEXT
    icon = LABELS.ICON
    page_size = 200
    page_size_options = [25, 50, 100, 200, 500, 1000]
    can_create = True
    can_delete = True

    # form=CustomDraftCategoryTextForm

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
        pgs_sync_conn = PgsSyncConnection()
        with PgsSyncSession(
                engine=pgs_sync_conn.engine,
                log_good_ops=ALCHEMY_OPTIONS.ALCHEMY_ORM_RAW_SQL_LOGS
        ) as pgs_sync_session:
            active_drafts_data = get_sync_active_drafts_data(
                ongoing_sync_session=pgs_sync_session)
        category_values = active_drafts_data["category_values"]
        text_values = active_drafts_data["text_values"]
        # acc_id_values = active_drafts_data["acc_id_values"]
        # username_values = active_drafts_data["acc_username_values"]
        acc_data_values = active_drafts_data["acc_data_values"]

        column_filters_list = [
            CustomBooleanFilter(  # field: active
                column=DraftCategoryTextModel.active,
                title=LABELS.FILTER_ALLOWED),

            CustomCurrentStatusFilter(  # field: current_status
                column=DraftCategoryTextModel.current_status,
                values=[],  # Defined in override method def lookups (override class CustomCurrentStatusFilter)
                title=LABELS.FILTER_NEW_DRAFT),

            CustAccountDataFilter(  # combine fields: account_username, account_id
                column=DraftCategoryTextModel.account_data,
                values=acc_data_values,
                title=LABELS.FILTER_ACCOUNT_DATA),

            CustomStaticValuesFilter(  # field: draft_category
                column=DraftCategoryTextModel.draft_category,
                values=category_values,
                title=LABELS.FILTER_DRAFT_CATEGORY),

            CustomStaticValuesFilter(  # field: draft_text
                column=DraftCategoryTextModel.draft_text,
                values=text_values,
                title=LABELS.FILTER_DRAFT_TEXT),

            # CustomNewCategoryTextFilter(  # # combine fields: new_category, new_text
            #     column=DraftCategoryTextModel.new_category,
            #     values=[("all", LABELS.ALL_RECS),
            #             ("new_category", LABELS.NEW_CLASS_ONLY),
            #             ("new_text", LABELS.NEW_TEXT_ONLY),
            #             ("new_category_text", LABELS.NEW_CLASS_AND_TEXT)],
            #     title=LABELS.FILTER_NEW_DRAFT),

            # CustomStaticValuesFilter(  # field: account_username
            #     column=DraftCategoryTextModel.account_username,
            #     values=username_values,
            #     title=LABELS.FILTER_ACCOUNT_USERNAME),

            # CustomStaticValuesFilter(  # field: account_id
            #     column=DraftCategoryTextModel.account_id,
            #     values=acc_id_values,
            #     title=LABELS.ACCOUNT_ID),

            # CustomForeignKeyFilter(  # foreign key field: customer_id (display field: account_id)
            #     foreign_key=DraftCategoryTextModel.customer_id,
            #     foreign_display_field=CustomerModel.account_username,
            #     foreign_model=CustomerModel,
            #     title=LABELS.FILTER_ACCOUNT_USERNAME),

            # CustomForeignKeyFilter(  # foreign key field: customer_id (display field: account_id)
            #     foreign_key=DraftCategoryTextModel.customer_id,
            #     foreign_display_field=CustomerModel.account_id,
            #     foreign_model=CustomerModel,
            #     title=LABELS.FILTER_ACCOUNT_ID),

        ]  # <== Do not remove or comment!!! It's used!!!
        return column_filters_list

    column_default_sort = [
        (DraftCategoryTextModel.active, True),  # True - ascending, False - descending
        (DraftCategoryTextModel.created_at, True),  # True - ascending, False - descending
    ]

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

    # column_details_exclude_list = [  # If column_details_list not defined
    #     DraftCategoryTextModel.customer_id,
    #     DraftCategoryTextModel.updated_at, ]

    form_columns = [
        # Work if not overridden by form=CustomDraftCategoryTextForm above
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

    form_overrides = {
        # Work if not overridden by form=CustomDraftCategoryTextForm above
        "current_status": SelectField,
        "active": SelectField,  # SelectField with widget CheckboxInput
    }

    form_args = {
        # Work if not overridden by form=CustomDraftCategoryTextForm above
        "account_id": {
            "default": SQLADMIN_OPTIONS.ADMIN_DEFAULT_DRAFT_ACCOUNT_ID},
        "account_username": {
            "default": SQLADMIN_OPTIONS.ADMIN_DEFAULT_DRAFT_ACCOUNT_USERNAME},
        "current_status": {
            "default": DRAFT_STATUS.ADMIN_DRAFT_CLASS_ADDED,
            # choices=[(status.value, status.name) for status in DRAFT_STATUS],  #  For ordinal enums and custom names
            "choices": [(status.value, status.value) for status in DRAFT_STATUS], },  # For enums embedded in Postgres
        "active": {
            "choices": [("True", "ДА"), ("False", "НЕТ")],
            "default": "True", },
    }

    async def insert_model(self, request: Request, data: dict) -> None:
        new_category_form_field = data.get("draft_category")
        active_form_field = data.get("active")
        if new_category_form_field:
            data["current_status"] = DRAFT_STATUS.ADMIN_DRAFT_CLASS_ADDED
            data["account_id"] = SQLADMIN_OPTIONS.ADMIN_DEFAULT_DRAFT_ACCOUNT_ID
            data["account_username"] = SQLADMIN_OPTIONS.ADMIN_DEFAULT_DRAFT_ACCOUNT_USERNAME
            data["active"] = True if active_form_field == "True" else False  # Because data from SelectField is string
        return await Query(self).insert(data, request)

    async def delete_model(self, request: Request, pk: Any) -> None:
        # Define custom logic if necessary
        await Query(self).delete(pk, request)

    async def update_model(self, request: Request, pk: str, data: dict) -> Any:
        # Define custom logic or custom data if necessary
        return await Query(self).update(pk, data, request)

    # async def update_model(self, request: Request, pk: str, data: dict) -> None:
    #     stmt = select(self.model).where(self.model.id == int(pk))
    #     result = await request.state.session.execute(stmt)
    #     current_model = result.scalar_one()
    #     data["account_id"] = current_model.account_id
    #     return await super().update_model(request, pk, data)

    async def on_model_delete(self, model: Any, request: Request) -> None:
        """Perform some actions before a model is deleted. By default does nothing"""
        # Define custom logic if necessary

    async def after_model_delete(self, model: Any, request: Request) -> None:
        """Perform some actions after a model is deleted. By default do nothing"""
        # Define custom logic if necessary

    # TODO: Display readonly ENUM fields
    form_widget_args = {
        # Work if not overridden by form=CustomDraftCategoryTextForm above
        "account_id": {"readonly": False, "disabled": False},
        "account_username": {"readonly": False, "disabled": False},
        "ds_existing_category": {"readonly": True, "disabled": True},
        "draft_category": {"readonly": False},
        "ds_existing_text": {"readonly": True, "disabled": True},
        "draft_text": {"readonly": True, "disabled": True},
        # TODO: Settle issue with disabled field error in SQLAdmin
        "current_status": {"readonly": False, "disabled": False},
        "created_at": {"readonly": True, "disabled": True},
        "active": {"widget": widgets.CheckboxInput()},
    }

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

    custom_action_process = custom_drafts_action_func  # Custom drafts actions defined in separate func
