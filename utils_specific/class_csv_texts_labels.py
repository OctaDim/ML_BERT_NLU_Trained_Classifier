import csv
from datetime import datetime
from io import TextIOWrapper
from typing import TextIO


class CsvTextLabel:

    def __init__(self, csv_file_obj: TextIO | TextIOWrapper):
        self.csv_file_obj = csv_file_obj

    def get_text_label_dict(self) -> dict[str: int]:
        train_data_set = {}
        self.csv_file_obj.seek(0)
        csv_dict_reader = csv.DictReader(self.csv_file_obj)
        for cur_row in csv_dict_reader:
            text = cur_row.get("text", "").strip().lower()
            label = cur_row.get("label", "").strip().lower()
            if text and label is not None:
                train_data_set[text] = int(label)
            else:
                date_time = cur_row.get("date_time", "")
                print(f"Current row skipped, empty field value [ERROR]: "
                      f"text: {text}, label: {label}, "
                      f"date_time: {date_time}\n")
        return train_data_set

    def get_texts_list_unique(self) -> list[str]:
        text_lab_unique_dict: dict = self.get_text_label_dict()
        texts_list = list(text_lab_unique_dict.keys())
        return texts_list

    def get_labels_list_unique(self) -> list[int]:
        text_lab_unique_dict: dict = self.get_text_label_dict()
        labels_list = [int(lab) for lab in text_lab_unique_dict.values()]
        return labels_list

    def add_new_text_label_row(
            self, new_text: str, new_label: int) -> bool:
        csv_writer = csv.writer(self.csv_file_obj,
                                quoting=csv.QUOTE_NONNUMERIC)
        date_time_str = str(datetime.now())
        csv_writer.writerow([date_time_str, new_label, new_text])
        return True
