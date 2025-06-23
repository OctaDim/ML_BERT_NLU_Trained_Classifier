from typing import List

import torch
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import BertForSequenceClassification, BertTokenizer

from configs.settings import BERT_TRAIN_OPTIONS


class ClassifierBERT:

    def __init__(self,
                 labels: dict[str: int],
                 model_name: str = "bert-base-multilingual-cased",
                 cache_dir: str = None,
                 max_len: int = 64):
        """ BERT Model classifier to classify text phrases by sense categories.
        labels: dict[str: int]:
        model_name: str: Название предобученной модели (по умолчанию 'bert-base-multilingual-cased').
        num_labels: int: Количество классов (2 для 'да'/'нет').
        max_len: int: Максимальная длина токенизированного текста.
        cache_dir: str: Директория куда будет скачиваться (кэшироваться) модель при первой инициализации
        """

        self.labels = labels
        self.max_len = max_len

        cuda_avail_flag = torch.cuda.is_available()
        self.device = torch.device("cuda" if cuda_avail_flag else "cpu")
        self.tokenizer = BertTokenizer.from_pretrained(
            pretrained_model_name_or_path=model_name,  # org
            cache_dir=cache_dir,  # extra
            force_download=False,
            local_files_only=True,  # try
            # local_files_only=False,  # org
            token=None,
            revision="main",
            trust_remote_code=False,
        )

        self.model = BertForSequenceClassification.from_pretrained(
            pretrained_model_name_or_path=model_name,  # org
            cache_dir=cache_dir,  # extra
            config=None,
            ignore_mismatched_sizes=False,
            force_download=False,
            local_files_only=True,  # try
            # local_files_only=False,  # org
            token=None,
            revision="main",
            use_safetensors=None,
            weights_only=True,
            num_labels=len(labels),
        ).to(self.device)

    def train(self, texts: List[str],
              labels: List[int],
              batch_size: int = 8,
              max_epochs: int = 15,
              learning_rate: float = 5e-5):
        """Дообучение модели на своих данных.
        texts (List[str]): Список текстов для обучения.
        labels (List[int]): Список меток (0 = 'нет', 1 = 'да').
        batch_size (int): Размер батча.
        epochs (int): Количество эпох.
        learning_rate (float): Скорость обучения.
        """
        dataset = self._create_dataset(texts, labels)
        dataloader = DataLoader(
            dataset=dataset,  # org
            batch_size=batch_size,  # org
            shuffle=True,  # org
            sampler=None,
            batch_sampler=None,
            num_workers=0,
            collate_fn=None,
            pin_memory=False,
            drop_last=False,
            timeout=0,
            worker_init_fn=None,
            multiprocessing_context=None,
            generator=None,
            prefetch_factor=None,
            persistent_workers=False,
            pin_memory_device="",
            in_order=True,
        )

        optimizer = AdamW(
            params=self.model.parameters(),  # org
            lr=learning_rate,  # org
            betas=(0.9, 0.999),
            eps=1e-8,
            weight_decay=1e-2,
            amsgrad=False,
            maximize=False,
            foreach=None,
            capturable=False,
            differentiable=False,
            fused=None,
        )

        self.model.train()
        cont_100perc_counter = 0
        for cur_epoch in range(max_epochs):
            total_loss = 0
            for batch in dataloader:
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                labels = batch["label"].to(self.device)

                outputs = self.model(input_ids=input_ids,
                                     attention_mask=attention_mask,
                                     labels=labels, )
                loss = outputs.loss
                loss.backward()
                optimizer.step()
                optimizer.zero_grad()
                total_loss += loss.item()

            cur_perc_res = round((1 - total_loss / len(dataloader)) * 100)
            if cont_100perc_counter > 0 and cur_perc_res == 100:
                cont_100perc_counter += 1
            elif cont_100perc_counter == 0 and cur_perc_res == 100:
                cont_100perc_counter = 1
            else:
                cont_100perc_counter = 0

            limit_100perc_epochs = BERT_TRAIN_OPTIONS.CONTINUOUS_100PERC_EPOCHS
            print(f"Эпоха обучения: {cur_epoch + 1} "
                  f"[верные ответы: {cur_perc_res}%] "
                  f"{cont_100perc_counter}/{limit_100perc_epochs}")

            if cont_100perc_counter == limit_100perc_epochs:
                return

    def predict(self, text: str) -> str:
        """Предсказание метки ('да'/'нет') для текста
        Args: text (str): Входной текст
        Returns: str: 'да' или 'нет'"""
        encoding = self.tokenizer(text,
                                  truncation=True,
                                  padding="max_length",
                                  max_length=self.max_len,
                                  return_tensors="pt", )
        input_ids = encoding["input_ids"].to(self.device)
        attention_mask = encoding["attention_mask"].to(self.device)

        with torch.no_grad():
            outputs = self.model(input_ids=input_ids,
                                 attention_mask=attention_mask)
            logits = outputs.logits
            prediction = torch.argmax(logits, dim=1).item()

        return self.labels[prediction]

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
                encoding = self.tokenizer(text,
                                          truncation=True,
                                          padding="max_length",
                                          max_length=self.max_len,
                                          return_tensors="pt", )
                return {
                    "input_ids": encoding["input_ids"].flatten(),
                    "attention_mask": encoding["attention_mask"].flatten(),
                    "label": torch.tensor(label, dtype=torch.long),
                }


        return YesNoDataset(texts=texts,
                            labels=labels,
                            tokenizer=self.tokenizer,
                            max_len=self.max_len)
