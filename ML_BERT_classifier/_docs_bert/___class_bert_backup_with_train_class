from typing import Dict, List, Literal, Union

import torch
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset, TensorDataset
from transformers import BertForSequenceClassification, BertTokenizer

from configs.console_colors import CONSOLE_COLORS


# class TrainDataset(Dataset):
#     """Create training data-set"""
#
#     def __init__(self, texts, labels, tokenizer, max_len):
#         self.texts = texts
#         self.labels = labels
#         self.tokenizer = tokenizer
#         self.max_len = max_len
#
#     def __len__(self):
#         return len(self.texts)
#
#     def __getitem__(self, idx):
#         text = self.texts[idx]
#         label = self.labels[idx]
#         encoding = self.tokenizer(text,
#                                   truncation=True,
#                                   padding="max_length",
#                                   max_length=self.max_len,
#                                   return_tensors="pt")
#         dataset_data = {"input_ids": encoding["input_ids"].flatten(),
#                         "attention_mask": encoding["attention_mask"].flatten(),
#                         "label": torch.tensor(label, dtype=torch.long)}
#         return dataset_data


class ClassifierBERT:

    def __init__(self,
                 labels: Dict[int, str],
                 model_name: str = "bert-base-multilingual-cased",
                 cache_dir: str = None,
                 max_len: int = 64):
        """ BERT Model classifier to classify text phrases by sense categories.
        labels: dict[str: int]: e.g. {0: 'wish', 1: 'cancel', 3: 'rudeness'}
        model_name: str: Pretrained model name, 'bert-base-multilingual-cased' by default
        cache_dir: str: Pretrained model download directory when init, if differs from default one
        max_len: int: Max length in symbols of the token string, more will be cut"""

        self.labels = labels
        self.max_len = max_len
        self.train_dataset = None

        device_name = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device_name)
        green_color = CONSOLE_COLORS.BRIGHT_GREEN
        reset_color = CONSOLE_COLORS.RESET
        print(f"Device: "
              f"{green_color}{device_name.upper()}{reset_color}\n")

        self.tokenizer = BertTokenizer.from_pretrained(
            pretrained_model_name_or_path=model_name,  # org
            cache_dir=cache_dir,  # extra
            force_download=False,
            local_files_only=True,  # False by default
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
            local_files_only=True,  # False by default
            token=None,
            revision="main",
            use_safetensors=None,
            weights_only=True,
            num_labels=len(labels),
        ).to(self.device)  # Transfer pretrained model to the cur device cpu or gpu

    def create_train_dataset(
            self,
            texts_list: List[str],
            labels_list: List[int],
            truncation: bool = False,
            padding: Union[Literal["max_length", "longest"], False, None] = "max_length",
            return_tensors: Union[Literal["pt", "tf", "np"], None] = "pt"
    ) -> TensorDataset:
        """:param texts_list: list: texts in corresponding labels order
        :param labels_list: list: right labels in corresponding texts order
        :param truncation: bool: truncate text or not to self.max_len
        :param padding: "max_length" padding to the length of self.max_len,
        "longest" padding to the max length text of the batch,
        False|None - without padding
        :param return_tensors: "pt" returns PyTorch tensors !!!FOR THIS PROJECT ONLY "pt"!!!,
        "tf" returns TensorFlow tensors, "np" returns NumPy arrays,
        None returns lists"""

        # train_dataset_obj = TrainDataset(texts=texts,
        #                                  labels=labels,
        #                                  tokenizer=self.tokenizer,
        #                                  max_len=self.max_len)
        # return train_dataset_obj

        input_ids = []
        attention_masks = []
        for text in texts_list:
            encoding = self.tokenizer(text,
                                      truncation=truncation,
                                      padding=padding,
                                      max_length=self.max_len,
                                      return_tensors=return_tensors)
            input_ids.append(encoding["input_ids"])
            attention_masks.append(encoding["attention_mask"])

        input_ids = torch.cat(input_ids, dim=0)
        attention_masks = torch.cat(attention_masks, dim=0)
        labels = torch.tensor(labels_list, dtype=torch.long)

        tensor_dataset = TensorDataset(
            input_ids, attention_masks, labels)

        self.train_dataset = tensor_dataset
        return tensor_dataset

    def train(self,
              train_dataset: Union[TensorDataset, None] = None,
              max_training_epochs: int = 50,
              max_cont_100perc_epochs: int = 5,
              batch_size: int = 8,
              learning_rate: float = 5e-5):
        """Model retraining with extra training data-set
        :param train_dataset: TensorDataset: Training dataset can be passed
        or self.train_dataset will be used otherwise
        :param max_training_epochs: int: Training epochs number max limit
        :param max_cont_100perc_epochs: int: Max continuous 100% right predictions epochs
        :param batch_size: int: Batch size, depends on memory size (8, 16, 32, ...)
        :param learning_rate: float: Learning speed. The slower, the more accurate
        """

        if not train_dataset and not self.train_dataset:
            print(f"TrainDataset [ERROR]: execute method .create_train_dataset() "
                  f"before calling method .train(): "
                  f"train_dataset: {train_dataset}, "
                  f"self.train_dataset: {self.train_dataset}")
            return

        dataset = train_dataset if train_dataset else self.train_dataset
        dataloader = DataLoader(dataset=dataset,  # org
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
                                in_order=True)

        optimizer = AdamW(params=self.model.parameters(),  # org
                          lr=learning_rate,  # org
                          betas=(0.9, 0.999),
                          eps=1e-8,
                          weight_decay=1e-2,
                          amsgrad=False,
                          maximize=False,
                          foreach=None,
                          capturable=False,
                          differentiable=False,
                          fused=None)

        self.model.train()
        cont_100perc_epochs_counter = 0

        for cur_train_epoch_idx in range(max_training_epochs):
            total_loss = 0

            for batch in dataloader:
                input_ids = batch[0].to(self.device)
                attention_mask = batch[1].to(self.device)
                labels = batch[2].to(self.device)

                # If class TrainDataset(Dataset) is used
                # input_ids = batch["input_ids"].to(self.device)
                # attention_mask = batch["attention_mask"].to(self.device)
                # labels = batch["label"].to(self.device)

                outputs = self.model(input_ids=input_ids,
                                     attention_mask=attention_mask,
                                     labels=labels)
                loss = outputs.loss
                loss.backward()
                optimizer.step()
                optimizer.zero_grad()
                total_loss += loss.item()

            cur_perc_res = round((1 - total_loss / len(dataloader)) * 100)
            if cont_100perc_epochs_counter > 0 and cur_perc_res == 100:
                cont_100perc_epochs_counter += 1
            elif cont_100perc_epochs_counter == 0 and cur_perc_res == 100:
                cont_100perc_epochs_counter = 1
            else:
                cont_100perc_epochs_counter = 0
            print(f"Training Epoch: {cur_train_epoch_idx + 1} "
                  f"[Right Categories: {cur_perc_res}%] "
                  f"{cont_100perc_epochs_counter}/{max_cont_100perc_epochs}")

            if cont_100perc_epochs_counter == max_cont_100perc_epochs:
                return

    def predict(self, text: str) -> str:
        """Predict class (category, label) for given text or phrase
        text: str: Income any text or phrase to predict category for it
        Returns: str: Returns predicted category label"""
        encoding = self.tokenizer(text,
                                  truncation=False,
                                  padding="max_length",
                                  max_length=self.max_len,
                                  return_tensors="pt")
        input_ids = encoding["input_ids"].to(self.device)
        attention_mask = encoding["attention_mask"].to(self.device)

        with torch.no_grad():
            outputs = self.model(input_ids=input_ids,
                                 attention_mask=attention_mask)
            logits = outputs.logits
            prediction = torch.argmax(logits, dim=1).item()

        return self.labels[prediction]
