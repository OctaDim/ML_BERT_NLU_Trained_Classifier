from typing import Dict, List, Tuple

from sqlalchemy.orm import Session

from db_postgres.postgres_models.draft_category_text_model import (
    DraftCategoryTextModel)
from db_postgres.postgres_queries_utils.get_model_records_flex_query import (
    get_sync_model_rows_flex_query)


def get_sync_active_drafts_data(ongoing_sync_session: Session
                                ) -> Dict[str, List[Tuple[any, any]]]:
    filter_fields = ["draft_category",
                     "draft_text",
                     "account_id",
                     "account_username"]

    pgs_active_drafts_objs = get_sync_model_rows_flex_query(
        orm_model_class=DraftCategoryTextModel,
        ongoing_session=ongoing_sync_session,
        selected_fields=filter_fields,
        fields_values_filter={"active": False},
        order_by_fields=None,
        return_scalars=False)

    drafts_cat_set = set()
    drafts_text_set = set()
    drafts_acc_id_set = set()
    drafts_username_set = set()
    for cur_rec in pgs_active_drafts_objs:
        cur_category = cur_rec.draft_category
        cur_text = cur_rec.draft_text
        cur_acc_id = cur_rec.account_id
        cur_username = cur_rec.account_username
        drafts_cat_set.add(cur_category) if cur_category else None
        drafts_text_set.add(cur_text) if cur_text else None
        drafts_acc_id_set.add(cur_acc_id) if cur_acc_id else None
        drafts_username_set.add(cur_username) if cur_username else None

    drafts_cat_set = sorted(drafts_cat_set)
    drafts_text_set = sorted(drafts_text_set)
    drafts_acc_id_set = sorted(drafts_acc_id_set)
    drafts_username_set = sorted(drafts_username_set)

    filter_cat_values = [(cat, cat) for cat in drafts_cat_set]
    filter_text_values = [(txt, txt) for txt in drafts_text_set]
    filter_acc_id_values = [(acc_id, acc_id) for acc_id in drafts_acc_id_set]
    filter_username_values = [(acc_un, acc_un) for acc_un in drafts_username_set]

    active_drafts_data = {
        "filter_cat_values": filter_cat_values,
        "filter_text_values": filter_text_values,
        "filter_acc_id_values": filter_acc_id_values,
        "filter_username_values": filter_username_values, }
    return active_drafts_data
