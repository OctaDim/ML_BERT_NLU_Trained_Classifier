if __name__ == "__main__":
    async def test_add_save_text_category():
        from fast_api.app_account_data.scheme_account_data import AccountDataBert
        from fast_api.app_add_text_category.func_add_save_text_category import add_save_single_text_category
        from db_postgres.postgres_dependencies.dep_get_bert_model_instance import (
            get_bert_model_instance_dep)
        from ML_BERT_classifier.init_bert import init_and_start_bert_model
        from db_postgres.postgres_init.db_tables_initialization import (
            sync_initialize_db_tables)

        await sync_initialize_db_tables()
        await init_and_start_bert_model()

        bert_model_inst = await get_bert_model_instance_dep()
        update_text = "text-6 for cat-4"
        update_category = "cat-4"
        account_data = AccountDataBert(account_username="globalhome",
                                       account_id="30")
        await add_save_single_text_category(
            account_data=account_data,
            update_text=update_text,
            update_category=update_category,
            bert_model_inst=bert_model_inst)


    import asyncio

    asyncio.run(main=test_add_save_text_category(), debug=True)
