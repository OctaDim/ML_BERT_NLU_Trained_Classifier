if __name__ == "__main__":
    async def test_main_process():
        from db_postgres.postgres_dependencies.dep_get_bert_model_instance import (
            get_bert_model_instance_dep)
        from ML_BERT_classifier.init_bert import init_and_start_bert_model
        from db_postgres.postgres_init.db_tables_initialization import (
            initialize_db_tables)
        from fast_api.app_account_data.scheme_account_data import (
            AccountDataBert)
        from fast_api.app_add_single_category.func_add_draft_single_category import (
            add_draft_single_category)

        await initialize_db_tables()
        await init_and_start_bert_model()

        bert_model_inst = await get_bert_model_instance_dep()
        update_category = "new draft single category"
        account_data = AccountDataBert(account_username="octadim",
                                       account_id="123")
        await add_draft_single_category(account_data=account_data,
                                        update_category=update_category,
                                        bert_model_inst=bert_model_inst)


    import asyncio

    asyncio.run(main=test_main_process(), debug=True)
