import os


def validate_bert_model_directory(model_directory_path) -> bool:
    # TODO: Add checking BERT model files and dirs exist
    model_directory_str = model_directory_path if model_directory_path else ""
    if model_directory_path and os.path.isdir(model_directory_str):
        print(f"BERT Model directory exists [OK]")
        return True
    else:  # Last saved model path from DB not found
        print(f"BERT model directory not found [ERROR]:\n"
              f"model_directory_path: {model_directory_path}\n")
        return False
