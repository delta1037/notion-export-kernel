# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com
import copy
import os
import logging
import shutil

import NotionDump
from NotionDump.Notion.Notion import NotionQuery
from NotionDump.Parser.page_parser import PageParser
from NotionDump.Parser.database_parser import DatabaseParser
from NotionDump.utils import common_op
from NotionDump.utils import internal_var


class Page:
    # 初始化
    def __init__(self, page_id, query_handle: NotionQuery, export_child_pages=False):
        self.page_id = page_id.replace('-', '')
        self.query_handle = query_handle

        # 这里传入handle是为了子块的解析
        self.page_parser = PageParser(self.page_id, self.query_handle, parser_type=internal_var.PARSER_TYPE_MD)
        # 初始化一个Database对象，这里page id无关紧要
        self.database_parser = DatabaseParser(self.page_id)
        # 页面的操作就是块的操作
        # self.block_handle = Block(block_id=self.page_id)

        # 创建临时文件夹
        self.tmp_dir = NotionDump.TMP_DIR
        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)

        # 是否导出子页面
        self.export_child_page = export_child_pages

    # show_child_page
    @staticmethod
    def get_pages_detail():
        return internal_var.PAGE_DIC

    def __test_show_child_page(self):
        print("in page_id: ", self.page_id, internal_var.PAGE_DIC)

    # 获取到所有的PAGE数据
    def page_to_md(self, md_name=None):
        page_json = self.query_handle.retrieve_block_children(self.page_id)
        if page_json is None:
            return False
        # 解析到临时文件中
        tmp_md_filename = self.page_parser.page_to_md(page_json)

        # 更新已经获取到的页面的状态(现有内容，再更新状态)
        common_op.update_child_page_stats(self.page_id, dumped=True, main_page=True,
                                          local_path=tmp_md_filename)
        common_op.update_page_recursion(self.page_id, recursion=True)
        # 从页面里获取到所有的子页面,并将子页面添加到父id中
        common_op.update_child_pages(self.page_parser.get_child_pages_dic(), self.page_id)
        if md_name is not None:
            shutil.copyfile(tmp_md_filename, md_name)

        if self.export_child_page:
            self.__recursion_child_page()
        if md_name is not None:
            return md_name
        return tmp_md_filename

    def __recursion_child_page(self):
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
                    tmp_filename = self.page_parser.page_to_md(page_json, new_id=child_id)
                    child_pages_dic = self.page_parser.get_child_pages_dic()
                else:
                    # page里面搞一个Database的解析器
                    db_json = self.query_handle.query_database(child_id)
                    if db_json is None:
                        logging.log(logging.ERROR, "get page error, id=" + child_id)
                        continue
                    # 获取解析后的数据
                    tmp_filename = self.database_parser.database_to_csv(db_json, new_id=child_id)
                    child_pages_dic = self.database_parser.get_child_page_dic()

                # 再更新本地的存放路径
                common_op.update_child_page_stats(child_id, dumped=True, local_path=tmp_filename)
                # 从页面里获取到所有的子页面,并将子页面添加到父id中
                common_op.update_child_pages(child_pages_dic, child_id)

                # 调试
                if NotionDump.DUMP_DEBUG:
                    print("# end child_page_id=", child_id)
                    print(self.__test_show_child_page())
        if update_flag:
            self.__recursion_child_page()

    def page_to_db(self):
        # 从配置文件中获取数据库配置，打开数据库，并将csv文件写入到数据库中
        page_json = self.query_handle.retrieve_block_children(self.page_id)
        if page_json is None:
            return None

        # tmp_csv_filename = self.database_parser.database_to_csv(db_json, col_name_list)
        # TODO 将Md文件写入到数据库;调用SQL中的notion2sql提供的接口
        return

    # 源文件，直接输出成json; 辅助测试使用
    def page_to_json(self, json_name=None):
        page_json = self.query_handle.retrieve_block_children(self.page_id)
        if page_json is None:
            return None

        if json_name is None:
            json_name = self.tmp_dir + self.page_id + ".json"
        common_op.save_json_to_file(page_json, json_name)
        return
