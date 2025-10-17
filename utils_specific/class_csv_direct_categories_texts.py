import csv
from datetime import datetime
from io import TextIOWrapper
from typing import TextIO, List, Union, Tuple


class CsvDirectCategoryText:

    def __init__(self, csv_file_obj: TextIO | TextIOWrapper):
        self.csv_file_obj = csv_file_obj
        self.csv_dict_reader = csv.DictReader(csv_file_obj)

    def get_direct_text_category_dict(
            self, reversed_direct_cat_text: bool = False
    ) -> dict[str: str]:
        text_cat_text_dict = {}
        self.csv_file_obj.seek(0)
        csv_dict_reader = csv.DictReader(self.csv_file_obj)
        for cur_row in csv_dict_reader:
            direct_category = cur_row.get("direct_category", "")
            direct_text = cur_row.get("direct_text", "")
            direct_category = str(direct_category.strip().lower())
            direct_text = str(direct_text.strip().lower())

            if direct_category and direct_text:
                if reversed_direct_cat_text:
                    text_cat_text_dict[direct_category] = direct_text
                else:
                    text_cat_text_dict[direct_text] = direct_category
            else:
                date_time = cur_row.get("date_time", "")
                print(f"Current row skipped, empty field value [ERROR]: "
                      f"direct_category: {direct_category}, "
                      f"direct_text: {direct_text}, "
                      f"date_time: {date_time}\n")
        return text_cat_text_dict

    def get_direct_text_categ_by_acc_dict(
            self, account_id: str,
            account_username: str,
            reversed_direct_cat_text: bool = False,
    ) -> dict[str: str]:
        text_cat_text_dict = {}
        self.csv_file_obj.seek(0)
        csv_dict_reader = csv.DictReader(self.csv_file_obj)
        for cur_row in csv_dict_reader:
            csv_account_id = cur_row.get("account_id", "")
            csv_account_username = cur_row.get("account_username", "")
            csv_account_id = str(csv_account_id.strip().lower())
            csv_account_username = str(csv_account_username.strip().lower())

            if (csv_account_id == account_id
                    and csv_account_username == account_username):
                direct_category = cur_row.get("direct_category", "")
                direct_text = cur_row.get("direct_text", "")
                direct_category = str(direct_category.strip().lower())
                direct_text = str(direct_text.strip().lower())

                if direct_category and direct_text:
                    if reversed_direct_cat_text:
                        text_cat_text_dict[direct_category] = direct_text
                    else:
                        text_cat_text_dict[direct_text] = direct_category
                else:
                    date_time = cur_row.get("date_time", "")
                    print(f"Current row skipped, empty field value [ERROR]: "
                          f"direct_category: {direct_category}, "
                          f"direct_text: {direct_text}, "
                          f"date_time: {date_time}\n")
        return text_cat_text_dict


    def get_direct_categories_texts_list(self) -> list[dict[str: str]]:
        direct_categories_texts_list = []
        self.csv_file_obj.seek(0)
        csv_dict_reader = csv.DictReader(self.csv_file_obj)
        for cur_row in csv_dict_reader:
            account_id = cur_row.get("account_id", "")
            account_username = cur_row.get("account_username", "")
            direct_category = cur_row.get("direct_category", "")
            direct_text = cur_row.get("direct_text", "")
            account_id = str(account_id.lower().strip())
            account_username = str(account_username.lower().strip())
            direct_category = str(direct_category.lower().strip())
            direct_text = str(direct_text.lower().strip())

            cur_direct_cat_text = {
                "account_id": account_id,
                "account_username": account_username,
                "direct_category": direct_category,
                "direct_text": direct_text}
            direct_categories_texts_list.append(cur_direct_cat_text)
        return direct_categories_texts_list

    def get_direct_categories_list_sorted(
            self, titled: bool = False
    ) -> list[str]:
        direct_categories_list = []
        self.csv_file_obj.seek(0)
        csv_dict_reader = csv.DictReader(self.csv_file_obj)
        for cur_row in csv_dict_reader:
            direct_category = cur_row.get("direct_category", "")
            direct_category = str(direct_category.strip().lower())
            direct_category = direct_category.title() if titled else direct_category

            direct_categories_list.append(direct_category)
        unique_direct_categories = list(set(direct_categories_list))
        sorted_direct_categories = sorted(unique_direct_categories)
        return sorted_direct_categories

    def get_direct_categs_by_acc_list(
            self, account_id: str,
            account_username: str,
            titled: bool = False
    ) -> list[str]:
        direct_text_cat_dict = {}
        self.csv_file_obj.seek(0)
        csv_dict_reader = csv.DictReader(self.csv_file_obj)
        for cur_row in csv_dict_reader:
            csv_account_id = cur_row.get("account_id", "")
            csv_account_username = cur_row.get("account_username", "")
            csv_account_id = str(csv_account_id.strip().lower())
            csv_account_username = str(csv_account_username.strip().lower())

            if (csv_account_id == account_id
                    and csv_account_username == account_username):
                direct_category = cur_row.get("direct_category", "")
                direct_text = cur_row.get("direct_text", "")
                direct_category = str(direct_category.strip().lower())
                direct_category = direct_category.title() if titled else direct_category
                direct_text = str(direct_text.strip().lower())

                direct_text_cat_dict[direct_text] = direct_category
        direct_categories_list = list(direct_text_cat_dict.values())
        unique_direct_categories = list(set(direct_categories_list))
        sorted_direct_categories = sorted(unique_direct_categories)
        return sorted_direct_categories

    def add_single_direct_category_text_row(
            self,
            account_id: str,
            account_username: str,
            new_direct_category: str,
            new_direct_text: str
    ) -> bool:
        csv_writer = csv.writer(self.csv_file_obj,
                                quoting=csv.QUOTE_NONNUMERIC)
        date_time_str = str(datetime.now())
        csv_writer.writerow([date_time_str,
                             account_id,
                             account_username,
                             new_direct_category,
                             new_direct_text])
        return True

    def add_multi_direct_cat_text_rows(
            self, upd_direct_category_text_data: List[Union[List, Tuple]]
    ) -> bool:
        csv_writer = csv.writer(self.csv_file_obj,
                                quoting=csv.QUOTE_NONNUMERIC)
        csv_writer.writerows(upd_direct_category_text_data)
        return True

    def write_new_direct_category_text_csv(
            self, direct_category_text_dict: dict) -> bool:
        csv_writer = csv.writer(self.csv_file_obj,
                                quoting=csv.QUOTE_NONNUMERIC)
        csv_writer.writerow(["date_time",
                             "account_id",
                             "account_username",
                             "direct_category",
                             "direct_text"])
        date_time_str = str(datetime.now())
        for key, value in direct_category_text_dict.items():
            csv_writer.writerow([date_time_str, key, value])
        return True
