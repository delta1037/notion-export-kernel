# author: delta1037
# Date: 2022/01/10
# mail:geniusrabbit@qq.com
import copy
import os
import logging

import NotionDump
from NotionDump.Notion.Notion import NotionQuery
from NotionDump.Parser.block_parser import BlockParser
from NotionDump.Parser.database_parser import DatabaseParser
from NotionDump.utils import common_op, internal_var


# 混合递归调用，主要是为Page和Database类型
class MixParser:
    # 初始化
    def __init__(self, mix_id, query_handle: NotionQuery, export_child_pages=False, parser_type=internal_var.PARSER_TYPE_MD):
        self.mix_id = mix_id
        self.query_handle = query_handle
        self.parser_type = parser_type
        # 是否导出子页面,也就是递归操作
        self.export_child_page = export_child_pages

        # 创建临时文件夹
        self.tmp_dir = NotionDump.TMP_DIR
        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)

        # 解析器
        # 这里传入handle是为了子块的解析
        self.block_parser = BlockParser(self.mix_id, self.query_handle, parser_type=self.parser_type)
        # 初始化一个Database对象，这里page id无关紧要
        self.database_parser = DatabaseParser(self.mix_id, parser_type=self.parser_type)

    # 调试时显示子页面内容
    def __test_show_child_page(self):
        print("in page_id: ", self.mix_id, internal_var.PAGE_DIC)

    def __recursion_mix_parser(self):
        update_flag = False
        recursion_page = copy.deepcopy(internal_var.PAGE_DIC)
        for child_id in recursion_page:
            # 判断页面是否已经操作过
            if common_op.is_page_recursion(child_id):
                update_flag = True
                # 调试
                if NotionDump.DUMP_DEBUG:
                    print("# start child_page_id=", child_id)
                    print(self.__test_show_child_page())
                # 先更新页面的状态，无论获取成功或者失败都过去了，只获取一次
                common_op.update_page_recursion(child_id, recursion=True)

                if common_op.is_page(child_id):
                    page_json = self.query_handle.retrieve_block_children(child_id)
                    if page_json is None:
                        logging.log(logging.ERROR, "get page error, id=" + child_id)
                        continue
                    # 解析到临时文件中
                    tmp_filename = self.block_parser.block_to_md(page_json, new_id=child_id)
                    child_pages_dic = self.block_parser.get_child_pages_dic()
                else:
                    # page里面搞一个Database的解析器
                    db_json = self.query_handle.query_database(child_id)
                    if db_json is None:
                        logging.log(logging.ERROR, "get page error, id=" + child_id)
                        continue
                    # 获取解析后的数据
                    tmp_filename = self.database_parser.database_to_csv(db_json, new_id=child_id)
                    child_pages_dic = self.database_parser.get_child_pages_dic()

                # 再更新本地的存放路径
                common_op.update_child_page_stats(child_id, dumped=True, local_path=tmp_filename)
                # 从页面里获取到所有的子页面,并将子页面添加到父id中
                common_op.update_child_pages(child_pages_dic, child_id)

                # 调试
                if NotionDump.DUMP_DEBUG:
                    print("# end child_page_id=", child_id)
                    print(self.__test_show_child_page())
        if update_flag:
            self.__recursion_mix_parser()

    def mix_parser(self, json_handle, json_type):
        # 解析到临时文件中
        if json_type == "database":
            # 注意这里把数据库里所有的字段都捞出来了
            tmp_filename = self.database_parser.database_to_csv(json_handle)
        elif json_type == "block":
            tmp_filename = self.block_parser.block_to_md(json_handle)
        else:
            logging.exception("unknown parser_type:" + json_type)
            return None

        # 更新已经获取到的页面的状态(现有内容，再更新状态)
        common_op.update_child_page_stats(self.mix_id, dumped=True, main_page=True,
                                          local_path=tmp_filename)
        common_op.update_page_recursion(self.mix_id, recursion=True)
        # 从页面里获取到所有的子页面,并将子页面添加到父id中
        if json_type == "database":
            common_op.update_child_pages(self.database_parser.get_child_pages_dic(), self.mix_id)
        elif json_type == "block":
            common_op.update_child_pages(self.block_parser.get_child_pages_dic(), self.mix_id)
        else:
            logging.exception("unknown parser_type:" + json_type)
            return None

        if self.export_child_page:
            self.__recursion_mix_parser()

        return tmp_filename
