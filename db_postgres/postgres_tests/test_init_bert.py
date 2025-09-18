# ####################### DEBUG CODE (start) ###########################
# ######################################################################


if __name__ == "__main__":
    from ML_BERT_classifier.init_bert import (
        init_and_start_bert_model, bert_model_inst)
    from db_postgres.postgres_init.db_tables_initialization import (
        initialize_db_tables)
    async def main_loop_func():
        await initialize_db_tables()
        await init_and_start_bert_model()

    import asyncio
    asyncio.run(main=main_loop_func(), debug=True)
    print(hash(bert_model_inst))
    print(bert_model_inst)


# ########################## DEBUG CODE (end) ##########################
# ######################################################################
