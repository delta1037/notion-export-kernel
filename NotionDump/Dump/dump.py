# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com
import logging

import NotionDump
from NotionDump.Dump.block import Block
from NotionDump.Dump.database import Database
from NotionDump.Dump.page import Page
from NotionDump.Notion.Notion import NotionQuery
from NotionDump.utils import internal_var


class Dump:
    def __init__(
            self,
            dump_id,
            query_handle: NotionQuery,
            export_child_pages=False,
            parser_type=internal_var.PARSER_TYPE_MD,
            dump_type=NotionDump.DUMP_TYPE_PAGE
    ):
        self.dump_id = dump_id.replace('-', '')
        self.query_handle = query_handle
        # 是否导出子页面
        self.export_child_page = export_child_pages
        self.parser_type = parser_type
        self.dump_type = dump_type

        self.handle = None
        if dump_type == NotionDump.DUMP_TYPE_PAGE:
            self.handle = Page(
                page_id=self.dump_id,
                query_handle=self.query_handle,
                export_child_pages=self.export_child_page
            )
        elif dump_type == NotionDump.DUMP_TYPE_BLOCK:
            self.handle = Block(
                block_id=self.dump_id,
                query_handle=self.query_handle,
                export_child_pages=self.export_child_page
            )
        elif dump_type == NotionDump.DUMP_TYPE_DB_TABLE:
            self.handle = Database(
                database_id=self.dump_id,
                query_handle=self.query_handle,
                export_child_pages=self.export_child_page
            )
        else:
            logging.exception("unknown dump type:" + str(self.dump_type))

    # show_child_page
    @staticmethod
    def get_pages_detail():
        return internal_var.PAGE_DIC

    # 获取到所有的BLOCK数据
    def dump_to_file(self, file_name=None):
        if self.handle is None:
            logging.exception("dump init fail")
            return ""
        # 递归时第一个block单独作为一个main page存放
        return self.handle.dump_to_file(file_name=file_name)

    def dump_to_db(self):
        if self.handle is None:
            logging.exception("dump init fail")
            return ""
        return self.handle.dump_to_db()

    # 源文件，直接输出成json; 辅助测试使用
    def dump_to_json(self, json_name=None):
        if self.handle is None:
            logging.exception("dump init fail")
            return ""
        return self.handle.dump_to_json(json_name=json_name)
