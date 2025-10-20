import os
from datetime import datetime, timedelta
from os import PathLike
from typing import Dict, List, Literal, Union

import torch
from torch.optim import AdamW
from torch.utils.data import DataLoader, TensorDataset
from transformers import BertForSequenceClassification, BertTokenizer

from configs.console_colors import CONSOLE_COLORS
from configs.settings import REDIS_OPTIONS, BERT_OPTIONS
from db_redis.redis_funcs.func_redis_save_key_mapping import (
    redis_save_key_mapping_dict)
from utils_common.normalized_path import get_full_file_normal_path, get_full_dir_normal_path


class ClassifierBERT:

    def __init__(self,
                 labels: Dict[int, str],
                 model_name: str = "bert-base-multilingual-cased",
                 cache_dir: str = None,
                 max_len: int = 64):
        """ BERT Model classifier to classify text phrases by sense categories.
        labels: dict[str: int]: e.g. {0: 'wish', 1: 'cancel', 3: 'rudeness'}
        arg: model_name: str: Pretrained model name, 'bert-base-multilingual-cased' by default
        arg: cache_dir: str: Pretrained model download directory when init, if differs from default one
        arg: max_len: int: Max length in symbols of the token string, more will be cut"""
        self.labels = labels
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.max_len = max_len
        self.last_saved_model_dir = None
        self.last_saved_dataset_dir = None

        device_name = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device_name)
        green_color = CONSOLE_COLORS.BRIGHT_GREEN
        reset_color = CONSOLE_COLORS.RESET
        print(f"Device: {green_color}{device_name.upper()}{reset_color}\n")

        self.tokenizer = self.__get_bert_tokenizer()
        self.model = self.__get_bert_for_sequence_classification(labels)

    def __get_bert_tokenizer(self):
        tokenizer = BertTokenizer.from_pretrained(
            pretrained_model_name_or_path=self.model_name,  # org
            cache_dir=self.cache_dir,  # extra
            force_download=False,
            local_files_only=True,  # False by default
            token=None,
            revision="main",
            trust_remote_code=False, )
        return tokenizer

    def __get_bert_for_sequence_classification(
            self, labels: dict
    ) -> BertForSequenceClassification | None:
        model = BertForSequenceClassification.from_pretrained(
            pretrained_model_name_or_path=self.model_name,  # org
            cache_dir=self.cache_dir,  # extra
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
        return model

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
        print(f"{'@' * 65}\n"
              f"prediction => {prediction}\n"
              f"self.labels[prediction] => {self.labels[prediction]}\n"
              f"self.labels => {self.labels}\n")
        return self.labels[prediction]

    def create_train_dataset(
            self,
            texts_list: List[str],
            labels_list: List[int],
            truncation: bool = False,
            padding: Union[Literal["max_length", "longest"], bool, None] = "max_length",  # Just for prod server
            # padding: Union[Literal["max_length", "longest"], False, None] = "max_length",  # Its more exact
            return_tensors: Union[Literal["pt", "tf", "np"], None] = "pt"
    ) -> TensorDataset:
        """:param texts_list: list: texts in corresponding test_train_data order
        :param labels_list: list: right test_train_data in corresponding texts order
        :param truncation: bool: truncate text or not to self.max_len
        :param padding: "max_length" padding to the length of self.max_len,
        "longest" padding to the max length text of the batch,
        False|None - without padding
        :param return_tensors: "pt" returns PyTorch tensors !!!FOR THIS PROJECT ONLY "pt"!!!,
        "tf" returns TensorFlow tensors, "np" returns NumPy arrays,
        None returns lists"""

        print(f"####### texts_list: {texts_list[:5]}.......\n"
              f"####### labels_list: {labels_list}\n"
              f"####### truncation: {truncation}\n"
              f"####### padding: {padding}\n"
              f"####### return_tensors: {return_tensors}\n")

        input_ids = []
        attention_masks = []
        for cur_text in texts_list:
            encoding = self.tokenizer(cur_text,
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
        # self.train_dataset = tensor_dataset
        return tensor_dataset

    async def train(self,
                    train_dataset: TensorDataset,
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
        print(f"train_dataset: {train_dataset}\n"
              f"max_training_epochs: {max_training_epochs}\n"
              f"max_cont_100perc_epochs: {max_cont_100perc_epochs}\n"
              f"batch_size: {batch_size}\n"
              f"learning_rate: {learning_rate}\n")

        if not train_dataset:
            print(f"TrainDataset [ERROR]: execute method .create_train_dataset() "
                  f"before calling method .train(): "
                  f"train_dataset: {train_dataset}")
            return

        dataset = train_dataset
        # dataset = train_dataset if train_dataset else self.train_dataset
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

        red_color = CONSOLE_COLORS.BRIGHT_RED
        reset_color = CONSOLE_COLORS.RESET
        print(f"\n{red_color} Model training epochs process....."
              f"{reset_color}")
        self.model.train()

        REDIS_KEY_EXPIRE_TIME = timedelta(days=REDIS_OPTIONS.STATUSES_EXPIRY_DAYS)
        redis_update = {
            "train_message": "Model training epochs process.....",
            "start_training": datetime.now().strftime("%d_%m_%Y__%H:%M:%S"),
            "max_training_epochs": max_training_epochs,
            "max_cont_100perc_epochs": max_cont_100perc_epochs,
            "batch_size": batch_size,
            "learning_rate": learning_rate, }
        redis_error = await redis_save_key_mapping_dict(
            key_name="train_process",
            mapping_dict=redis_update,
            expiry_seconds=REDIS_KEY_EXPIRE_TIME)
        if redis_error:
            print(redis_error)

        cont_100perc_epochs_counter = 0
        for cur_train_epoch_idx in range(max_training_epochs):
            redis_update = {
                "start_cur_epoch": datetime.now().strftime("%d_%m_%Y__%H:%M:%S"),
                "cur_train_epoch_idx": cur_train_epoch_idx, }
            redis_error = await redis_save_key_mapping_dict(
                key_name="train_process",
                mapping_dict=redis_update,
                expiry_seconds=REDIS_KEY_EXPIRE_TIME)
            if redis_error:
                print(redis_error)

            total_loss = 0
            for batch in dataloader:
                input_ids = batch[0].to(self.device)
                attention_mask = batch[1].to(self.device)
                labels = batch[2].to(self.device)

                outputs = self.model(input_ids=input_ids,
                                     attention_mask=attention_mask,
                                     labels=labels)
                loss = outputs.loss
                loss.backward()
                optimizer.step()
                optimizer.zero_grad()
                total_loss += loss.item()

            cur_perc_res = round((1 - total_loss / len(dataloader)) * 100)
            if cur_perc_res == 100:
                cont_100perc_epochs_counter += 1
            else:
                cont_100perc_epochs_counter = 0
            print(f"{red_color}Training epoch:{reset_color} "
                  f"{cur_train_epoch_idx + 1} "
                  f"[Right categories: {cur_perc_res}%] "
                  f"{cont_100perc_epochs_counter}/{max_cont_100perc_epochs}")

            train_epoch_log = (
                f"Training epoch: {cur_train_epoch_idx + 1} "
                f"[Right categories: {cur_perc_res}%] "
                f"{cont_100perc_epochs_counter}/{max_cont_100perc_epochs}")
            redis_update = {
                "train_epoch_log": train_epoch_log,
                "end_cur_epoch": datetime.now().strftime("%d_%m_%Y__%H:%M:%S"), }
            redis_error = await redis_save_key_mapping_dict(
                key_name="train_process",
                mapping_dict=redis_update,
                expiry_seconds=REDIS_KEY_EXPIRE_TIME)
            if redis_error:
                print(redis_error)

            if cont_100perc_epochs_counter == max_cont_100perc_epochs:
                redis_update = {
                    "cont_100perc_epochs_counter": cont_100perc_epochs_counter, }
                redis_error = await redis_save_key_mapping_dict(
                    key_name="train_process",
                    mapping_dict=redis_update,
                    expiry_seconds=REDIS_KEY_EXPIRE_TIME)
                if redis_error:
                    print(redis_error)
                return
        return

    def save_model(
            self,
            dir_full_path: str | Literal[""] | PathLike | bytes
    ) -> None | str:
        """Save model and tokeniser"""

        if not dir_full_path:
            error_log = (f"Model save dir path not defined [ERROR]: "
                         f"dir_full_path: {dir_full_path}")
            print(error_log)
            return error_log

        try:
            os.makedirs(dir_full_path, exist_ok=True)
            self.model.save_pretrained(str(dir_full_path))
            self.tokenizer.save_pretrained(dir_full_path)

            saved_model_extra_dir = BERT_OPTIONS.BERT_SAVED_MODEL_EXTRA_BASE_DIR
            saved_model_extra_dir_path = get_full_dir_normal_path(
                all_dir_str_parts=[dir_full_path, saved_model_extra_dir])
            os.makedirs(saved_model_extra_dir_path, exist_ok=True)

            model_metadata_f_name = BERT_OPTIONS.BERT_SAVED_MODEL_METADATA_FILE_NAME
            save_model_metadata_fpath = get_full_file_normal_path(
                all_dir_str_parts=[saved_model_extra_dir_path],
                file_name_with_ext=model_metadata_f_name)
            save_model_metadata = {
                "labels": self.labels,
                "model_name": self.model_name,
                "cache_dir": self.cache_dir,
                "max_len": self.max_len,
                "device": self.device,
                "last_saved_model_dir": self.last_saved_model_dir,
                "last_saved_dataset_dir": self.last_saved_dataset_dir, }
            torch.save(obj=save_model_metadata,
                       f=save_model_metadata_fpath)
            print(">>>>>>> save_model_metadata:", save_model_metadata)

            self.last_saved_model_dir = dir_full_path
        except Exception as error:
            error_log = f"BERT Model saving [ERROR]: error: {error}"
            print(error_log)
            return error_log

    def load_model(self, dir_full_path: str = None) -> str | None:
        """Load model and tokeniser saved earlier"""

        model_path = dir_full_path

        if not model_path:
            error_log = (f"Model load dir path not defined [ERROR]: "
                         f"dir_full_path: {dir_full_path}, "
                         f"self.last_trained_model_path "
                         f"{self.last_saved_model_dir}")
            print(error_log)
            return error_log

        if not os.path.isdir(model_path):
            error_log = (f"Model load dir path not exists [ERROR]: "
                         f"dir_full_path: {dir_full_path}, "
                         f"self.last_trained_model_path "
                         f"{self.last_saved_model_dir}")
            print(error_log)
            return error_log

        try:
            self.model = BertForSequenceClassification.from_pretrained(
                model_path).to(self.device)
            self.tokenizer = BertTokenizer.from_pretrained(model_path)
            self.last_saved_model_dir = model_path

            saved_model_extra_dir = BERT_OPTIONS.BERT_SAVED_MODEL_EXTRA_BASE_DIR
            model_metadata_f_name = BERT_OPTIONS.BERT_SAVED_MODEL_METADATA_FILE_NAME
            load_model_metadata_fpath = get_full_file_normal_path(
                all_dir_str_parts=[dir_full_path, saved_model_extra_dir],
                file_name_with_ext=model_metadata_f_name)
            loaded_model_metadata = torch.load(f=load_model_metadata_fpath)
            self.labels = loaded_model_metadata["labels"]
            self.model_name = loaded_model_metadata["model_name"]
            self.cache_dir = loaded_model_metadata["cache_dir"]
            self.max_len = loaded_model_metadata["max_len"]
            self.device = loaded_model_metadata["device"]
            self.last_saved_model_dir = loaded_model_metadata["last_saved_model_dir"]
            self.last_saved_dataset_dir = loaded_model_metadata["last_saved_dataset_dir"]
            print(">>>>>>> loaded_model_metadata:", loaded_model_metadata)

        except Exception as error:
            error_log = f"BERT Model loading [ERROR]: error: {error}"
            print(error_log)
            return error_log

    def reinitialize_with_new_labels(self,
                                     new_labels_categories: Dict[int, str]
                                     ) -> None | str:
        """Reinitialize the model with a new set (dictionary) of labels.
        This preserves the original model_name, cache_dir and max_len parameters,
        but adjusts the model's classification head to accommodate the new number of labels.
        arg: new_labels_categories: dict[str: int]: e.g. {0: 'wish', 1: 'cancel', 3: 'rudeness'}"""
        try:
            print(f"*** BEFORE MODEL REINITIALIZING:\n"
                  f"*** self: {self}\n"
                  f"*** hash(self): {hash(self)}\n"
                  f"*** self.model: {self.model}\n"
                  f"*** hash(self.model): {hash(self.model)}\n"
                  f"*** self.model.config.num_labels: {self.model.config.num_labels}\n"
                  f"*** self.labels [{len(self.labels)}]: {self.labels}\n"
                  f"*** new_labels_categories {new_labels_categories}\n"
                  f"*** len(new_labels_categories): {len(new_labels_categories)}\n")
            self.model = self.__get_bert_for_sequence_classification(new_labels_categories)
            self.labels = new_labels_categories  # Update the labels number
            print(f"### AFTER MODEL REINITIALIZING:\n"
                  f"### self: {self}\n"
                  f"### hash(self): {hash(self)}\n"
                  f"### self.model: {self.model}\n"
                  f"### hash(self.model): {hash(self.model)}\n"
                  f"### self.model.config.num_labels: {self.model.config.num_labels}\n"
                  f"### self.labels [{len(self.labels)}]: {self.labels}\n"
                  f"### new_labels_categories {new_labels_categories}\n"
                  f"### len(new_labels_categories): {len(new_labels_categories)}\n")
        except Exception as error:
            error_log = f"BERT Model reinitialising [ERROR]: error: {error}"
            print(error_log)
            return error_log
