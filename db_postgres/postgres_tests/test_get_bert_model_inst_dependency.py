# ####################### DEBUG CODE (start) ###########################
# ######################################################################


if __name__ == "__main__":
    from fast_api.fast_api_dependencies.dep_get_bert_model_instance import get_bert_model_instance_dep
    async def test_get_bert_model_inst_dep():
        from ML_BERT_classifier.init_bert import init_and_start_bert_model
        from db_postgres.postgres_init.db_tables_initialization import sync_initialize_db_tables

        await sync_initialize_db_tables()
        await init_and_start_bert_model()
        depend = await get_bert_model_instance_dep()
        return depend

    import asyncio
    dependency = asyncio.run(main=test_get_bert_model_inst_dep(),
                             debug=True)
    print(f"dependency: {dependency}")


# ########################## DEBUG CODE (end) ##########################
# ######################################################################
