from configs.settings import BASE_DIR, BERT_OPTIONS
from utils_common.normalized_path import get_full_file_normal_path
from utils_specific.class_csv_labels_categories import CsvLabelCategory


labels_categories_dir = BERT_OPTIONS.BERT_INITIAL_DATASET_CSV_PATH
labels_categories_file = BERT_OPTIONS.BERT_LABEL_CATEGORY_CSV_NAME
csv_normal_file_path = get_full_file_normal_path(
    all_dir_str_parts=[BASE_DIR, labels_categories_dir],
    file_name_with_ext=labels_categories_file)

with open(csv_normal_file_path, mode="r", encoding="utf-8") as csv_file:
    csf_bert = CsvLabelCategory(csv_file_obj=csv_file)
    cat_list = csf_bert.get_categories_list_sorted()
    print(cat_list)

    cat_dict = csf_bert.get_label_category_dict()
    print(cat_dict)
