import csv
from datetime import datetime
from io import TextIOWrapper
from typing import TextIO, List, Dict, Union, Tuple


class CsvTextLabel:

    def __init__(self, csv_file_obj: TextIO | TextIOWrapper):
        self.csv_file_obj = csv_file_obj

    def get_text_label_dict(
            self,
            reversed_label_text_dict: bool = False
    ) -> dict[str, int] | dict[int, str]:
        text_lab_text_dict = {}
        self.csv_file_obj.seek(0)
        csv_dict_reader = csv.DictReader(self.csv_file_obj)
        for cur_row in csv_dict_reader:
            text = str(cur_row.get("text", "").strip().lower())
            label = int(cur_row.get("label", "").strip().lower())
            if text and (label is not None and label != ""):  # Not if not: label can be zero!!!
                if reversed_label_text_dict:
                    text_lab_text_dict[label] = text
                else:
                    text_lab_text_dict[text] = label
            else:
                date_time = cur_row.get("date_time", "")
                print(f"Current row skipped, empty field value [ERROR]: "
                      f"text: {text}, label: {label}, time: {date_time}\n")
        return text_lab_text_dict

    def get_label_text_dicts_list(self) -> List[Dict[str, int | str]]:
        """Returns list of dicts with label_index (int) and text (str)"""
        self.csv_file_obj.seek(0)
        csv_dict_reader = csv.DictReader(self.csv_file_obj)
        csv_lab_text_list = []
        for cur_row in csv_dict_reader:
            text = str(cur_row.get("text", "").strip().lower())
            label = int(cur_row.get("label", "").strip().lower())
            if text and (label is not None and label != ""):  # Not if not: label can be zero!!!
                cur_lab_text_dict = {"text": text,
                                     "label_index": label}
                csv_lab_text_list.append(cur_lab_text_dict)
            else:
                date_time = cur_row.get("date_time", "")
                print(f"Current row skipped, empty field value [ERROR]: "
                      f"text: {text}, label: {label}, date_time: {date_time}\n")
        return csv_lab_text_list

    def get_texts_list_unique(self) -> list[str]:
        text_lab_unique_dict: dict = self.get_text_label_dict()
        texts_list = list(text_lab_unique_dict.keys())
        return texts_list

    def get_labels_list_unique(self) -> list[int]:
        text_lab_unique_dict: dict = self.get_text_label_dict()
        labels_list = [int(lab) for lab in text_lab_unique_dict.values()]
        return labels_list

    def add_single_text_label_row(
            self, new_text: str, new_label: int) -> bool:
        csv_writer = csv.writer(self.csv_file_obj,
                                quoting=csv.QUOTE_NONNUMERIC)
        date_time_str = str(datetime.now())
        csv_writer.writerow([date_time_str, new_label, new_text])
        return True

    def add_multi_text_label_rows(
            self, upd_text_label_data: List[Union[List, Tuple]]
    ) -> bool:
        csv_writer = csv.writer(self.csv_file_obj,
                                quoting=csv.QUOTE_NONNUMERIC)
        csv_writer.writerows(upd_text_label_data)
        return True

    def write_new_text_label_csv(
            self, text_label_dict: dict) -> bool:
        csv_writer = csv.writer(self.csv_file_obj,
                                quoting=csv.QUOTE_NONNUMERIC)
        csv_writer.writerow(["date_time", "label", "text"])
        date_time_str = str(datetime.now())
        for key, value in text_label_dict.items():
            csv_writer.writerow([date_time_str, key, value])
        return True
