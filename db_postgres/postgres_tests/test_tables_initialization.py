# ######################### DEBUG CODE (start) #########################
# ######################################################################
if __name__ == "__main__":
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    from db_postgres.postgres_init.db_tables_initialization import (
        initialize_db_tables)
    import asyncio
    asyncio.run(main=initialize_db_tables(), debug=True)
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
# ######################### DEBUG CODE (start) #########################
# ######################################################################
