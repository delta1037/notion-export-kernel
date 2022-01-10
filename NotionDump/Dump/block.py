# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com

from NotionDump.Dump.page import Page
from NotionDump.Notion.Notion import NotionQuery
from NotionDump.utils import internal_var


# Block内容解析
class Block:
    # 初始化
    def __init__(self, block_id, query_handle: NotionQuery, export_child_pages=False, parser_type=internal_var.PARSER_TYPE_MD):
        self.block_id = block_id.replace('-', '')
        self.query_handle = query_handle
        # 是否导出子页面
        self.export_child_page = export_child_pages
        self.parser_type = parser_type

        # 构造解析器
        self.page_handle = Page(
            page_id=self.block_id,
            query_handle=self.query_handle,
            export_child_pages=self.export_child_page,
            parser_type=self.parser_type
        )

    # show_child_page
    @staticmethod
    def get_pages_detail():
        return internal_var.PAGE_DIC

    # 获取到所有的BLOCK数据
    def page_to_md(self, md_name=None):
        # 递归时第一个block单独作为一个main page存放
        return self.page_handle.page_to_md(md_name=md_name)

    def page_to_db(self):
        return self.page_handle.page_to_db()

    # 源文件，直接输出成json; 辅助测试使用
    def page_to_json(self, json_name=None):
        return self.page_handle.page_to_json(json_name=json_name)
