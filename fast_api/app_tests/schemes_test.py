from pydantic import BaseModel


class AuthDataTest(BaseModel):
    username: str = "temp_username"
    password: str = "temp_password"


class SaveModelDataTest(BaseModel):
    """If model_save_dir_path is not defined and passed via request
    BERT_OPTIONS.BERT_TRAINED_MODELS_SAVE_PATH from settings.py is used"""
    model_save_dir_path: str = r"C:\Users\dexp\Projects\ML_BERT_NLU_Training_Classifier\ML_BERT_classifier\models_bert_test_fine_trained\trained_bert_test_manually_defined_save_dir"
    # model_save_dir_path: str = "C:\\Users\\dexp\\Projects\\ML_BERT_NLU_Training_Classifier\\ML_BERT_classifier\\models_bert_test_fine_trained\\trained_bert_test_manually_defined_save_dir"


class LoadModelDataTest(BaseModel):
    """If model_load_dir_path is not defined and passed via request
    bert_model_instance.last_saved_model_path is tried to be used
    If not defined manually call method .save_model first"""
    model_load_dir_path: str = r"C:\Users\dexp\Projects\ML_BERT_NLU_Training_Classifier\ML_BERT_classifier\models_bert_test_fine_trained\trained_bert_26_06_2025_11_55_14_902828-11111"
    # model_load_dir_path: str = r"C:\Users\dexp\Projects\ML_BERT_NLU_Training_Classifier\ML_BERT_classifier\models_bert_test_fine_trained\trained_bert_26_06_2025_11_58_12_624875-22222"
    # model_load_dir_path: str = "C:\\Users\\dexp\\Projects\\ML_BERT_NLU_Training_Classifier\\ML_BERT_classifier\\models_bert_test_fine_trained\\trained_bert_26_06_2025_11_58_12_624875-11111"
    # model_load_dir_path: str = "C:\\Users\\dexp\\Projects\\ML_BERT_NLU_Training_Classifier\\ML_BERT_classifier\\models_bert_test_fine_trained\\trained_bert_26_06_2025_11_58_12_624875-22222"
