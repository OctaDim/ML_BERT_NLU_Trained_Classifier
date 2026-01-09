from wtforms.fields.simple import StringField, BooleanField
from wtforms.form import Form
from wtforms.fields import SelectField

from configs.enums import DRAFT_STATUS
from configs.labels_messages import LABELS
from configs.settings import FASTAPI_CONFIG_NAMES, SQLADMIN_OPTIONS


class CustomDraftCategoryTextForm(Form):
    account_id = StringField(
        label=LABELS.ACCOUNT_ID,
        default=SQLADMIN_OPTIONS.ADMIN_DEFAULT_DRAFT_ACCOUNT_ID, )

    account_username = StringField(
        label=LABELS.ACCOUNT_USERNAME,
        default=SQLADMIN_OPTIONS.ADMIN_DEFAULT_DRAFT_ACCOUNT_USERNAME, )

    draft_category = StringField(
        label=LABELS.DRAFT_CATEGORY, )

    current_status = SelectField(
        label=LABELS.DRAFT_STATUS,
        # choices=[(status.value, status.name) for status in DRAFT_STATUS],  #  For ordinal enums and custom names
        choices=[(status.value, status.value) for status in DRAFT_STATUS],  # For enums embedded on the Postgres level
        default=DRAFT_STATUS.ADMIN_DRAFT_CLASS_ADDED.value,
        coerce=str, ) # set int if field is int

    active = BooleanField(
        label=LABELS.ACTIVE_STATUS,
        false_values=(False, "false", "", None), )
