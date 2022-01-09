# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com
import os
import logging
import NotionDump
from NotionDump.Parser.block_parser import BlockParser


class PageParser:
    def __init__(self, page_id, token=None, client_handle=None, async_api=False, parser_type=NotionDump.PARSER_TYPE_PLAIN):
        self.page_id = page_id
        self.tmp_dir = NotionDump.TMP_DIR
        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)
        self.block_parser = BlockParser(block_id=self.page_id)
        self.parser_type = parser_type

    @staticmethod
    def __newline(last_type, now_type):
        if last_type == "to_do" and now_type == "to_do":
            return False
        if last_type == "numbered_list_item" and now_type == "numbered_list_item":
            return False
        if last_type == "bulleted_list_item" and now_type == "bulleted_list_item":
            return False
        return True

    def page_to_md(self, page_handle):
        block_list = page_handle["results"]
        # 数据库是空的，直接返回完事
        if len(block_list) == 0:
            return

        # 创建Markdown文件
        tmp_md_filename = self.tmp_dir + self.page_id + ".md"
        file = open(tmp_md_filename, "w", encoding="utf-8", newline='')

        block_text = ""
        last_type = "to_do"  # 初始化不换行
        list_index = 1
        for block in block_list:
            # 遍历block，解析内容，填充到md文件中
            block_type = block["type"]
            if self.__newline(last_type, block_type) and block_text != "":
                block_text += "\n"
            if last_type == "numbered_list_item":
                list_index = list_index + 1
            else:
                list_index = 1
            last_type = block_type
            if block_type == "paragraph":
                # Page paragraph
                block_text += self.block_parser.paragraph_parser(block, self.parser_type)
            elif block_type == "heading_1":
                # Page heading_1
                block_text += self.block_parser.heading_1_parser(block, self.parser_type)
            elif block_type == "heading_2":
                # Page heading_2
                block_text += self.block_parser.heading_2_parser(block, self.parser_type)
            elif block_type == "heading_3":
                # Page heading_3
                block_text += self.block_parser.heading_3_parser(block, self.parser_type)
            elif block_type == "to_do":
                # Page to_do
                block_text += self.block_parser.to_do_parser(block, self.parser_type)
            elif block_type == "bulleted_list_item":
                # Page bulleted_list_item
                block_text += self.block_parser.bulleted_list_item_parser(block, self.parser_type)
            elif block_type == "numbered_list_item":
                # Page numbered_list_item
                block_text += self.block_parser.numbered_list_item_parser(block, list_index, self.parser_type)
            elif block_type == "toggle":
                # Page toggle
                block_text += self.block_parser.toggle_parser(block, self.parser_type)
            elif block_type == "divider":
                # Page divider
                block_text += self.block_parser.divider_parser(block, self.parser_type)
            elif block_type == "callout":
                # Page callout
                block_text += self.block_parser.callout_parser(block, self.parser_type)
            elif block_type == "code":
                # Page code
                block_text += self.block_parser.code_parser(block, self.parser_type)
            elif block_type == "quote":
                # Page quote
                block_text += self.block_parser.quote_parser(block, self.parser_type)
            elif block_type == "equation":
                # Page equation
                block_text += self.block_parser.equation_parser(block, self.parser_type)
            elif block_type == "table":
                # Page table
                block_text += self.block_parser.table_parser(block, self.parser_type)
            else:
                logging.exception("unknown properties type:" + block_type)

            block_text += "\n"

        file.write(block_text)
        file.flush()
        file.close()
        # 将临时文件地址转出去，由外面进行进一步的操作
        return tmp_md_filename
