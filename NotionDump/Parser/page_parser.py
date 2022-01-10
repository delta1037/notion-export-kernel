# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com
import os
import logging
from notion_client import Client, AsyncClient

import NotionDump
from NotionDump.utils import internal_var
from NotionDump.Api.database import Database
from NotionDump.Api.block import Block
from NotionDump.Parser.block_parser import BlockParser


class PageParser:
    def __init__(self, page_id, token=None, client_handle=None, async_api=False,
                 parser_type=internal_var.PARSER_TYPE_PLAIN):
        self.token = token
        self.page_id = page_id.replace('-', '')

        # 创建临时文件夹
        self.tmp_dir = NotionDump.TMP_DIR
        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)

        if client_handle is None and token is not None:
            # 有的token话就初始化一下
            if not async_api:
                self.client = Client(auth=self.token)
            else:
                self.client = AsyncClient(auth=self.token)
        else:
            # 没有token，传进来handle就用，没传就不用
            self.client = client_handle
        if self.client is None:
            logging.exception("page parser init fail, client = NULL, page_id=" + self.page_id)
        self.block_parser = BlockParser(block_id=self.page_id)
        self.parser_type = parser_type

    # 获取子页面字典
    def get_child_pages_dic(self):
        return self.block_parser.get_child_pages_dic()

    # 判断是否添加额外的换行
    @staticmethod
    def __newline(last_type, now_type):
        if last_type == "to_do" and now_type == "to_do":
            return False
        if last_type == "numbered_list_item" and now_type == "numbered_list_item":
            return False
        if last_type == "bulleted_list_item" and now_type == "bulleted_list_item":
            return False
        if last_type == "toggle" and now_type == "toggle":
            return False
        # 处理表格类型
        if last_type == "table" and now_type == "table_row":
            return False
        if last_type == "table_row" and now_type == "table_row":
            return False
        return True

    def __get_children_block_list(self, block):
        # 如果没有子页面，直接返回空
        if not block["has_children"]:
            return None

        # 指定类型才递归
        if block["type"] != "todo" \
                and block["type"] != "numbered_list_item" \
                and block["type"] != "bulleted_list_item" \
                and block["type"] != "toggle" \
                and block["type"] != "table"\
                and block["type"] != "table_row":
            return None

        # 获取块id下面的内容并继续解析
        block_handle = Block(block["id"].replace('-', ''), token=self.token, client_handle=self.client)
        # export_json=True 测试时导出json文件
        block_list = block_handle.retrieve_block_children()["results"]
        # 如果没有获取到块，也返回空
        if len(block_list) == 0:
            return None
        # 返回获取到的块列表
        return block_list

    def __parser_block_list(self, block_list, indent=0):
        prefix = ""
        p_index = 0
        while p_index < indent:
            prefix += "\t"  # 前缀是一个TAB
            p_index += 1
        # 测试一下有多宽
        # print("|" + prefix + "|")

        # 如果有内容先加个换行再说
        block_text = ""
        if indent != 0:
            block_text = "\n"

        last_type = "to_do"  # 初始化不换行
        list_index = 1

        # 记录解析到的表格的状态，表格会一次性解析完，所以这里不需要重新设置
        last_line_is_table = True

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
            if block_type != "table" and block_type != "table_row":
                block_text += prefix
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
                block_text += self.block_parser.divider_parser(block)
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
                block_text += self.block_parser.equation_parser(block)
            elif block_type == "table":
                # table直接递归即可
                pass
            elif block_type == "table_row":
                # Page child_database
                block_text += self.block_parser.table_row_parser(
                    block,
                    first_row=last_line_is_table,
                    parser_type=self.parser_type
                )
                # 第一行设置首行标志
                last_line_is_table = False
            elif block_type == "child_page":
                # Page child_page 子页面只返回链接，不返回内容
                # print("child_page", self.block_parser.child_page_parser(block, self.parser_type))
                block_text += self.block_parser.child_page_parser(block, self.parser_type)
            elif block_type == "child_database":
                # Page child_database
                # Page中嵌套数据库的类型
                db_handle = Database(database_id=block["id"], token=self.token, client_handle=self.client)
                db_handle.database_to_csv()
            else:
                logging.exception("unknown page block properties type:" + block_type)

            # 看改块下面有没有子块，如果有就继续解析
            children_block_list = self.__get_children_block_list(block)
            if children_block_list is not None:
                block_text += self.__parser_block_list(children_block_list, indent + 1)
            block_text += "\n"
        return block_text

    def page_to_md(self, page_handle, new_id=None):
        block_list = page_handle["results"]
        # 数据库是空的，直接返回完事
        if len(block_list) == 0:
            return

        # 创建Markdown文件
        if new_id is not None:
            tmp_md_filename = self.tmp_dir + new_id.replace('-', '') + ".md"
        else:
            tmp_md_filename = self.tmp_dir + self.page_id + ".md"

        file = open(tmp_md_filename, "w", encoding="utf-8", newline='')
        # 解析block_list
        block_text = self.__parser_block_list(block_list)

        # 将解析内容写入文件
        file.write(block_text)
        file.flush()
        file.close()

        # print("write file " + tmp_md_filename)
        # 将临时文件地址转出去，由外面进行进一步的操作
        return tmp_md_filename
