# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com
import os
import shutil

import NotionDump
from NotionDump.Notion.Notion import NotionQuery
from NotionDump.Parser.mix_parser import MixParser
from NotionDump.utils import common_op
from NotionDump.utils import internal_var


class Page:
    # 初始化
    def __init__(
            self,
            page_id,
            query_handle: NotionQuery,
            export_child_pages=False,
            page_parser_type=NotionDump.PARSER_TYPE_MD,
            db_parser_type=NotionDump.PARSER_TYPE_PLAIN
    ):
        self.page_id = page_id.replace('-', '')
        self.query_handle = query_handle
        # 是否导出子页面
        self.export_child_page = export_child_pages
        self.page_parser_type = page_parser_type
        self.db_parser_type = db_parser_type

        # 构造解析器
        self.mix_parser = MixParser(
            mix_id=self.page_id,
            query_handle=self.query_handle,
            export_child_pages=self.export_child_page,
            page_parser_type=self.page_parser_type,
            db_parser_type=self.db_parser_type
        )

        # 创建临时文件夹
        self.tmp_dir = NotionDump.TMP_DIR
        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)

    # show_child_page
    @staticmethod
    def get_pages_detail():
        return internal_var.PAGE_DIC

    # 获取到所有的PAGE数据
    def dump_to_file(self, file_name=None):
        # 解析到临时文件中
        tmp_md_filename = self.mix_parser.mix_parser(root_id=self.page_id, id_type="block")
        if tmp_md_filename is None:
            common_op.debug_log("page parser fail, id="+self.page_id, level=NotionDump.DUMP_MODE_DEFAULT)
            return ""

        if file_name is not None:
            shutil.copyfile(tmp_md_filename, file_name)
            common_op.debug_log("copy " + tmp_md_filename + " to " + file_name, level=NotionDump.DUMP_MODE_DEFAULT)
            return file_name

        return tmp_md_filename

    def dump_to_db(self):
        # 从配置文件中获取数据库配置，打开数据库，并将csv文件写入到数据库中
        page_json = self.query_handle.retrieve_block_children(self.page_id)
        if page_json is None:
            return None

        # TODO 将Md文件写入到数据库;调用SQL中的notion2sql提供的接口
        return

    # 源文件，直接输出成json; 辅助测试使用
    def dump_to_json(self, json_name=None):
        page_json = self.query_handle.retrieve_block_children(self.page_id)
        if page_json is None:
            return None

        if json_name is None:
            json_name = self.tmp_dir + self.page_id + ".json"
        common_op.save_json_to_file(page_json, json_name)
        return
