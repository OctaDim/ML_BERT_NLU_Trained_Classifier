import csv
from io import TextIOWrapper
from typing import TextIO


class CsvTextLabel:

    def __init__(self, csv_file_obj: TextIO | TextIOWrapper):
        self.csv_file_obj = csv_file_obj
        self.csv_dict_reader = csv.DictReader(csv_file_obj)

    def get_texts_labels_dict(self) -> dict[str: int]:
        train_data_set = {}
        self.csv_file_obj.seek(0)
        csv_dict_reader = csv.DictReader(self.csv_file_obj)
        for cur_row in csv_dict_reader:
            text = cur_row.get("text", "").strip().lower()
            label = cur_row.get("label", "").strip().lower()
            if text and label:
                train_data_set[text] = label
            else:
                date_time = cur_row.get("date_time", "")
                print(f"Current row skipped, empty field value [ERROR]: "
                      f"text: {text}, label: {label}, "
                      f"date_time: {date_time}\n")
        return train_data_set

    def get_texts_labels_train_datasets(self) -> dict[str: list, str: list]:
        labels_list = []
        texts_list = []
        self.csv_file_obj.seek(0)
        csv_dict_reader = csv.DictReader(self.csv_file_obj)
        for cur_row in csv_dict_reader:
            text = cur_row.get("text", "").strip().lower()
            label = cur_row.get("label", "").strip().lower()
            if text and label:
                texts_list.append(text)
                labels_list.append(label)
            else:
                date_time = cur_row.get("date_time", "")
                print(f"Current row skipped, empty field value [ERROR]: "
                      f"text: {text}, label: {label}, "
                      f"date_time: {date_time}\n")
        train_data_sets = {"texts": texts_list, "labels": labels_list}
        return train_data_sets
