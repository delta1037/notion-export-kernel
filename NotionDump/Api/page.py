# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com

import os
import logging
import shutil

from notion_client import Client, AsyncClient
from notion_client import APIErrorCode, APIResponseError

import NotionDump
from NotionDump.Parser.page_parser import PageParser
from NotionDump.Api.block import Block
from NotionDump.utils import common_op
from NotionDump.utils import internal_var


class Page:
    # 初始化
    def __init__(self, page_id, token, client_handle=None, async_api=False, export_child_pages=False):
        self.token = token
        self.page_id = page_id.replace('-', '')
        if client_handle is None:
            if not async_api:
                self.client = Client(auth=self.token)
            else:
                self.client = AsyncClient(auth=self.token)
        else:
            self.client = client_handle
        # 这里传入handle是为了子块的解析
        self.page_parser = PageParser(self.page_id, client_handle=self.client,
                                      parser_type=internal_var.PARSER_TYPE_MD)
        # 页面的操作就是块的操作
        self.block_handle = Block(
            block_id=self.page_id,
            token=self.token,
            client_handle=self.client
        )

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

    # 获取Page的信息
    def retrieve_page(self):
        try:
            return self.client.pages.retrieve(page_id=self.page_id)
        except APIResponseError as error:
            if NotionDump.DUMP_DEBUG:
                if error.code == APIErrorCode.ObjectNotFound:
                    logging.exception("Page Retrieve is invalid, id=" + self.page_id)
                else:
                    # Other error handling code
                    logging.exception(error)
            else:
                logging.exception("Page Retrieve is invalid, id=" + self.page_id)
        except Exception as e:
            if NotionDump.DUMP_DEBUG:
                logging.exception(e)
            else:
                logging.exception("Page Retrieve Not found or no authority, id=" + self.page_id)
        return None

    # 获取Page的所有块(这里page相当于是一个母块，要获取改母块下所有的子块)
    def query_page(self):
        return self.block_handle.retrieve_block_children()

    # 获取到所有的PAGE数据
    def page_to_md(self, md_name=None):
        page_json = self.query_page()
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
        return True

    def __recursion_child_page(self):
        update_flag = False
        for page_id in internal_var.PAGE_DIC:
            # print("page id " + page_id)
            # self.__test_show_child_page()
            if common_op.is_page_recursion(page_id):
                update_flag = True
                # print("begin")
                # self.__test_show_child_page()
                block_handle = Block(page_id, self.token, self.client)
                page_json = block_handle.retrieve_block_children()
                # 先更新页面的状态，无论获取成功或者失败都过去了，只获取一次
                common_op.update_page_recursion(page_id, recursion=True)
                if page_json is None:
                    logging.log(logging.ERROR, "get page error, id=" + page_id)
                    continue

                # 解析到临时文件中
                # print("parser page id " + page_id)
                tmp_md_filename = self.page_parser.page_to_md(page_json, new_id=page_id)
                # 再更新本地的存放路径
                common_op.update_child_page_stats(page_id, dumped=True, local_path=tmp_md_filename)
                # 从页面里获取到所有的子页面,并将子页面添加到父id中
                common_op.update_child_pages(self.page_parser.get_child_pages_dic(), page_id)
                # print("end")
                # self.__test_show_child_page()
        if update_flag:
            self.__recursion_child_page()

    def page_to_db(self):
        # 从配置文件中获取数据库配置，打开数据库，并将csv文件写入到数据库中
        page_json = self.query_page()
        if page_json is None:
            return None

        # tmp_csv_filename = self.database_parser.database_to_csv(db_json, col_name_list)
        # TODO 将Md文件写入到数据库;调用SQL中的notion2sql提供的接口
        return

    # 源文件，直接输出成json; 辅助测试使用
    def page_to_json(self, json_name=None):
        page_json = self.query_page()
        if page_json is None:
            return None

        if json_name is None:
            json_name = self.tmp_dir + self.page_id + ".json"
        common_op.save_json_to_file(page_json, json_name)
        return
