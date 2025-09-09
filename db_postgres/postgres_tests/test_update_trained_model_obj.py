# ####################### DEBUG CODE (start) ###########################
# ######################################################################
async def update_model_object_test():
    from db_postgres.postgres_utils.merge_obj_ongoing_session import merge_obj_to_ongoing_session
    from db_postgres.postgres_async_conn.pgs_async_connection import PostgresConnection
    from db_postgres.postgres_models.trained_bert_model import TrainedBertModel
    from db_postgres.postgres_models.customer_model import CustomerModel
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    pgs_conn = PostgresConnection()
    print(f"pgs_conn", {await pgs_conn.db_health_check()})
    new_customer = TrainedBertModel()
    new_update_data = [
        {"customer_id": 11,
         "model_directory": "/usr/local/ML_BERT_NLU_Training_Classifier/WORKING_DATA/trained_product_bert_models/trained_bert_06_09_2025_13_28_58_835504-19760", },
        # {"username": "octadim", "account_id": "333", },
        # {"username": "тест_1", "account_id": "111", },
        # {"username": "тест_2", "account_id": "222", },
    ]
    async with pgs_conn.async_session() as pgs_session:
        print(f"pgs_conn: {pgs_session}")
        for cur_data in new_update_data:
            await merge_obj_to_ongoing_session(
                object_to_merge=new_customer,
                new_update_data=cur_data,
                ongoing_session=pgs_session)
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main=update_model_object_test(), debug=True)
# ########################## DEBUG CODE (end) ##########################
# ######################################################################
