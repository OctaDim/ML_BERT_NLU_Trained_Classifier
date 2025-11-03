from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db_postgres.postgres_models.label_category_model import (
    LabelCategoryModel)
from db_postgres.postgres_models.label_text_model import (
    LabelTextModel)


async def get_label_text_dict_qry(
        ongoing_session: AsyncSession,
        reversed_text_label_dict: bool = False
) -> dict[int, str] | dict[str, int]:
    orm_query = (
        select(LabelCategoryModel.label_index,
               LabelTextModel.text)
        .select_from(LabelTextModel)
        .join(LabelCategoryModel,
              LabelCategoryModel.id == LabelTextModel.label_category_id,
              isouter=True))  # LabelTextModel left join

    result = await ongoing_session.execute(orm_query)
    orm_models_rows = result.all()
    # print(f"####### orm_models_rows: {orm_models_rows}")  # Too long
    print(f"####### type(orm_models_rows): {type(orm_models_rows)}")
    print(f"####### len(orm_models_rows): {len(orm_models_rows)}")

    pgs_lab_text_lab_dict = {}
    if orm_models_rows:
        for cur_row in orm_models_rows:
            if reversed_text_label_dict:
                pgs_lab_text_lab_dict[cur_row.text] = cur_row.label_index
            else:
                pgs_lab_text_lab_dict[cur_row.label_index] = cur_row.text

    # print(f"####### pgs_lab_text_dict: {pgs_lab_text_dict}")  # Too long
    print(f"####### type(pgs_lab_text_dict): {type(pgs_lab_text_lab_dict)}")
    print(f"####### len(pgs_lab_text_dict): {len(pgs_lab_text_lab_dict)}")
    return pgs_lab_text_lab_dict
