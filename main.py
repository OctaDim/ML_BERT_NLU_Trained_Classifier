from ML_BERT.bert_init import BERTClassifierYesNo
from configs.console_colors import CONSOLE_COLORS
from configs.settings import BASE_DIR, BERT_MODEL_NAMES, BERT_OPTIONS
from test_phrases.labels_categories import labels
from test_phrases.test_phrases import test_phrases
from train_data_sets.train_data_sets import common_train_dataset
from utils_common.normalized_path import get_full_dir_normal_path


bert_model_full_path = get_full_dir_normal_path(
    [BASE_DIR, BERT_OPTIONS.BERT_MODELS_DOWNLOAD_PATH])

if __name__ == "__main__":
    print("Инициализация модели:")
    bert_model_instance = BERTClassifierYesNo(
        labels=labels,
        model_name=BERT_MODEL_NAMES.BERT_BASE_MULTILINGUAL_CASED,
        cache_dir=bert_model_full_path,
        max_len=64,
    )
    print()

    categories_lens = [len(label) for label in labels.values()]
    category_max_len = max(categories_lens)
    all_phrases_tot = len(test_phrases)
    green_color = CONSOLE_COLORS.BRIGHT_GREEN
    red_color = CONSOLE_COLORS.BRIGHT_RED
    reset_color = CONSOLE_COLORS.RESET

    print("Результаты предсказаний БЕЗ ОБУЧЕНИЯ модели:")
    right_answers_tot = 0
    counter = 0
    for cur_test_phrase, cur_test_label in test_phrases.items():
        counter += 1
        pred_category = bert_model_instance.predict(cur_test_phrase)
        if pred_category == labels.get(cur_test_label):
            result_str = f"{green_color}[OK]{reset_color}"
            right_answers_tot += 1
        else:
            result_str = f"{red_color}[ERROR]{reset_color}"
        category_str = f"{pred_category} -".ljust(
            category_max_len + 2, "-")
        order_str = f"{counter}/{all_phrases_tot}".ljust(9)
        print(f"{order_str} {category_str} {cur_test_phrase} {result_str}")
    percent = round((right_answers_tot / all_phrases_tot) * 100)
    print("#"*75)
    print(f"Правильные ответы: {right_answers_tot}/{all_phrases_tot} "
          f"[{percent} %]\n\n")

    print("Данные для тренировки и дообучения модели:")
    train_dataset_unique = {}
    for cur_test_phrase, cur_test_label in common_train_dataset.items():
        train_dataset_unique[cur_test_phrase] = cur_test_label
    train_phrases = list(train_dataset_unique.keys())
    train_labels = list(train_dataset_unique.values())
    print(f"train_phrases: {train_phrases}\n"
          f"train_labels: {train_labels}\n")

    print("Дообучение модели:")
    bert_model_instance.train(
        texts=train_phrases,
        labels=train_labels,
        max_epochs=BERT_OPTIONS.BERT_TRAIN_MAX_EPOCHS_NUMBER,
        batch_size=BERT_OPTIONS.BERT_TRAIN_BATCH_SUZE,
        learning_rate=BERT_OPTIONS.BERT_TRAIN_LEARNING_RATE)
    print()

    print("Результаты предсказаний после ДООБУЧЕНИЯ модели:")
    right_answers_tot = 0
    counter = 0
    for cur_test_phrase, cur_test_label in test_phrases.items():
        counter += 1
        pred_category = bert_model_instance.predict(cur_test_phrase)
        if pred_category == labels.get(cur_test_label):
            result_str = f"{green_color}[OK]{reset_color}"
            right_answers_tot += 1
        else:
            result_str = f"{red_color}[ERROR]{reset_color}"
        category_str = f"{pred_category} -".ljust(
            category_max_len + 2, "-")
        order_str = f"{counter}/{all_phrases_tot}".ljust(9)
        print(f"{order_str} {category_str} {cur_test_phrase} {result_str}")
    percent = round((right_answers_tot / all_phrases_tot) * 100)
    print("#"*75)
    print(f"Правильные ответы: {right_answers_tot}/{all_phrases_tot} "
          f"[{percent} %]\n\n")
