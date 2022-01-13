import logging

import NotionDump
from NotionDump.Dump.dump import Dump
from NotionDump.Notion.Notion import NotionQuery
from NotionDump.utils import common_op

TOKEN_TEST = "secret_WRLJ9xyEawNxzRhVHVWfciTl9FAyNCd29GMUvr2hQD4"
DB_TABLE_INLINE_ID = "3b40cf6b60fc49edbe25740dd9a74af7"


# 获取数据库原始数据测试：根据token和id获取json数据，得到临时JSON文件
def test_get_db_json_data(query):
    db_handle = Dump(
        dump_id=DB_TABLE_INLINE_ID,
        query_handle=query,
        export_child_pages=False,
        dump_type=NotionDump.DUMP_TYPE_DB_TABLE
    )
    db_handle.dump_to_json()


# 解析数据库内容测试：根据token和id解析数据库内容，得到临时CSV文件
def test_db_table_inline_parser(query):
    common_op.debug_log("test_db_table_inline_parser start")
    db_handle = Dump(
        dump_id=DB_TABLE_INLINE_ID,
        query_handle=query,
        export_child_pages=True,
        dump_type=NotionDump.DUMP_TYPE_DB_TABLE
    )
    page_detail_json = db_handle.dump_to_file()

    # 输出样例
    common_op.save_json_to_file(page_detail_json, "page_detail.json")
    common_op.debug_log("test_db_table_inline_parser end")


if __name__ == '__main__':
    query_handle = NotionQuery(token=TOKEN_TEST)
    if query_handle is None:
        logging.exception("query handle init error")
        exit(-1)
    # 获取数据库原始数据测试
    # test_get_db_json_data(query_handle)

    # 解析数据库内容测试
    test_db_table_inline_parser(query_handle)
