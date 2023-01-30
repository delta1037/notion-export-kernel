# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com

import os

import NotionDump
from NotionDump.Notion.Notion import NotionQuery
from NotionDump.Parser.base_parser import BaseParser
from NotionDump.utils import common_op


# Block内容解析
class BlockParser:
    # 初始化
    def __init__(
            self,
            block_id,
            query_handle: NotionQuery,
            parser_type=NotionDump.PARSER_TYPE_MD,
            export_child_pages=False
    ):
        self.block_id = block_id.replace('-', '')
        self.query_handle = query_handle
        self.parser_type = parser_type
        # 是否导出子页面,也就是递归操作
        self.export_child_page = export_child_pages

        # 创建临时文件夹
        self.tmp_dir = NotionDump.TMP_DIR
        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)

        # 基解析器
        self.base_parser = BaseParser(
            base_id=self.block_id,
            export_child=self.export_child_page
        )

    # 获取子页面字典
    def get_child_pages_dic(self):
        return self.base_parser.get_child_pages_dic()

    def __get_children_block_list(self, block):
        # 如果没有子页面，直接返回空
        if not block["has_children"]:
            return None

        if block["type"] == 'child_page':
            return None

        # 递归黑名单
        if block["type"] == "template":
            common_op.debug_log("type " + block["type"] + " has no child, ignore", level=NotionDump.DUMP_MODE_DEFAULT)
            return None

        # 指定类型才递归(白名单)
        if block["type"] != "to_do" \
                and block["type"] != "numbered_list_item" \
                and block["type"] != "bulleted_list_item" \
                and block["type"] != "toggle" \
                and block["type"] != "table" \
                and block["type"] != "table_row"\
                and block["type"] != "column_list" \
                and block["type"] != "column" \
                and block["type"] != "synced_block" \
                and block["type"] != "heading_1" \
                and block["type"] != "heading_2" \
                and block["type"] != "heading_3" \
                and block["type"] != "paragraph" \
                and block["type"] != "quote" \
                and block["type"] != "callout":
            common_op.debug_log("[ISSUE] type " + block["type"] + " has no child", level=NotionDump.DUMP_MODE_DEFAULT)
            return None

        # 获取块id下面的内容并继续解析
        if block["type"] == "synced_block" and block["synced_block"]["synced_from"] is not None:
            child_block_id = block["synced_block"]["synced_from"]["block_id"]
            common_op.debug_log("type synced_block " + child_block_id + " get child", level=NotionDump.DUMP_MODE_DEFAULT)
        else:
            child_block_id = block["id"]

        block_list = []
        retrieve_ret = self.query_handle.retrieve_block_children(child_block_id, parent_id=self.block_id)
        if retrieve_ret is not None:
            block_list = retrieve_ret["results"]

        # 如果没有获取到块，也返回空
        if len(block_list) == 0:
            return None
        # 返回获取到的块列表
        common_op.debug_log("## retrieve block " + child_block_id, level=NotionDump.DUMP_MODE_DEFAULT)
        return block_list

    def parser_block(self, block, list_index, last_line_is_table, prefix):
        block_type = block["type"]
        block_text = ""
        if block_type == "paragraph":
            # paragraph
            block_text = self.base_parser.paragraph_parser(block, self.parser_type)
        elif block_type == "heading_1":
            # heading_1
            block_text = self.base_parser.heading_1_parser(block, self.parser_type)
        elif block_type == "heading_2":
            # heading_2
            block_text = self.base_parser.heading_2_parser(block, self.parser_type)
        elif block_type == "heading_3":
            # heading_3
            block_text = self.base_parser.heading_3_parser(block, self.parser_type)
        elif block_type == "to_do":
            # to_do
            block_text = self.base_parser.to_do_parser(block, self.parser_type)
        elif block_type == "bulleted_list_item":
            # bulleted_list_item
            block_text = self.base_parser.bulleted_list_item_parser(block, self.parser_type)
        elif block_type == "numbered_list_item":
            # numbered_list_item
            block_text = self.base_parser.numbered_list_item_parser(block, list_index, self.parser_type)
        elif block_type == "toggle":
            # toggle
            block_text = self.base_parser.toggle_parser(block, self.parser_type)
        elif block_type == "divider":
            # divider
            block_text = self.base_parser.divider_parser(block)
        elif block_type == "callout":
            # callout
            block_text = self.base_parser.callout_parser(block, self.parser_type)
            # callout内换行使用HTML符号
            block_text = block_text.replace('\n', '<br>')
        elif block_type == "code":
            # code
            code_text = self.base_parser.code_parser(block, self.parser_type)
            block_text = code_text.replace('\n', '\n'+prefix)
        elif block_type == "quote":
            # quote
            block_text = self.base_parser.quote_parser(block, self.parser_type)
        elif block_type == "equation":
            # Page equation
            block_text = self.base_parser.equation_parser(block)
        elif block_type == "table":
            # table直接递归即可
            pass
        elif block_type == "table_row":
            # Page table_row
            block_text = self.base_parser.table_row_parser(
                block,
                first_row=last_line_is_table,
                parser_type=self.parser_type
            )
        elif block_type == "child_page":
            # Page child_page 子页面只返回链接，不返回内容
            block_text = self.base_parser.child_page_parser(block, self.parser_type)
        elif block_type == "child_database":
            # Page child_database
            # Page中嵌套数据库的类型，只保存页面，不进行解析
            block_text = self.base_parser.child_database_parser(block, self.parser_type)
        elif block_type == "image":
            # Page image
            block_text = self.base_parser.image_parser(block, self.parser_type)
        elif block_type == "file" or block_type == "pdf" or block_type == "video":
            # Page file
            block_text = self.base_parser.file_parser(block, self.parser_type)
        elif block_type == "bookmark":
            # Page bookmark
            block_text = self.base_parser.bookmark_parser(block, self.parser_type)
        elif block_type == "embed":
            # Page embed
            block_text = self.base_parser.embed_parser(block, self.parser_type)
        elif block_type == "link_preview":
            # Page bookmark
            block_text = self.base_parser.link_preview_parser(block, self.parser_type)
        elif block_type == "link_to_page":
            # Page link_to_page
            block_text = self.base_parser.link_to_page_parser(block, self.parser_type)
        elif block_type == "table_of_contents":
            block_text = '[TOC]'
        elif block_type == "template":
            # 模板内容不解析
            block_text = '[TEMPLATE]'
        elif block_type == "breadcrumb":
            # 路径信息不解析（notion也不会返回）
            block_text = "[breadcrumb]"
        else:
            common_op.debug_log("[ISSUE] unknown page block properties type:" + block_type, level=NotionDump.DUMP_MODE_DEFAULT)
            block_text = "[unknown_type:" + block_type + "]"
        if block_text is None:
            block_text = ""
        return block_text

    def parser_block_list(self, block_list, indent=0, line_div="\n", last_block_type="none"):
        prefix = ""
        p_index = 0
        # line_div 为br时，是内部换行，\n时是大块换行
        while p_index < indent and line_div == "\n":
            prefix += "\t"  # 前缀是一个TAB
            p_index += 1

        # 如果有内容先加个换行再说
        block_text = ""
        if indent != 0 and line_div == "\n":
            block_text = line_div

        last_type = "to_do"  # 初始化不换行
        list_index = 1

        # 记录解析到的表格的状态，表格会一次性解析完，所以这里不需要重新设置
        last_line_is_table = True

        for block in block_list:
            # 遍历block，解析内容，填充到md文件中
            block_type = block["type"]

            # 在外面解析列类型
            if block_type == "column_list":
                # 列类型的分解
                column_list = self.__get_children_block_list(block)
                if block_text == "\n":
                    # 如果只有一个换行符，重置内容
                    block_text = ""
                if column_list is not None:
                    for column in column_list:
                        column_rows = self.__get_children_block_list(column)
                        if column_rows is not None:
                            if block_text != "":
                                # 与前边得隔离开
                                block_text += "\n"
                            block_text += self.parser_block_list(column_rows, indent)
            elif block_type == "synced_block":
                # 同步块解析其中的内容
                synced_block_list = self.__get_children_block_list(block)
                if block_text == "\n":
                    # 如果只有一个换行符，重置内容
                    block_text = ""
                if synced_block_list is not None:
                    block_text += self.parser_block_list(synced_block_list, indent, last_block_type="synced_block")
            else:
                # 如果是连续的类型，就不需要额外加换行符
                if common_op.parser_newline(last_type, block_type) and block_text != "" and block_text != "\n":
                    block_text += line_div

                # 记录数字列表的标识
                if last_type == "numbered_list_item":
                    list_index = list_index + 1
                else:
                    list_index = 1
                last_type = block_type
                if block_type != "table" and block_type != "table_row":
                    block_text += prefix

                block_text += self.parser_block(
                    block=block,
                    list_index=list_index,
                    last_line_is_table=last_line_is_table,
                    prefix=prefix
                )

                # 看改块下面有没有子块，如果有就继续解析
                children_block_list = self.__get_children_block_list(block)
                t_line_div = "\n"
                if block_type == "quote" or block_type == "callout":
                    t_line_div = "<br>"
                if children_block_list is not None:
                    if block_type == "heading_1" \
                            or block_type == "heading_2" \
                            or block_type == "heading_3" \
                            or block_type == "paragraph" \
                            or block_type == "quote" \
                            or block_type == "callout":
                        # 不需要加大indent值
                        # if block_type != "quote" and block_type != "callout":
                        #     # 处理quote和callout内部的换行问题
                        block_text += t_line_div
                        block_text += self.parser_block_list(children_block_list, indent, line_div=t_line_div)
                    else:
                        block_text += self.parser_block_list(children_block_list, indent + 1)
                else:
                    block_text += "\n"

            if block_type == "table_row":
                # 第一行设置首行标志
                last_line_is_table = False

        return block_text

    def block_to_md(self, block_handle, page_detail=None, new_id=None):
        block_list = block_handle["results"]
        # 空内容不生成文件
        if len(block_list) == 0 and (page_detail is None or page_detail == ""):
            return ""

        # 创建Markdown文件
        if new_id is not None:
            self.block_id = new_id.replace('-', '')
            self.base_parser.set_new_id(self.block_id)
        tmp_md_filename = self.tmp_dir + self.block_id + ".md"
        file = open(tmp_md_filename, "w", encoding="utf-8", newline='')

        # 如果存在属性就拼接上去
        block_text = ""
        if page_detail is not None and page_detail != "":
            block_text = page_detail + "\n" + NotionDump.MD_DIVIDER + "\n"

        # 解析block_list
        block_text += self.parser_block_list(block_list)

        # 将解析内容写入文件
        file.write(block_text)
        file.flush()
        file.close()

        common_op.debug_log("write file " + tmp_md_filename, level=NotionDump.DUMP_MODE_DEFAULT)
        # 将临时文件地址转出去，由外面进行进一步的操作
        return tmp_md_filename

    # 源文件，直接输出成json; 辅助测试使用
    def block_to_json(self, block_json, json_name=None):
        if block_json is None:
            return None

        if json_name is None:
            json_name = self.tmp_dir + self.block_id + ".json"
        common_op.save_json_to_file(block_json, json_name)
