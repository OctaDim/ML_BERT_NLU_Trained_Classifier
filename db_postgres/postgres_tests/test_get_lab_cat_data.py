# ####################### DEBUG CODE (start) ###########################
# ######################################################################
if __name__ == "__main__":
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    import asyncio
    from db_postgres.postgres_queries.query_get_label_category_data import get_label_category_data
    label_category_records = asyncio.run(main=get_label_category_data(), debug=True)
    print(label_category_records)
# ########################## DEBUG CODE (end) ##########################
# ######################################################################
