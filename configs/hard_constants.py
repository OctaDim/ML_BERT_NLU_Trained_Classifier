from dataclasses import dataclass


@dataclass(frozen=True)
class HARD_CONST:  # DO NOT CHANGE HARD_CONST CONSTANTS!!!
    SAVED_MODEL_EXTRA_DIR: str = "saved_model_extra_data"
    SAVED_MODEL_METADATA_PT_FN: str = "model_metadata.pt"
    SAVED_MODEL_EXTRA_DATA_JSON_FN: str = "model_extra_data.json"
