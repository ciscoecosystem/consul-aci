from custom_logger import CustomLogger
import os
import sqlite3
import alchemy_core


logger = CustomLogger.get_logger("./app.log")
DATABASE_PATH = alchemy_core.DATABASE_NAME.split("///")[1]


def get_data_from_db(table_list, schema=False):
    response = dict()
    for table in table_list:
        try:
            connection = sqlite3.connect(DATABASE_PATH)
            cursor = connection.cursor()

            if schema:
                query = "pragma table_info('{}');".format(table)
            else:
                query = "select *from {};".format(table)

            cursor.execute(query)

            data = cursor.fetchall()
            if schema:
                columns = list(map(lambda x: x[1], data))
                response[table] = columns
            else:
                response[table] = data
        except Exception as e:
            logger.info("Error in migration for table '{}', {}".format(table, e))

    return response


def update_db():
    try:
        table_list = ['login', 'tenant', 'polling']
        old_data = get_data_from_db(table_list)
        logger.info("agent, {}".format(old_data['login']))
        os.remove(DATABASE_PATH)
        db_obj = alchemy_core.Database()
        db_obj.create_tables()

        connection = db_obj.engine.connect()
        with connection.begin():
            for agent_info in old_data['login']:
                db_obj.insert_and_update(
                    connection,
                    db_obj.LOGIN_TABLE_NAME,
                    agent_info[:-3]
                )
        connection.close()

        connection = db_obj.engine.connect()
        with connection.begin():
            for tenant_info in old_data['tenant']:
                db_obj.insert_into_table(
                    connection,
                    db_obj.TENANT_TABLE_NAME,
                    [tenant_info[0]]
                )
        connection.close()

        connection = db_obj.engine.connect()
        with connection.begin():
            for polling_data in old_data['polling']:
                db_obj.insert_and_update(
                    connection,
                    db_obj.POLLING_TABLE_NAME,
                    ['interval', polling_data[1]]
                )
        connection.close()

    except Exception as e:
        logger.info("Error in updating db in migration, {}".format(e))


if __name__ == "__main__":
    if os.path.exists(DATABASE_PATH):

        table_list = ['data_fetch', 'ep']
        schema_in_db = get_data_from_db(table_list, True)

        tables_to_update = []

        for each in schema_in_db:
            if schema_in_db[each] == alchemy_core.Database.SCHEMA_DICT[each]:
                logger.info("Migration not needed for {}".format(each))
            else:
                logger.info("Migration needed for {}".format(each))
                logger.info("Old schema of {}, {}".format(each, schema_in_db[each]))
                logger.info("New schema of {}, {}".format(each, alchemy_core.Database.SCHEMA_DICT[each]))
                tables_to_update.append(each)
        if tables_to_update:
            update_db()
