# ####################### DEBUG CODE (start) ###########################
# ######################################################################
if __name__ == "__main__":
    import asyncio
    from db_postgres.postgres_queries.qry_get_label_category_data import get_label_category_data_qry
    label_category_records = asyncio.run(main=get_label_category_data_qry(), debug=True)
    print(label_category_records)
# ########################## DEBUG CODE (end) ##########################
# ######################################################################
