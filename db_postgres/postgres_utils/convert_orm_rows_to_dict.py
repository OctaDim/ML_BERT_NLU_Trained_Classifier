from typing import Sequence, Any, List, Tuple

from sqlalchemy import Row, RowMapping

from db_postgres.postgres_async_conn.pgs_async_connection import Base


async def convert_orm_rows_to_dicts(
        orm_rows_sequence: Sequence[Row]
) -> list[dict[str, Any]]:
    model_data_list = []
    for cur_record in orm_rows_sequence:
        cur_rec_dict = {}
        for field_name, field_value in cur_record[0].__dict__.items():
            cur_rec_dict[field_name] = field_value
        model_data_list.append(cur_rec_dict)
    return model_data_list


async def convert_model_recs_to_dicts(
        model_records_list: Sequence[Row|RowMapping]
) -> list[dict[str, Any]]:
    model_data_dicts_list = []
    for cur_record in model_records_list:
        cur_rec_dict = {}
        for field_name, field_value in cur_record.__dict__.items():
            cur_rec_dict[field_name] = field_value
        model_data_dicts_list.append(cur_rec_dict)
    return model_data_dicts_list
