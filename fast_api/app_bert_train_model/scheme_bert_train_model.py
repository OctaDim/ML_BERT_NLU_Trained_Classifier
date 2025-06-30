from pydantic import BaseModel


class TrainModelDataBert(BaseModel):
    save_model_after_train: bool = True
    trained_model_save_dir_path: str = ""  # Not necessary. Auto created by default, if save_model_after_train=True
