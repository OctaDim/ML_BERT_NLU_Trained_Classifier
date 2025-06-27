from configs.settings import BASE_DIR, BERT_OPTIONS
from utils_common.normalized_path import get_full_file_normal_path
from utils_specific.class_csv_texts_labels import CsvTextLabel


text_labels_dir = BERT_OPTIONS.BERT_INITIAL_DATASET_CSV_PATH
text_labels_file = BERT_OPTIONS.BERT_TEXT_LABEL_CSV_NAME
csv_normal_file_path = get_full_file_normal_path(
    all_dir_str_parts=[BASE_DIR, text_labels_dir],
    file_name_with_ext=text_labels_file)

with open(csv_normal_file_path, mode="r", encoding="utf-8") as csv_file:
    csf_bert = CsvTextLabel(csv_file_obj=csv_file)
    text_dict = csf_bert.get_text_label_dict()
    print(text_dict)

    text_lab_dict = csf_bert.get_text_label_datasets()
    print(text_lab_dict)
