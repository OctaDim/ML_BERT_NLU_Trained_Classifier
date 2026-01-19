from typing import Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from db_postgres.postgres_queries.qry_get_id_category_dict import (
    get_id_category_dict_qry)
from db_postgres.postgres_queries.qry_get_renamed_class_category_id_dict import (
    get_renamed_class_cat_id_dict)


async def get_renamed_classes_by_customer_list(
        ongoing_session: AsyncSession,
        customer_id: int | None,
) -> List[Dict[str, str]]:
    """Returns list of dicts with all model classes taking into account
    customer renamed classes"""

    id_category_dict = await get_id_category_dict_qry(
        ongoing_session=ongoing_session,
        reversed_category_id_dict=False)
    print(f"####### id_category_dict: {id_category_dict}")  # Too long
    print(f"####### type(id_category_dict): {type(id_category_dict)}")
    print(f"####### len(id_category_dict): {len(id_category_dict)}")

    cat_id_renamed_class_dict = await get_renamed_class_cat_id_dict(
        ongoing_session=ongoing_session,
        customer_id=customer_id,
        reversed_cat_id_renamed_class_dict=True)

    original_renamed_classes = []
    for cur_cat_id, cur_model_class_name in id_category_dict.items():
        if cur_cat_id in cat_id_renamed_class_dict.keys():
            renamed_class_name = cat_id_renamed_class_dict[cur_cat_id]
        else:
            renamed_class_name = cur_model_class_name
        original_renamed_classes.append(
            {"label_category_id": cur_cat_id,
             "model_class_name": cur_model_class_name,
             "renamed_class_name": renamed_class_name})

    # # Sorted when pgs requesting ids-categories dictionary
    # original_renamed_classes = sorted(original_renamed_classes,
    #                                   key=lambda x: x['model_class_name'])

    print(f"####### original_renamed_classes: {original_renamed_classes}")  # Too long
    print(f"####### type(original_renamed_classes): {type(original_renamed_classes)}")
    print(f"####### len(original_renamed_classes): {len(original_renamed_classes)}")
    return original_renamed_classes
