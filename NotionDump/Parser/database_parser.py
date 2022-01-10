# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com

import csv
import os
import logging
from notion_client import Client, AsyncClient

import NotionDump
from NotionDump.Parser.block_parser import BlockParser


class DatabaseParser:
    def __init__(self, database_id, token=None, client_handle=None, async_api=False):
        self.database_id = database_id.replace('-', '')
        self.token = token
        if client_handle is None and token is not None:
            # 有的token话就初始化一下
            if not async_api:
                self.client = Client(auth=self.token)
            else:
                self.client = AsyncClient(auth=self.token)
        else:
            # 没有token，传进来handle就用，没传就不用
            self.client = client_handle

        self.tmp_dir = NotionDump.TMP_DIR
        if not os.path.exists(self.tmp_dir):
            os.mkdir(self.tmp_dir)

        # 这里虽然传入了但是也不会用到
        self.block_parser = BlockParser(
            block_id=self.database_id,
            token=self.token,
            client_handle=self.client
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
            logging.exception("col name no title error! id=" + self.database_id)
            return ""
        col_name_list.append(title_name)  # 把title_name放在最后一个，逆序之后就是第一个
        # 根据现有的数据库看来这里需要逆序一下才和实际的数据库一致
        col_name_list.reverse()
        return col_name_list

    # 格式化存储，这里是临时文件存在方式（在外面转成数据库，或者最终输出CSV的格式）
    def database_to_csv(self, database_handle, col_name_list=None):
        page_list = database_handle.get("results")
        # 数据库是空的，直接返回完事
        if len(page_list) == 0:
            return

        # col_name_list 是想要的列，并且会按照该顺序输出；如果没有给定则获取所有列
        if col_name_list is None:
            # 如果没有给定输出顺序，则获取到page中的所有列（注意不保证是显示的顺序！！！！）
            col_name_list = self.__get_col_name_list(page_list[0])

        # 创建CSV文件
        tmp_csv_filename = self.tmp_dir + self.database_id + ".csv"
        file = open(tmp_csv_filename, "w", encoding="utf-8", newline='')
        csv_writer = csv.writer(file)
        # 首先将列的名称写入到CSV文件中
        csv_writer.writerow(col_name_list)

        # 返回的内容好像是倒序的，先倒置过来吧
        page_list.reverse()
        # 解析每一个page的内容
        for page in page_list:
            page_iter = []
            for item in col_name_list:
                # 解析每一个方格的内容
                if page["properties"][item]["type"] == "title":  # title
                    page_iter.append(self.block_parser.title_parser(page["properties"][item]))
                elif page["properties"][item]["type"] == "multi_select":  # multi_select
                    page_iter.append(self.block_parser.multi_select_parser(page["properties"][item]))
                elif page["properties"][item]["type"] == "select":
                    page_iter.append(self.block_parser.select_parser(page["properties"][item]))
                elif page["properties"][item]["type"] == "rich_text":
                    page_iter.append(self.block_parser.rich_text_parser(page["properties"][item]))
                elif page["properties"][item]["type"] == "url":
                    page_iter.append(self.block_parser.url_parser(page["properties"][item]))
                elif page["properties"][item]["type"] == "email":
                    page_iter.append(self.block_parser.email_parser(page["properties"][item]))
                elif page["properties"][item]["type"] == "checkbox":
                    page_iter.append(self.block_parser.checkbox_parser(page["properties"][item]))
                elif page["properties"][item]["type"] == "phone_number":
                    page_iter.append(self.block_parser.phone_number_parser(page["properties"][item]))
                elif page["properties"][item]["type"] == "date":
                    page_iter.append(self.block_parser.date_parser(page["properties"][item]))
                elif page["properties"][item]["type"] == "people":
                    page_iter.append(self.block_parser.people_parser(page["properties"][item]))
                elif page["properties"][item]["type"] == "number":
                    page_iter.append(self.block_parser.number_parser(page["properties"][item]))
                elif page["properties"][item]["type"] == "files":
                    page_iter.append(self.block_parser.files_parser(page["properties"][item]))
                else:
                    logging.exception("unknown properties type:" + page["properties"][item]["type"])

            # 将内容填充到CSV中
            csv_writer.writerow(page_iter)
            # print("write success")

        file.flush()
        file.close()
        # 将临时文件地址转出去，由外面进行进一步的操作
        return tmp_csv_filename
