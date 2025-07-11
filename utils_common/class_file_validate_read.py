import csv
import io
import re
from io import BytesIO, StringIO
from typing import BinaryIO, List, Literal, Union

import pandas
from fastapi import UploadFile


class FileValidateRead:

    def __init__(self, file: UploadFile):
        self.file = file
        self.file_content = None
        self.signature_xlsx = b"\x50\x4B\x03\x04"  # XLSX (ZIP archive)
        self.signature_xls = b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1"  # XLS (OLE Compound File)

    @staticmethod
    def format_list_data(orig_list: List[List[str]]):
        formatted_list = [
            [str(value).strip().lower() for value in sublist]
            for sublist in orig_list]
        return formatted_list

    async def async_reset_and_read_file(self):
        await self.file.seek(0)
        self.file_content = await self.file.read()
        return self.file_content

    async def validate_content_excel(self,
                                     validate_xlsx: bool = True,
                                     validate_xls: bool = True) -> bool:
        file_content = await self.async_reset_and_read_file()
        is_valid_xls_xlsx_file = any([
            validate_xlsx and file_content.startswith(self.signature_xlsx),
            validate_xls and file_content.startswith(self.signature_xls),
        ])
        return is_valid_xls_xlsx_file

    async def validate_content_txt(self) -> bool:
        await self.async_reset_and_read_file()
        try:
            self.file_content.decode("utf-8")
            return True
        except UnicodeDecodeError:
            return False

    async def validate_content_csv(self) -> bool:
        await self.async_reset_and_read_file()
        try:
            content_str = self.file_content.decode('utf-8')
            str_io_buffer = StringIO(content_str)

            reader = csv.reader(str_io_buffer)  # Is valid csv file
            try:
                next(reader)  # Is valid csv file, not empty
                return True
            except StopIteration:
                return True  # Is valid csv file, but empty
        except (UnicodeDecodeError, csv.Error):
            return False

    async def read_file_excel(self, convert_to_str: bool = True) -> list:
        await self.async_reset_and_read_file()
        bytes_io_buffer = BytesIO(self.file_content)
        data_frame = pandas.read_excel(bytes_io_buffer,
                                       header=None,
                                       keep_default_na=False, )
        data_frame = data_frame.astype(str) if convert_to_str else data_frame
        data_list = data_frame.values.tolist()
        formatted_list = self.format_list_data(orig_list=data_list)
        return formatted_list


    async def read_file_txt(self, convert_to_str: bool = True) -> list:
        await self.async_reset_and_read_file()
        monolith_str = self.file_content.decode("utf-8")
        file_rows = monolith_str.splitlines()
        data_list = []
        for cur_row in file_rows:
            line_str_list = re.findall(r'"(.*?)"', cur_row)
            if not line_str_list:
                line_str_list = re.findall(r"'(.*?)'", cur_row)
            if not line_str_list:
                line_str_list = cur_row.split(",")
                line_str_list = [elem.strip() for elem in line_str_list]
            if convert_to_str:
                line_str_list = [str(elem) for elem in line_str_list]
            data_list.append(line_str_list)
        formatted_list = self.format_list_data(orig_list=data_list)
        return formatted_list

    async def read_file_csv(self,
                            skip_first_row: bool = True,
                            quote_char: Literal["'", '"'] = '"') -> list:
        await self.async_reset_and_read_file()
        content_str = self.file_content.decode("utf-8")
        str_io_buffer = io.StringIO(content_str)
        csv_reader = csv.reader(str_io_buffer,
                                skipinitialspace=True,
                                quotechar=quote_char, )
        data_list = []
        monolith_str = self.file_content.decode("utf-8")
        if monolith_str.splitlines():
            first_row_str = monolith_str.splitlines()[0]
            if skip_first_row and quote_char not in first_row_str:
                next(csv_reader)
            else:
                first_csv_row = next(csv_reader)
                first_row_list = [str(value) for value in first_csv_row]
                data_list.append(first_row_list)

        for cur_csv_row in csv_reader:
            cur_row_list = [str(value) for value in cur_csv_row]
            data_list.append(cur_row_list)
        formatted_list = self.format_list_data(orig_list=data_list)
        return formatted_list
