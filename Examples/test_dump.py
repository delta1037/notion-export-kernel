import logging

import NotionDump
from NotionDump.Dump.dump import Dump
from NotionDump.Notion.Notion import NotionQuery
from NotionDump.utils import common_op

TOKEN_TEST = "secret_WRLJ9xyEawNxzRhVHVWfciTl9FAyNCd29GMUvr2hQD4"
PAGE_MIX_ID = "950e57e0507b4448a55a13b2f47f031f"
DB_TABLE_INLINE_ID = "3b40cf6b60fc49edbe25740dd9a74af7"
TABLE_ID = "13b914160ef740dcb64e55c5393762fa"
RER_LIST_ID = "d32db4693409464b9981caec9ef11974"


# 解析数据库内容测试：根据token和id解析数据库内容，得到临时CSV文件
def test_page_parser(query):
    page_handle = Dump(
        dump_id=PAGE_MIX_ID,
        query_handle=query,
        export_child_pages=True,
        dump_type=NotionDump.DUMP_TYPE_PAGE
    )
    # 将解析内容存储到文件中；返回内容存储为json文件
    page_detail_json = page_handle.dump_to_file()

    print("json output to page_parser_result")
    common_op.save_json_to_file(
        handle=page_detail_json,
        json_name="page_parser_result.json"
    )


# 解析数据库内容测试：根据token和id解析数据库内容，得到临时CSV文件
def test_db_table_inline_parser(query):
    db_handle = Dump(
        dump_id=DB_TABLE_INLINE_ID,
        query_handle=query,
        export_child_pages=True,
        dump_type=NotionDump.DUMP_TYPE_DB_TABLE
    )
    # 将解析内容存储到文件中；返回内容存储为json文件
    page_detail_json = db_handle.dump_to_file()

    print("json output to db_parser_result")
    common_op.save_json_to_file(
        handle=page_detail_json,
        json_name="db_parser_result.json"
    )


# 页面表格测试
def test_get_table_block(query):
    block_handle = Dump(
        dump_id=TABLE_ID,
        query_handle=query,
        export_child_pages=True,
        dump_type=NotionDump.DUMP_TYPE_BLOCK
    )
    # 将解析内容存储到文件中；返回内容存储为json文件
    page_detail_json = block_handle.dump_to_file()

    print("json output to block_table_parser_result")
    common_op.save_json_to_file(
        handle=page_detail_json,
        json_name="block_table_parser_result.json"
    )


# 递归列表测试
def test_get_rer_list(query):
    block_handle = Dump(
        dump_id=RER_LIST_ID,
        query_handle=query,
        export_child_pages=True,
        dump_type=NotionDump.DUMP_TYPE_BLOCK
    )
    # 将解析内容存储到文件中；返回内容存储为json文件
    page_detail_json = block_handle.dump_to_file()

    print("json output to block_list_parser_result")
    common_op.save_json_to_file(
        handle=page_detail_json,
        json_name="block_list_parser_result.json"
    )


if __name__ == '__main__':
    query_handle = NotionQuery(token=TOKEN_TEST)
    if query_handle is None:
        logging.exception("query handle init error")
        exit(-1)

    # Block解析测试
    test_get_table_block(query_handle)

    # Block解析测试
    test_get_rer_list(query_handle)

    # 数据库解析测试
    test_db_table_inline_parser(query_handle)

    # 页面解析测试
    test_page_parser(query_handle)

