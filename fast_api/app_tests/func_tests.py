from ML_BERT_classifier.init_bert import bert_model_instance
from configs.console_colors import CONSOLE_COLORS
from test_phrases.test_phrases import test_phrases
from train_data_sets.test_train_data import test_labels_categories


def test_group_prediction():
    print("#" * 100)
    all_categories_lens = [len(cat) for cat in test_labels_categories.values()]
    categories_max_len = max(all_categories_lens)
    all_phrases_tot = len(test_phrases)

    green_color = CONSOLE_COLORS.BRIGHT_GREEN
    red_color = CONSOLE_COLORS.BRIGHT_RED
    reset_color = CONSOLE_COLORS.RESET

    right_categories_tot = 0
    counter = 0
    for cur_text, cur_test_label in test_phrases.items():
        counter += 1
        predicted_category = bert_model_instance.predict(cur_text)
        if predicted_category == test_labels_categories.get(cur_test_label):
            result_str = f"{green_color}[OK]{reset_color}"
            right_categories_tot += 1
        else:
            result_str = f"{red_color}[ERROR]{reset_color}"
        category_str = f"{predicted_category} -".ljust(
            categories_max_len + 2, "-")
        order_str = f"{counter}/{all_phrases_tot}".ljust(9)
        print(f"{order_str} {category_str} {cur_text} {result_str}")
    accuracy = round((right_categories_tot / all_phrases_tot) * 100)
    print("#" * 100)
    print(f"Right Categories: {right_categories_tot}/{all_phrases_tot} "
          f"[{accuracy} %]\n")
