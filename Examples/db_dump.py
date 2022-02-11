# author: delta1037
# Date: 2022/01/11
# mail:geniusrabbit@qq.com

import logging

import NotionDump
from NotionDump.Dump.database import Database
from NotionDump.Dump.dump import Dump
from NotionDump.Notion.Notion import NotionQuery
from NotionDump.utils import common_op

TOKEN_TEST = "secret_WRLJ9xyEawNxzRhVHVWfciTl9FAyNCd29GMUvr2hQD4"
DB_TABLE_INLINE_ID = "3b40cf6b60fc49edbe25740dd9a74af7"
NotionDump.DUMP_MODE = NotionDump.DUMP_MODE_DEBUG


# 解析数据库内容测试：根据token和id解析数据库内容，得到临时CSV文件
def test_db_table_inline_parser_dic(query):
    db_handle = Database(
        database_id=DB_TABLE_INLINE_ID,
        query_handle=query,
        export_child_pages=False
    )
    # 将解析内容存储到文件中；返回内容存储为json文件
    page_detail_json = db_handle.dump_to_file()

    print("json output to db_parser_result")
    common_op.save_json_to_file(
        handle=page_detail_json,
        json_name=".tmp/db_parser_result.json"
    )
    print(db_handle.dump_to_dic())


# 解析数据库内容测试：根据token和id解析数据库内容，得到临时CSV文件
def test_db_table_inline_parser_csv(query, export_child=False):
    db_handle = Dump(
        dump_id=DB_TABLE_INLINE_ID,
        query_handle=query,
        export_child_pages=export_child,
        dump_type=NotionDump.DUMP_TYPE_DB_TABLE
    )
    # 将解析内容存储到文件中；返回内容存储为json文件
    page_detail_json = db_handle.dump_to_file()

    print("json output to db_parser_result")
    common_op.save_json_to_file(
        handle=page_detail_json,
        json_name=".tmp/db_parser_result.json"
    )


def test_db_table_inline_parser_md(query, export_child=False):
    db_handle = Dump(
        dump_id=DB_TABLE_INLINE_ID,
        query_handle=query,
        export_child_pages=export_child,
        dump_type=NotionDump.DUMP_TYPE_DB_TABLE,
        db_parser_type=NotionDump.PARSER_TYPE_MD,
    )
    # 将解析内容存储到文件中；返回内容存储为json文件
    page_detail_json = db_handle.dump_to_file()

    print("json output to db_parser_result")
    common_op.save_json_to_file(
        handle=page_detail_json,
        json_name=".tmp/db_parser_result.json"
    )


if __name__ == '__main__':
    query_handle = NotionQuery(token=TOKEN_TEST)
    if query_handle is None:
        logging.exception("query handle init error")
        exit(-1)

    # 数据库存储到CSV文件
    # test_db_table_inline_parser_csv(query_handle, True)

    # 数据库存储到MD文件
    # test_db_table_inline_parser_md(query_handle, True)

    # 数据库存储到字典
    test_db_table_inline_parser_dic(query_handle)

