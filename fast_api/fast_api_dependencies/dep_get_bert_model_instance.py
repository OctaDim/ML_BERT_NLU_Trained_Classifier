from ML_BERT_classifier.init_bert import get_global_bert_model_inst


async def get_bert_model_instance_dep():
    return get_global_bert_model_inst()
