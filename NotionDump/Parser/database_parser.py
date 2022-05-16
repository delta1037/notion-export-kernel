# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com

import csv
import os

import NotionDump
from NotionDump.Parser.base_parser import BaseParser
from NotionDump.utils import common_op


class DatabaseParser:
    def __init__(
            self,
            database_id,
            parser_type=NotionDump.PARSER_TYPE_PLAIN,
            export_child_pages=False
    ):
        self.database_id = database_id.replace('-', '')
        self.parser_type = parser_type
        # 是否导出子页面,也就是递归操作
        self.export_child_page = export_child_pages

        self.tmp_dir = NotionDump.TMP_DIR
        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)

        # 块解析器
        self.base_parser = BaseParser(
            base_id=self.database_id,
            export_child=self.export_child_page
        )

    # 从一个页面里把列名给解析出来
    def __get_col_name_list(self, one_page):
        col_name_list = []
        title_name = ""
        for item in one_page["properties"]:
            if one_page["properties"][item]["type"] == "title":
                title_name = item
            else:
                col_name_list.append(item)
        if title_name == "":
            common_op.debug_log("col name no title error! id=" + self.database_id, level=NotionDump.DUMP_MODE_DEFAULT)
            return ""
        col_name_list.append(title_name)  # 把title_name放在最后一个，逆序之后就是第一个
        # 根据现有的数据库看来这里需要逆序一下才和实际的数据库一致
        col_name_list.reverse()
        return col_name_list

    def get_child_pages_dic(self):
        return self.base_parser.get_child_pages_dic()

    # 解析一列中的一项
    def __parser_item(self, item_block, page_id):
        item_ret = ""
        if item_block["type"] == "title":  # title
            item_ret = self.base_parser.title_parser(item_block, page_id, parser_type=self.parser_type)
        elif item_block["type"] == "multi_select":  # multi_select
            item_ret = self.base_parser.multi_select_parser(item_block, parser_type=self.parser_type)
        elif item_block["type"] == "select":
            item_ret = self.base_parser.select_parser(item_block, parser_type=self.parser_type)
        elif item_block["type"] == "rich_text":
            item_ret = self.base_parser.rich_text_parser(item_block, parser_type=self.parser_type)
        elif item_block["type"] == "url":
            item_ret = self.base_parser.url_parser(item_block)
        elif item_block["type"] == "email":
            item_ret = self.base_parser.email_parser(item_block)
        elif item_block["type"] == "checkbox":
            item_ret = self.base_parser.checkbox_parser(item_block)
        elif item_block["type"] == "phone_number":
            item_ret = self.base_parser.phone_number_parser(item_block)
        elif item_block["type"] == "date":
            item_ret = self.base_parser.date_parser(item_block)
        elif item_block["type"] == "people":
            item_ret = self.base_parser.people_parser(item_block)
        elif item_block["type"] == "number":
            item_ret = self.base_parser.number_parser(item_block)
        elif item_block["type"] == "files":
            item_ret = self.base_parser.files_parser(item_block, parser_type=self.parser_type)
        elif item_block["type"] == "relation":
            item_ret = self.base_parser.relation_parser(item_block)
        elif item_block["type"] == "rollup":
            # rollup类型单独解析
            rollup_block = item_block["rollup"]
            if "array" in rollup_block:
                for rollup_item in rollup_block["array"]:
                    if item_ret != "":
                        item_ret += ","
                    item_ret += self.__parser_item(rollup_item, "")
        elif item_block["type"] == "formula":
            item_ret = self.base_parser.formula_parser(item_block)
        elif item_block["type"] == "created_time":
            item_ret = self.base_parser.created_time_parser(item_block)
        elif item_block["type"] == "last_edited_time":
            item_ret = self.base_parser.last_edited_time_parser(item_block)
        elif item_block["type"] == "created_by":
            item_ret = self.base_parser.created_by_parser(item_block)
        elif item_block["type"] == "last_edited_by":
            item_ret = self.base_parser.last_edited_by_parser(item_block)
        else:
            item_ret = "[unknown_type:" + item_block["type"] + "]"
            common_op.debug_log("[ISSUE] unknown properties type:" + item_block["type"], level=NotionDump.DUMP_MODE_DEFAULT)

        return item_ret

    def database_to_md(self, page_properties, new_id=None):
        if page_properties is None:
            return ""
        # 获取属性部分
        if "properties" not in page_properties:
            return ""
        page_properties = page_properties["properties"]

        # 设置基础解析器的id
        if new_id is not None:
            self.base_parser.set_new_id(new_id)

        # 数据库是空的，直接返回完事
        if len(page_properties) == 0:
            return ""

        properties_md = "|KEY|VALUE|\n|---|---|"
        # print(page_properties.keys())
        p_title = ""
        for p_name in list(page_properties.keys())[::-1]:
            p_value = self.__parser_item(page_properties[p_name], page_id="")
            if page_properties[p_name]["type"] == "title":
                p_title = p_value
            # print(p_value, p_name)
            properties_md += "\n" + "|" + str(p_name) + "|" + str(p_value) + "|"
        if p_title != "":
            properties_md = "# " + p_title + "\n" + properties_md
        return properties_md

    # 格式化存储，这里是临时文件存在方式（在外面转成数据库，或者最终输出CSV的格式）
    def database_to_file(self, database_handle, col_name_list=None, new_id=None):
        page_list = database_handle.get("results")
        # 数据库是空的，直接返回完事
        if len(page_list) == 0:
            return ""

        # col_name_list 是想要的列，并且会按照该顺序输出；如果没有给定则获取所有列
        if col_name_list is None:
            # 如果没有给定输出顺序，则获取到page中的所有列（注意不保证是显示的顺序！！！！）
            col_name_list = self.__get_col_name_list(page_list[0])

        # 创建文件
        suffix = ".csv"
        if self.parser_type == NotionDump.PARSER_TYPE_MD:
            suffix = ".md"
        if new_id is not None:
            self.base_parser.set_new_id(new_id)
            tmp_filename = self.tmp_dir + new_id.replace('-', '') + suffix
        else:
            tmp_filename = self.tmp_dir + self.database_id + suffix

        file = open(tmp_filename, "w", encoding="utf-8", newline='')

        csv_writer = None
        if self.parser_type == NotionDump.PARSER_TYPE_MD:
            head_line = "|"
            for it in col_name_list:
                head_line += it + "|"
            head_line += "\n|"
            for i in range(len(col_name_list)):
                head_line += " --- " + "|"
            file.write(head_line + "\n")
        else:
            csv_writer = csv.writer(file)
            # 首先将列的名称写入到CSV文件中
            csv_writer.writerow(col_name_list)

        # 返回的内容好像是倒序的，先倒置过来吧
        page_list.reverse()
        # 解析每一个page的内容
        for page in page_list:
            # 每一个page都有page id
            page_id = page["id"].replace('-', '')
            common_op.debug_log("database page id" + page_id)
            page_iter = []
            for item in col_name_list:
                # 解析每一个方格的内容
                page_iter.append(self.__parser_item(page["properties"][item], page_id))
            # 将内容填充到文件中
            if self.parser_type == NotionDump.PARSER_TYPE_MD:
                page_line = "|"
                for it in page_iter:
                    if isinstance(it, str):
                        page_line += it.replace('\n', '<br>') + "|"
                    else:
                        page_line += str(it) + "|"
                file.write(page_line + "\n")
            else:
                if csv_writer is not None:
                    csv_writer.writerow(page_iter)
                    common_op.debug_log("database page " + page_id + " write csv success")
                else:
                    common_op.debug_log("database page " + page_id + " write csv fail", level=NotionDump.DUMP_MODE_DEFAULT)
        file.flush()
        file.close()

        common_op.debug_log("write file " + tmp_filename, level=NotionDump.DUMP_MODE_DEFAULT)
        # 将临时文件地址转出去，由外面进行进一步的操作
        return tmp_filename

    def database_to_dic(self, database_handle, col_name_list=None, new_id=None):
        page_list = database_handle.get("results")
        # 数据库是空的，直接返回完事
        if len(page_list) == 0:
            return

        # col_name_list 是想要的列，并且会按照该顺序输出；如果没有给定则获取所有列
        if col_name_list is None:
            # 如果没有给定输出顺序，则获取到page中的所有列（注意不保证是显示的顺序！！！！）
            col_name_list = self.__get_col_name_list(page_list[0])

        # 返回的内容好像是倒序的，先倒置过来吧
        page_list.reverse()

        db_dic = []
        # 解析每一个page的内容
        for page in page_list:
            # 每一个page都有page id
            page_id = page["id"].replace('-', '')
            common_op.debug_log("database page id" + page_id)
            db_dic_line = {"_page_id": page_id}
            for item in col_name_list:
                # 解析每一个方格的内容
                db_dic_line[item] = self.__parser_item(page["properties"][item], page_id)
            # 将内容填充list中
            db_dic.append(db_dic_line)
            common_op.debug_log("database page " + page_id + " get dic success")

        # 将临时文件地址转出去，由外面进行进一步的操作
        return db_dic
