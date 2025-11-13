# ####################### DEBUG CODE (start) ###########################
# ######################################################################


if __name__ == "__main__":
    async def main_loop_func():
        from ML_BERT_classifier.init_bert import init_and_start_bert_model
        from db_postgres.postgres_init.db_tables_initialization import sync_initialize_db_tables

        await sync_initialize_db_tables()
        await init_and_start_bert_model()


    import asyncio
    from ML_BERT_classifier.init_bert import get_global_bert_model_inst

    asyncio.run(main=main_loop_func(), debug=True)

    print("🚀 LET'S CHECK !!! 🚀")
    func_bert_model_inst = get_global_bert_model_inst()
    print(f"func_bert_model_inst: {func_bert_model_inst}")
    print(f"func_bert_model_inst.last_saved_model_dir: {func_bert_model_inst.last_saved_model_dir}")
    print(f"func_bert_model_inst.last_saved_dataset_dir: {func_bert_model_inst.last_saved_dataset_dir}\n")


# ########################## DEBUG CODE (end) ##########################
# ######################################################################
