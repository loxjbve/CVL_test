# 数据库功能实现
import json
import pymysql
import os,glob
import data_process as dp
def create_table(cursor, table_name, sample_record):
    columns = []
    for key, value in sample_record.items():
        if isinstance(value, int):
            column_type = 'BIGINT'
        elif isinstance(value, str):
            column_type = 'VARCHAR(255)'
        else:
            column_type = 'TEXT'  # 处理其他类型如 null
        columns.append(f"{key} {column_type}")
    columns_sql = ", ".join(columns)
    create_table_sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({columns_sql});"
    cursor.execute(create_table_sql)

def insert_data(cursor, table_name, data):
    # 构建插入数据的 SQL 语句
    keys = data[0].keys()
    columns = ", ".join(keys)
    placeholders = ", ".join(["%s"] * len(keys))
    insert_sql = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"
    for record in data:
        values = tuple(record[key] for key in keys)
        cursor.execute(insert_sql, values)

def dump_to_db(file_path):
    table_name = os.path.splitext(os.path.basename(file_path))[0]

    # 读JSON
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 连接DB
    db_host,db_user,db_password,db_database,db_charset = dp.get_config("database")
    connection = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_database,
        charset=db_charset,
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            create_table(cursor, table_name, data[0])
            insert_data(cursor, table_name, data)
        connection.commit()
    finally:
        connection.close()
        print(f"已导入{table_name}")


def dump_all_json_files_to_db(directory):
    json_files = glob.glob(os.path.join(directory, '*_members.json'))
    for file_path in json_files:
        dump_to_db(file_path)

#dump_all_json_files_to_db("C:\\Users\\loxjbve\\PycharmProjects\\tgtest")
