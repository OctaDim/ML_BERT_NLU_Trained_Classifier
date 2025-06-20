# from transformers.optimization import AdamW
# from typing import List
# import torch
# from torch.optim import AdamW
# from torch.utils.data import DataLoader, Dataset
# from transformers import BertForSequenceClassification, BertTokenizer
# from test_phrases.test_phrases_yes_no import test_phrases_yes_no
# from train_data_sets.data_set_yes_no import train_dataset_yes_no
from ML_BERT.bert_init import BERTClassifierYesNo
from configs.settings import BERT_OPTIONS
from test_phrases.test_phrases_yes_no import test_phrases_yes_no
from train_data_sets.data_set_yes_no import train_dataset_yes_no
from train_data_sets.update_data_set_yes_no import update_train_dataset_yes_no


if __name__ == "__main__":
    print("Инициализация модели:")
    bert_model_instance = BERTClassifierYesNo()
    print()

    print("Результаты предсказаний без обучения модели вообще:")
    for cur_phrase in test_phrases_yes_no:
        category = bert_model_instance.predict(cur_phrase)
        category = f"{category} " if len(category) == 2 else category
        print(f"{category} = {cur_phrase}")
    print()

    print("Данные для первоначального обучения модели:")
    train_phrases = [phrase for phrase in train_dataset_yes_no.keys()]
    print(f"train_phrases: {train_phrases}")

    train_labels = [label for label in train_dataset_yes_no.values()]
    print(f"train_labels: {train_labels}\n")

    print("Первоначальное обучение модели:")
    bert_model_instance.train(
        texts=train_phrases,
        labels=train_labels,
        epochs=BERT_OPTIONS.BERT_TRAIN_EPOCHS_NUMBER,
        batch_size=BERT_OPTIONS.BERT_TRAIN_BATCH_SUZE,
        learning_rate=BERT_OPTIONS.BERT_TRAIN_LEARNING_RATE)
    print()

    print("Результаты предсказаний после первоначального обучения модели:")
    for cur_phrase in test_phrases_yes_no:
        category = bert_model_instance.predict(cur_phrase)
        category = f"{category} " if len(category) == 2 else category
        print(f"{category} = {cur_phrase}")
    print()

    print("Данные для дополнительного дообучения модели:")
    extra_phrases = [phrase for phrase in update_train_dataset_yes_no.keys()]
    print(f"extra_phrases: {extra_phrases}")

    extra_labels = [label for label in update_train_dataset_yes_no.values()]
    print(f"extra_labels: {extra_labels}\n")

    train_phrases.extend(extra_phrases)
    train_labels.extend(extra_labels)

    print("Дополнительное дообучение модели:")
    bert_model_instance.train(
        texts=train_phrases,
        labels=train_labels,
        epochs=BERT_OPTIONS.BERT_TRAIN_EPOCHS_NUMBER,
        batch_size=BERT_OPTIONS.BERT_TRAIN_BATCH_SUZE,
        learning_rate=BERT_OPTIONS.BERT_TRAIN_LEARNING_RATE)
    print()

    print("Результаты предсказаний после дополнительного обучения модели:")
    for cur_phrase in test_phrases_yes_no:
        category = bert_model_instance.predict(cur_phrase)
        category = f"{category} " if len(category) == 2 else category
        print(f"{category} = {cur_phrase}")
    print()
