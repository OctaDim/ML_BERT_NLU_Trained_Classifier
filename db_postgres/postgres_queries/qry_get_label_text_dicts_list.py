from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db_postgres.postgres_conn_async.pgs_async_connection import (
    PgsAsyncConnection)
from db_postgres.postgres_conn_async.postgres_async_session import (
    PgsAsyncSession)
from db_postgres.postgres_models.label_category_model import (
    LabelCategoryModel)
from db_postgres.postgres_models.label_text_model import (
    LabelTextModel)


async def get_label_text_dicts_list_qry(
        ongoing_session: AsyncSession,
) -> List[Dict[str, int | str]] | None:
    """Returns list of dicts with label_index (int) and text (str)"""
    orm_query = (
        select(LabelCategoryModel.label_index,
               LabelTextModel.text,
               LabelTextModel.created_at)
        .select_from(LabelTextModel)
        .join(LabelCategoryModel,
              LabelCategoryModel.id == LabelTextModel.label_category_id,
              isouter=True))  # LabelTextModel left join

    result = await ongoing_session.execute(orm_query)
    orm_models_rows = result.all()
    # print(f"####### orm_models_rows: {orm_models_rows}")  # Too long
    print(f"####### type(orm_models_rows): {type(orm_models_rows)}")
    print(f"####### len(orm_models_rows): {len(orm_models_rows)}")

    pgs_lab_text_list = []
    if orm_models_rows:
        for cur_row in orm_models_rows:
            cur_lab_text_dict = {"label_index": cur_row.label_index,
                                 "text": cur_row.text}
            pgs_lab_text_list.append(cur_lab_text_dict)
    # print(f"####### pgs_lab_text_list: {pgs_lab_text_list}")  # Too long
    print(f"####### type(pgs_lab_text_list): {type(pgs_lab_text_list)}")
    print(f"####### len(pgs_lab_text_list): {len(pgs_lab_text_list)}")
    return pgs_lab_text_list


if __name__ == "__main__":
    import asyncio


    async def test_get_label_text_list_qry():
        pgs_conn = PgsAsyncConnection()
        async with PgsAsyncSession(engine=pgs_conn.engine) as pgs_session:
            pgs_text_lab_list = await get_label_text_dicts_list_qry(
                ongoing_session=pgs_session)
            for cur_row in pgs_text_lab_list:
                print(cur_row)


    asyncio.run(main=test_get_label_text_list_qry(), debug=True)
