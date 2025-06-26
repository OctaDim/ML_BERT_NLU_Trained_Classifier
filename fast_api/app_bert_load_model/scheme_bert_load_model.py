from pydantic import BaseModel


class LoadModelDataBert(BaseModel):
    """If model_load_dir_path is not defined and passed via request
    bert_model_instance.last_saved_model_path is tried to be used
    If not defined manually call method .save_model first"""
    model_load_dir_path: str = r"C:\Users\dexp\Projects\ML_BERT_NLU_Training_Classifier\ML_BERT_classifier\models_bert_test_fine_trained\trained_bert_26_06_2025_11_55_14_902828-11111"
    # model_load_dir_path: str = r"C:\Users\dexp\Projects\ML_BERT_NLU_Training_Classifier\ML_BERT_classifier\models_bert_test_fine_trained\trained_bert_26_06_2025_11_58_12_624875-22222"
    # model_load_dir_path: str = "C:\\Users\\dexp\\Projects\\ML_BERT_NLU_Training_Classifier\\ML_BERT_classifier\\models_bert_test_fine_trained\\trained_bert_26_06_2025_11_58_12_624875-11111"
    # model_load_dir_path: str = "C:\\Users\\dexp\\Projects\\ML_BERT_NLU_Training_Classifier\\ML_BERT_classifier\\models_bert_test_fine_trained\\trained_bert_26_06_2025_11_58_12_624875-22222"
