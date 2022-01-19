# author: delta1037
# Date: 2022/01/11
# mail:geniusrabbit@qq.com

import logging

import NotionDump
from NotionDump.Dump.dump import Dump
from NotionDump.Notion.Notion import NotionQuery
from NotionDump.utils import common_op

TOKEN_TEST = "secret_WRLJ9xyEawNxzRhVHVWfciTl9FAyNCd29GMUvr2hQD4"
TABLE_ID = "13b914160ef740dcb64e55c5393762fa"
RER_LIST_ID = "d32db4693409464b9981caec9ef11974"


# 页面表格测试
def test_get_table_block(query, export_child=True):
    block_handle = Dump(
        dump_id=TABLE_ID,
        query_handle=query,
        export_child_pages=export_child,
        dump_type=NotionDump.DUMP_TYPE_BLOCK
    )
    # 将解析内容存储到文件中；返回内容存储为json文件
    page_detail_json = block_handle.dump_to_file()

    print("json output to block_table_parser_result")
    common_op.save_json_to_file(
        handle=page_detail_json,
        json_name=".tmp/block_table_parser_result.json"
    )


# 递归列表测试
def test_get_rer_list(query, export_child=True):
    block_handle = Dump(
        dump_id=RER_LIST_ID,
        query_handle=query,
        export_child_pages=export_child,
        dump_type=NotionDump.DUMP_TYPE_BLOCK
    )
    # 将解析内容存储到文件中；返回内容存储为json文件
    page_detail_json = block_handle.dump_to_file()

    print("json output to block_list_parser_result")
    common_op.save_json_to_file(
        handle=page_detail_json,
        json_name=".tmp/block_list_parser_result.json"
    )


if __name__ == '__main__':
    query_handle = NotionQuery(token=TOKEN_TEST)
    if query_handle is None:
        logging.exception("query handle init error")
        exit(-1)

    # Block解析测试
    # test_get_table_block(query_handle, export_child=False)
    test_get_table_block(query_handle, export_child=True)

    # Block解析测试
    # test_get_rer_list(query_handle, export_child=False)
    test_get_rer_list(query_handle, export_child=True)
