import torch
from transformers import BertTokenizer, BertForSequenceClassification
# from transformers.optimization import AdamW
from torch.optim import AdamW
from torch.utils.data import Dataset, DataLoader
from typing import List, Dict, Optional


class YesNoBERTClassifier:

    def __init__(
            self,
            model_name: str = "bert-base-multilingual-cased",
            num_labels: int = 2,
            max_len: int = 64,
    ):
        """Инициализация модели BERT для классификации 'да'/'нет'.

        Args:
            model_name (str): Название предобученной модели (по умолчанию 'bert-base-multilingual-cased').
            num_labels (int): Количество классов (2 для 'да'/'нет').
            max_len (int): Максимальная длина токенизированного текста.
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertForSequenceClassification.from_pretrained(model_name, num_labels=num_labels).to(self.device)
        self.max_len = max_len
        self.labels = {0: "нет", 1: "да"}

    def train(
            self,
            texts: List[str],
            labels: List[int],
            batch_size: int = 8,
            epochs: int = 3,
            learning_rate: float = 5e-5,
    ):
        """Дообучение модели на своих данных.

        Args:
            texts (List[str]): Список текстов для обучения.
            labels (List[int]): Список меток (0 = 'нет', 1 = 'да').
            batch_size (int): Размер батча.
            epochs (int): Количество эпох.
            learning_rate (float): Скорость обучения.
        """
        dataset = self._create_dataset(texts, labels)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        optimizer = AdamW(self.model.parameters(), lr=learning_rate)

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
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
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


        return YesNoDataset(texts, labels, self.tokenizer, self.max_len)


# Пример использования
if __name__ == "__main__":
    print("Инициализация модели")
    classifier = YesNoBERTClassifier()

    data_set = {
        "да, согласен": 1,
        "приду": 1,
        "хочу": 1,
        "да нет, наверное": 0,       # Неуверенный отказ
        "конечно, нет": 0,           # Противоречие с упором на "нет"
        "да, но только если...": 1,  # Условное согласие
        "в конечном итоге да": 1,
        "ответ отрицательный, нет": 0,
        "но я всё же да": 1,
        "хотя нет, передумал": 0,
        "да, конечно": 1,
        "не отказываюсь, да": 1,
        "да": 1,
        "конечно": 1,
        "ага": 1,
        "угу": 1,
        "ок": 1,
        "окей": 1,
        "хорошо": 1,
        "согласен": 1,
        "согласна": 1,
        "безусловно": 1,
        "естественно": 1,
        "разумеется": 1,
        "без проблем": 1,
        "да, пожалуйста": 1,
        "конечно, да": 1,
        "да, уверен": 1,
        "да, точно": 1,
        "подтверждаю": 1,
        "всё верно": 1,
        "именно так": 1,
        "несомненно": 1,
        "абсолютно": 1,
        "с радостью": 1,
        "легко": 1,
        "да, хоть сейчас": 1,
        "нет": 0,
        "неа": 0,
        "не": 0,
        "никак нет": 0,
        "ни за что": 0,
        "отказываюсь": 0,
        "не согласен": 0,
        "не согласна": 0,
        "нет, спасибо": 0,
        "не хочу": 0,
        "не буду": 0,
        "не надо": 0,
        "нет, не надо": 0,
        "отнюдь": 0,
        "ни в коем случае": 0,
        "нет, ни за что": 0,
        "даже не думай": 0,
        "забудь": 0,
        "нет, никогда": 0,
        "неа, не стоит": 0,
        "отказ": 0,
        "не готов": 0,
        "не могу": 0,
        "нет, да ладно": 1,
        "не то чтобы нет": 1,
        "я не против": 1,
        "не скажу что нет": 1,
        "не могу отказаться": 1,
        "не то чтобы я отказался": 1,
        "нет, но если надо — да": 1,
        "не хочу, но да": 1,
        "не уверен, но да": 1,
        "не знаю, но наверное да": 1,
        "не думаю, что нет": 1,
        "я бы не сказал нет": 1,
        "не откажусь": 1,
        "не против": 1,
        "не возражаю": 1,
        "не могу сказать нет": 1,
        "не отказываюсь": 1,
        "нет, но да": 1,
        "не совсем нет": 1,
        "не отказался бы": 1,
        "да нет": 0,
        "да, но нет": 0,
        "конечно нет": 0,
        "да, не надо": 0,
        "да, только не сейчас": 0,
        "да, но я передумал": 0,
        "да, но не хочу": 0,
        "я бы сказал да, но нет": 0,
        "да, но не могу": 0,
        "да, но не стоит": 0,
        "хотел бы, но нет": 0,
        "да, но лучше не надо": 0,
        "да, но не сегодня": 0,
        "да, но не для меня": 0,
        "да, но не уверен": 0,
        "да, но не сейчас": 0,
        "да, но не в этот раз": 0,
        "да, но не тут": 0,
        "да, но не так": 0,
        "да, но не совсем": 0,
        "возможно": 1,
        "наверное": 1,
        "может быть": 1,
        "подумаю": 0,
        "посмотрим": 0,
        "не знаю": 0,
        "зависит": 0,
        "спросите позже": 0,
        "не сейчас": 0,
        "позже": 0,
        "ну конечно, да": 1,
        "ага, как же": 0,
        "да, прямо сейчас": 0,
        "конечно, нет проблем": 0,
        "ещё чего": 0,
        "мечтай": 0,
        "скорее да, чем нет": 1,
        "скорее нет, чем да": 0,
        "вряд ли": 0,
        "очень сомневаюсь": 0,
        "без сомнений": 1

    }

    train_texts = [key for key in data_set.keys()]
    print("train_texts", train_texts)

    train_labels = [label for label in data_set.values()]
    print("train_labels", train_labels)

    # print("Пример данных для обучения (можно заменить на свои)")
    # train_texts = ["да", "конечно", "нет", "не хочу", "да, согласен", "никак нет"]
    # train_labels = [1, 1, 0, 0, 1, 0]  # 1 = 'да', 0 = 'нет'

    # Дообучение модели (опционально)
    print("Дообучение модели...")
    classifier.train(train_texts, train_labels, epochs=3)

    print("Тестирование")
    test_phrases = [
        "да, конечно",
        "нет, не хочу",
        "не отказываюсь, да",
        "да нет, наверное",
        "конечно, согласен",
        "нет, я не для того отказывался, да",
        "нет, я приду",
        "да, я отказываюсь",
        "да, я не хочу",
        "нет, я не отказываюсь",

    ]

    print("Результаты предсказаний:")
    for phrase in test_phrases:
        print(f"Фраза: '{phrase}' -> Ответ: {classifier.predict(phrase)}")
