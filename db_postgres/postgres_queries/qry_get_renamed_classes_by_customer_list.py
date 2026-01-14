from typing import Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from db_postgres.postgres_models.renamed_class_model import (
    RenamedCustomerClassModel)
from db_postgres.postgres_queries.qry_get_id_category_dict import (
    get_id_category_dict_qry)
from db_postgres.postgres_queries_utils.get_model_records_flex_query import (
    get_model_rows_flex_query)


async def get_renamed_classes_by_customer(
        ongoing_session: AsyncSession,
        customer_id: int | None,
) -> List[Dict[str, str]] | None:
    """Returns list of dicts with customer renamed classes"""
    filter_fields = {"customer_id": customer_id}

    id_category_dict = await get_id_category_dict_qry(
        ongoing_session=ongoing_session,
        reversed_category_id_dict=False)

    pgs_renamed_classes_objs = await get_model_rows_flex_query(
        orm_model_class=RenamedCustomerClassModel,
        ongoing_session=ongoing_session,
        selected_fields=None,
        fields_values_filter=filter_fields,
        order_by_fields="renamed_class_name",
        return_scalars=True)
    # print(f"####### pgs_renamed_classes_objs: {pgs_renamed_classes_objs}")  # Too long
    print(f"####### type(pgs_renamed_classes_objs): {type(pgs_renamed_classes_objs)}")
    print(f"####### len(pgs_renamed_classes_objs): {len(pgs_renamed_classes_objs)}")

    orig_renamed_class_list = []
    for cur_rec in pgs_renamed_classes_objs:
        renamed_class_name = cur_rec.renamed_class_name
        label_category_id = cur_rec.label_category_id
        model_class_name = id_category_dict.get(label_category_id)
        orig_renamed_class_list.append(
            {"model_class_name": model_class_name,
             "renamed_class_name": renamed_class_name})

    print(f"####### orig_renamed_class_list: {orig_renamed_class_list}")  # Too long
    print(f"####### type(pgs_orig_renamed_class_list): {type(orig_renamed_class_list)}")
    print(f"####### len(orig_renamed_class_list): {len(orig_renamed_class_list)}")
    return orig_renamed_class_list
