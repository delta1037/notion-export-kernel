from NotionDump.Api.database import Database

TOKEN_TEST = "secret_WRLJ9xyEawNxzRhVHVWfciTl9FAyNCd29GMUvr2hQD4"
DB_TABLE_INLINE_ID = "3b40cf6b60fc49edbe25740dd9a74af7"


# 获取数据库原始数据测试：根据token和id获取json数据，得到临时JSON文件
def test_get_db_json_data():
    db_handle = Database(token=TOKEN_TEST, database_id=DB_TABLE_INLINE_ID)
    db_handle.database_to_json()


# 解析数据库内容测试：根据token和id解析数据库内容，得到临时CSV文件
def test_db_table_inline_parser():
    db_handle = Database(token=TOKEN_TEST, database_id=DB_TABLE_INLINE_ID)
    db_handle.database_to_csv()


if __name__ == '__main__':
    # 获取数据库原始数据测试
    test_get_db_json_data()

    # 解析数据库内容测试
    test_db_table_inline_parser()
