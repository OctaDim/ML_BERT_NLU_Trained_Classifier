import csv
from datetime import datetime
from io import TextIOWrapper
from typing import TextIO, List, Union, Tuple


class CsvLabelCategory:

    def __init__(self, csv_file_obj: TextIO | TextIOWrapper):
        self.csv_file_obj = csv_file_obj
        self.csv_dict_reader = csv.DictReader(csv_file_obj)

    def get_label_category_dict(
            self, reversed_category_label: bool = False
    ) -> dict[int: str] | dict[str: int]:
        lab_cat_lab_dict = {}
        self.csv_file_obj.seek(0)
        csv_dict_reader = csv.DictReader(self.csv_file_obj)
        for cur_row in csv_dict_reader:
            label = int(cur_row.get("label", "").strip().lower())
            category = str(cur_row.get("category", "").strip().lower())
            if category and (label is not None and label != ""):  # Not if not: label can be zero!!!
                if reversed_category_label:
                    lab_cat_lab_dict[category] = label
                else:
                    lab_cat_lab_dict[label] = category
            else:
                date_time = cur_row.get("date_time", "")
                print(f"Current row skipped, empty field value [ERROR]: "
                      f"label: {label}, category: {category}, "
                      f"date_time: {date_time}\n")
        return lab_cat_lab_dict

    def get_categories_list_sorted(
            self, titled: bool = False
    ) -> list[str]:
        categories_list = []
        self.csv_file_obj.seek(0)
        csv_dict_reader = csv.DictReader(self.csv_file_obj)
        for cur_row in csv_dict_reader:
            category = str(cur_row.get("category", "").strip().lower())
            category = category.title() if titled else category
            categories_list.append(category)
        unique_categories = list(set(categories_list))
        sorted_categories = sorted(unique_categories)
        return sorted_categories

    def add_single_label_category_row(
            self, new_label: str, new_category: str) -> bool:
        csv_writer = csv.writer(self.csv_file_obj,
                                quoting=csv.QUOTE_NONNUMERIC)
        date_time_str = str(datetime.now())
        csv_writer.writerow([date_time_str, new_label, new_category])
        return True

    def add_multi_label_category_rows(
            self, upd_label_category_data: List[Union[List, Tuple]]
    ) -> bool:
        csv_writer = csv.writer(self.csv_file_obj,
                                quoting=csv.QUOTE_NONNUMERIC)
        csv_writer.writerows(upd_label_category_data)
        return True

    def write_new_label_category_csv(
            self, label_category_dict: dict) -> bool:
        csv_writer = csv.writer(self.csv_file_obj,
                                quoting=csv.QUOTE_NONNUMERIC)
        csv_writer.writerow(["date_time", "label", "category"])
        date_time_str = str(datetime.now())
        for key, value in label_category_dict.items():
            csv_writer.writerow([date_time_str, key, value])
        return True
