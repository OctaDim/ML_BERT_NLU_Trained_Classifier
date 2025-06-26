from pydantic import BaseModel
# from configs.settings import BERT_OPTIONS


class SaveModelDataBert(BaseModel):
    """If model_save_dir_path is not defined and passed via request
    BERT_OPTIONS.BERT_TRAINED_MODELS_SAVE_PATH from settings.py is used"""
    model_save_dir_path: str = ""
    # model_save_dir_path: str = BERT_OPTIONS.BERT_TRAINED_MODELS_SAVE_PATH
    # model_save_dir_path: str = r"C:\Users\dexp\Projects\ML_BERT_NLU_Training_Classifier\ML_BERT_classifier\models_bert_product_trained\trained_bert_manually_defined_save_dir"
    # model_save_dir_path: str = "C:\\Users\\dexp\\Projects\\ML_BERT_NLU_Training_Classifier\\ML_BERT_classifier\\models_bert_product_trained\\trained_bert_manually_defined_save_dir"
