import csv
from datetime import datetime
from io import TextIOWrapper
from typing import TextIO, Dict


class CsvDirectCategoryText:

    def __init__(self, csv_file_obj: TextIO | TextIOWrapper):
        self.csv_file_obj = csv_file_obj
        self.csv_dict_reader = csv.DictReader(csv_file_obj)

    def get_direct_text_category_dict(
            self, reversed_direct_cat_text: bool = False
    ) -> dict[int: str] | dict[str: int]:
        result_dict = {}
        self.csv_file_obj.seek(0)
        csv_dict_reader = csv.DictReader(self.csv_file_obj)
        for cur_row in csv_dict_reader:
            direct_category = cur_row.get("direct_category", "")
            direct_category = int(direct_category.strip().lower())

            direct_text = cur_row.get("direct_text", "")
            direct_text = str(direct_text.strip().lower())

            if direct_category and direct_text is not None:
                if reversed_direct_cat_text:
                    result_dict[direct_category] = direct_text
                else:
                    result_dict[direct_text] = direct_category
            else:
                date_time = cur_row.get("date_time", "")
                print(f"Current row skipped, empty field value [ERROR]: "
                      f"direct_category: {direct_category}, "
                      f"direct_text: {direct_text}, "
                      f"date_time: {date_time}\n")
        return result_dict

    def get_direct_categories_list_sorted(self) -> list[str]:
        direct_categories_list = []
        self.csv_file_obj.seek(0)
        csv_dict_reader = csv.DictReader(self.csv_file_obj)
        for cur_row in csv_dict_reader:
            category = cur_row.get("direct_category", "").strip()
            # category = category.title()  # Titled if necessary
            direct_categories_list.append(category)
        unique_direct_categories = list(set(direct_categories_list))
        sorted_direct_categories = sorted(unique_direct_categories)
        return sorted_direct_categories

    def add_single_direct_category_text_row(
            self, new_direct_category: str, new_direct_text: str
    ) -> bool:
        csv_writer = csv.writer(self.csv_file_obj,
                                quoting=csv.QUOTE_NONNUMERIC)
        date_time_str = str(datetime.now())
        csv_writer.writerow([
            date_time_str, new_direct_category, new_direct_text])
        return True

    def add_multi_direct_category_text_rows(
            self, upd_direct_category_text_data: list[list]) -> bool:
        csv_writer = csv.writer(self.csv_file_obj,
                                quoting=csv.QUOTE_NONNUMERIC)
        csv_writer.writerows(upd_direct_category_text_data)
        return True

    def write_new_direct_category_text_csv(
            self, direct_category_text_dict: dict) -> bool:
        csv_writer = csv.writer(self.csv_file_obj,
                                quoting=csv.QUOTE_NONNUMERIC)
        csv_writer.writerow([
            "date_time", "direct_category", "direct_text"])
        date_time_str = str(datetime.now())
        for key, value in direct_category_text_dict.items():
            csv_writer.writerow([date_time_str, key, value])
        return True
