# from transformers.optimization import AdamW
from typing import List

import torch
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import BertForSequenceClassification, BertTokenizer


class BERTClassifierYesNo:

    def __init__(
            self,
            model_name: str = "bert-base-multilingual-cased",
            num_labels: int = 2,
            max_len: int = 64,
            cache_dir: str = None,
    ):
        """Инициализация модели ML_BERT для классификации 'да'/'нет'.
        model_name: str: Название предобученной модели (по умолчанию 'bert-base-multilingual-cased').
        num_labels: int: Количество классов (2 для 'да'/'нет').
        max_len: int: Максимальная длина токенизированного текста.
        cache_dir: str: Директория куда будет скачиваться (кэшироваться) модель при первой инициализации
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = BertTokenizer.from_pretrained(
            pretrained_model_name_or_path=model_name,
            cache_dir=cache_dir,
        )

        self.model = BertForSequenceClassification.from_pretrained(
            pretrained_model_name_or_path=model_name,
            num_labels=num_labels,
        ).to(self.device)

        self.max_len = max_len
        self.labels = {0: "нет", 1: "да"}

    def train(
            self,
            texts: List[str],
            labels: List[int],
            batch_size: int = 8,
            epochs: int = 15,
            learning_rate: float = 5e-5,
    ):
        """Дообучение модели на своих данных.
        texts (List[str]): Список текстов для обучения.
        labels (List[int]): Список меток (0 = 'нет', 1 = 'да').
        batch_size (int): Размер батча.
        epochs (int): Количество эпох.
        learning_rate (float): Скорость обучения.
        """
        dataset = self._create_dataset(texts, labels)
        dataloader = DataLoader(
            dataset=dataset,
            batch_size=batch_size,
            shuffle=True,
        )

        optimizer = AdamW(
            params=self.model.parameters(),
            lr=learning_rate,
        )

        self.model.train()
        for epoch in range(epochs):
            total_loss = 0
            for batch in dataloader:
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                labels = batch["label"].to(self.device)

                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels,
                )
                loss = outputs.loss
                loss.backward()
                optimizer.step()
                optimizer.zero_grad()
                total_loss += loss.item()

            print(f"Эпоха {epoch + 1}, Loss: {total_loss / len(dataloader):.4f}")

    def predict(self, text: str) -> str:
        """Предсказание метки ('да'/'нет') для текста.

        Args:
            text (str): Входной текст.

        Returns:
            str: 'да' или 'нет'.
        """
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=self.max_len,
            return_tensors="pt",
        )
        input_ids = encoding["input_ids"].to(self.device)
        attention_mask = encoding["attention_mask"].to(self.device)

        with torch.no_grad():
            outputs = self.model(input_ids=input_ids,
                                 attention_mask=attention_mask)
            logits = outputs.logits
            pred = torch.argmax(logits, dim=1).item()

        return self.labels[pred]

    def _create_dataset(self, texts: List[str], labels: List[int]) -> Dataset:
        """Создание датасета для обучения."""


        class YesNoDataset(Dataset):

            def __init__(self, texts, labels, tokenizer, max_len):
                self.texts = texts
                self.labels = labels
                self.tokenizer = tokenizer
                self.max_len = max_len

            def __len__(self):
                return len(self.texts)

            def __getitem__(self, idx):
                text = self.texts[idx]
                label = self.labels[idx]
                encoding = self.tokenizer(
                    text,
                    truncation=True,
                    padding="max_length",
                    max_length=self.max_len,
                    return_tensors="pt",
                )
                return {
                    "input_ids": encoding["input_ids"].flatten(),
                    "attention_mask": encoding["attention_mask"].flatten(),
                    "label": torch.tensor(label, dtype=torch.long),
                }


        return YesNoDataset(texts=texts,
                            labels=labels,
                            tokenizer=self.tokenizer,
                            max_len=self.max_len)
