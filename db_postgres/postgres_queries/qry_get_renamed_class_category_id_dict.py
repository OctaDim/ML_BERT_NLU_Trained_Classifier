from typing import Dict

from sqlalchemy.ext.asyncio import AsyncSession

from db_postgres.postgres_models.renamed_class_model import (
    RenamedCustomerClassModel)
from db_postgres.postgres_queries_utils.get_model_records_flex_query import (
    get_model_rows_flex_query)


async def get_renamed_class_category_id_dict(
        ongoing_session: AsyncSession,
        customer_id: int | None,
        reversed_cat_id_renamed_class_dict: bool = False
) -> Dict[int, str] | Dict[str, int]:
    """Returns list of dicts with customer renamed classes"""
    filter_fields = {"customer_id": customer_id}

    pgs_renamed_classes_objs = await get_model_rows_flex_query(
        orm_model_class=RenamedCustomerClassModel,
        ongoing_session=ongoing_session,
        selected_fields=None,
        fields_values_filter=filter_fields,
        order_by_fields=None,
        return_scalars=True)
    # print(f"####### pgs_renamed_classes_objs: {pgs_renamed_classes_objs}")  # Too long
    print(f"####### type(pgs_renamed_classes_objs): {type(pgs_renamed_classes_objs)}")
    print(f"####### len(pgs_renamed_classes_objs): {len(pgs_renamed_classes_objs)}")

    renamed_class_cat_id_dict = {}
    for cur_rec in pgs_renamed_classes_objs:
        renamed_class_name = cur_rec.renamed_class_name
        lab_cat_id = cur_rec.label_category_id
        if reversed_cat_id_renamed_class_dict:
            renamed_class_cat_id_dict[lab_cat_id] = renamed_class_name
        else:
            renamed_class_cat_id_dict[renamed_class_name] = lab_cat_id

    print(f"####### renamed_class_cat_id_dict: {renamed_class_cat_id_dict}")  # Too long
    print(f"####### type(renamed_class_cat_id_dict): {type(renamed_class_cat_id_dict)}")
    print(f"####### len(renamed_class_cat_id_dict): {len(renamed_class_cat_id_dict)}")
    return renamed_class_cat_id_dict
