from pydantic import BaseModel


class SaveModelDataTest(BaseModel):
    model_save_dir_path: str = ""


class LoadModelDataTest(BaseModel):
    model_load_dir_path: str = ""
