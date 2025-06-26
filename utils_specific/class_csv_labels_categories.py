import csv
from io import TextIOWrapper
from typing import TextIO


class CsvLabelCategory:

    def __init__(self, csv_file_obj: TextIO | TextIOWrapper):
        self.csv_file_obj = csv_file_obj
        self.csv_dict_reader = csv.DictReader(csv_file_obj)

    def get_labels_categories_dict(self) -> dict[int: str]:
        labels_categories = {}
        self.csv_file_obj.seek(0)
        csv_dict_reader = csv.DictReader(self.csv_file_obj)
        for cur_row in csv_dict_reader:
            label = cur_row.get("label", "").strip().lower()
            category = cur_row.get("category", "").strip().lower()
            if label and category:
                labels_categories[label] = category
            else:
                date_time = cur_row.get("date_time", "")
                print(f"Current row skipped, empty field value [ERROR]: "
                      f"label: {label}, category: {category}, "
                      f"date_time: {date_time}\n")
        return labels_categories

    def get_categories_list_sorted(self) -> list[str]:
        categories_list = []
        self.csv_file_obj.seek(0)
        csv_dict_reader = csv.DictReader(self.csv_file_obj)
        for cur_row in csv_dict_reader:
            category = cur_row.get("category", "").strip()
            category = category.title()
            categories_list.append(category)
        unique_categories = list(set(categories_list))
        sorted_categories = sorted(unique_categories)
        return sorted_categories
